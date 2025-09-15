import os
import platform
import subprocess
import requests
from tqdm import tqdm
import hashlib
import time
from tools.logger import get_logger

# Enhanced helper functions with logging
logger = get_logger()

def get_download_dir():
    download_loc = ""
    if os.environ.get("XDG_CACHE_HOME", None) is None:
        download_loc = os.path.join('/', "home", os.environ.get("SUDO_USER", os.environ.get("USER", "unknown")), ".cache", "redroid", "downloads")
    else:
        download_loc = os.path.join(os.environ["XDG_CACHE_HOME"], "redroid", "downloads")
    if not os.path.exists(download_loc):
        os.makedirs(download_loc)
        logger.info(f"Created download directory: {download_loc}")
    return download_loc

def run(args):
    """Enhanced run function with logging"""
    logger.debug(f"Executing command: {' '.join(args) if isinstance(args, list) else args}")

    start_time = time.time()
    try:
        result = subprocess.run(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        execution_time = time.time() - start_time

        logger.log_command_execution(args, result.returncode, result.stdout, result.stderr)

        if result.stderr and result.returncode != 0:
            logger.error(f"Command failed in {execution_time:.2f}s: {result.stderr}")
            raise subprocess.CalledProcessError(
                returncode=result.returncode,
                cmd=result.args,
                stderr=result.stderr,
                stdout=result.stdout
            )
        else:
            logger.debug(f"Command completed successfully in {execution_time:.2f}s")

        return result
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Command execution failed after {execution_time:.2f}s: {e}")
        raise

def download_file(url, f_name):
    """Enhanced download function with detailed logging"""
    logger.log_download_start(url, f_name)

    md5 = ""
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            logger.debug(f"Download attempt {attempt + 1}/{max_retries}")

            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 8192  # Increased block size for better performance

            logger.debug(f"Starting download: {total_size_in_bytes} bytes")

            progress_bar = tqdm(
                total=total_size_in_bytes,
                unit='B',
                unit_scale=True,
                desc=f"Downloading {os.path.basename(f_name)}"
            )

            downloaded = 0
            last_log_time = time.time()

            with open(f_name, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
                    downloaded += len(data)

                    # Log progress every 10 seconds
                    current_time = time.time()
                    if current_time - last_log_time > 10:
                        logger.log_download_progress(f_name, downloaded, total_size_in_bytes)
                        last_log_time = current_time

            progress_bar.close()

            # Calculate MD5
            with open(f_name, "rb") as f:
                file_bytes = f.read()
                md5 = hashlib.md5(file_bytes).hexdigest()

            file_size = os.path.getsize(f_name)
            logger.log_download_complete(f_name, file_size, md5)

            if total_size_in_bytes != 0 and downloaded != total_size_in_bytes:
                raise ValueError(f"Download incomplete: {downloaded}/{total_size_in_bytes} bytes")

            return md5

        except Exception as e:
            logger.error(f"Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error(f"Download failed after {max_retries} attempts")
                raise

def host():
    """Enhanced host detection with logging"""
    machine = platform.machine()
    logger.debug(f"Detected machine architecture: {machine}")

    mapping = {
        "i686": ("x86", 32),
        "x86_64": ("x86_64", 64),
        "aarch64": ("arm64", 64),
        "armv7l": ("arm", 32),
        "armv8l": ("arm", 32)
    }

    if machine in mapping:
        result = mapping[machine]
        logger.info(f"Using architecture: {result[0]} ({result[1]}-bit)")
        return result

    error_msg = f"Unsupported architecture: {machine}"
    logger.error(error_msg)
    raise ValueError(error_msg)

def verify_file_integrity(file_path, expected_md5=None, expected_size=None):
    """Verify file integrity with optional MD5 and size checks"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False

    file_size = os.path.getsize(file_path)
    logger.debug(f"File size: {file_size} bytes")

    if expected_size and file_size != expected_size:
        logger.error(f"File size mismatch: expected {expected_size}, got {file_size}")
        return False

    if expected_md5:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            actual_md5 = hashlib.md5(file_bytes).hexdigest()

        if actual_md5 != expected_md5:
            logger.error(f"MD5 mismatch: expected {expected_md5}, got {actual_md5}")
            return False
        else:
            logger.debug(f"MD5 verification passed: {actual_md5}")

    logger.debug(f"File integrity verified: {file_path}")
    return True

def check_disk_space(path, required_gb=5):
    """Check if sufficient disk space is available"""
    try:
        statvfs = os.statvfs(path)
        free_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024 ** 3)

        logger.debug(f"Available disk space: {free_gb:.2f} GB")

        if free_gb < required_gb:
            logger.warning(f"Low disk space: {free_gb:.2f} GB available, {required_gb} GB recommended")
            return False

        return True
    except Exception as e:
        logger.error(f"Failed to check disk space: {e}")
        return True  # Assume OK if check fails

def check_dependencies():
    """Check if required system dependencies are available"""
    dependencies = {
        'docker': 'Docker container runtime',
        'tar': 'Archive extraction tool',
        'lzip': 'LZIP compression tool',
        'unzip': 'ZIP extraction tool'
    }

    missing = []
    for dep, description in dependencies.items():
        try:
            result = subprocess.run(['which', dep], capture_output=True, text=True)
            if result.returncode == 0:
                logger.debug(f"✓ {dep} found: {result.stdout.strip()}")
            else:
                missing.append((dep, description))
                logger.error(f"✗ {dep} not found")
        except Exception as e:
            missing.append((dep, description))
            logger.error(f"✗ Failed to check {dep}: {e}")

    if missing:
        logger.error("Missing dependencies:")
        for dep, description in missing:
            logger.error(f"  - {dep}: {description}")
        return False

    logger.info("All dependencies satisfied")
    return True

# Keep original color functions for backward compatibility
class bcolors:
    RED = '\033[31m'
    YELLOW = '\033[33m'
    GREEN = '\033[32m'
    ENDC = '\033[0m'

def print_color(str, color):
    print(color + str + bcolors.ENDC)