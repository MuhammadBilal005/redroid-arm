import os
import platform
import subprocess
import requests
from tqdm import tqdm
import hashlib

def get_download_dir():
    download_loc = ""
    if os.environ.get("XDG_CACHE_HOME", None) is None:
        download_loc = os.path.join('/', "home", os.environ.get("SUDO_USER", os.environ["USER"]), ".cache", "redroid", "downloads")
    else:
        download_loc = os.path.join(os.environ["XDG_CACHE_HOME"], "redroid", "downloads")
    if not os.path.exists(download_loc):
        os.makedirs(download_loc)
    return download_loc

def run(args):
    result = subprocess.run(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stderr:
        print(result.stderr.decode("utf-8"))
        raise subprocess.CalledProcessError(
                    returncode = result.returncode,
                    cmd = result.args,
                    stderr = result.stderr
                )
    return result

def download_file(url, f_name):
    md5 = ""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print_color(f"Error downloading {url}: {e}", bcolors.RED)
        raise
    
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    
    try:
        with open(f_name, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        
        with open(f_name, "rb") as f:
            bytes = f.read()
            md5 = hashlib.md5(bytes).hexdigest()
            
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            raise ValueError("Something went wrong while downloading")
            
    except Exception as e:
        progress_bar.close()
        if os.path.exists(f_name):
            os.remove(f_name)
        raise e
        
    return md5

def host():
    machine = platform.machine()
    
    mapping = {
        "i686": ("x86", 32),
        "x86_64": ("x86_64", 64),
        "aarch64": ("arm64", 64),  # This is the key mapping for ARM64
        "armv7l": ("arm", 32),
        "armv8l": ("arm", 32),
        "arm64": ("arm64", 64),    # Alternative ARM64 detection
    }
    
    if machine in mapping:
        arch, bits = mapping[machine]
        
        # Additional ARM64 detection for various systems
        if arch == "arm64" or machine == "aarch64":
            # Verify ARM64 capability
            try:
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo = f.read()
                    if "aarch64" in cpuinfo or "arm64" in cpuinfo:
                        print_color(f"Detected ARM64 architecture: {machine}", bcolors.GREEN)
                        return ("arm64", 64)
            except:
                pass
        
        # x86_64 SSE4.2 check (keeping original logic)
        if arch == "x86_64":
            try:
                with open("/proc/cpuinfo") as f:
                    if "sse4_2" not in f.read():
                        print_color("x86_64 CPU does not support SSE4.2, falling back to x86...", bcolors.YELLOW)
                        return ("x86", 32)
            except:
                pass
                
        return mapping[machine]
    
    raise ValueError("platform.machine '" + machine + "'"
                     " architecture is not supported. Supported architectures: x86, x86_64, arm, arm64/aarch64")

def detect_container_runtime():
    """Detect available container runtime (docker or podman)"""
    for runtime in ["docker", "podman"]:
        try:
            result = subprocess.run([runtime, "--version"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                return runtime
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    return None

def verify_android_version_support(version, arch):
    """Verify if the Android version is supported for the given architecture"""
    supported_versions = {
        "arm64": ["11.0.0", "12.0.0", "12.0.0_64only", "13.0.0", "13.0.0_64only", "14.0.0", "14.0.0_64only", "15.0.0", "15.0.0_64only"],
        "x86_64": ["8.1.0", "9.0.0", "10.0.0", "11.0.0", "12.0.0", "12.0.0_64only", "13.0.0", "14.0.0", "15.0.0"],
        "x86": ["8.1.0", "9.0.0", "10.0.0", "11.0.0", "12.0.0", "13.0.0", "14.0.0", "15.0.0"],
        "arm": ["8.1.0", "9.0.0", "10.0.0", "11.0.0", "12.0.0", "13.0.0", "14.0.0"]
    }
    
    return version in supported_versions.get(arch, [])

class bcolors:
    RED = '\033[31m'
    YELLOW = '\033[33m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_color(str, color):
    print(color + str + bcolors.ENDC)

def print_banner():
    """Print a nice banner for the script"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                   ReDroid Script v2.0                   ║
║              Enhanced ARM64 & Android 14 Support        ║
╚══════════════════════════════════════════════════════════╝
    """
    print_color(banner, bcolors.CYAN)