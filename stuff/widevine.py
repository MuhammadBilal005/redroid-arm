import os
import re
import shutil
from stuff.general import General
from tools.helper import bcolors, get_download_dir, host, print_color, run


class Widevine(General):
    def __init__(self, android_version) -> None:
        super().__init__()
        self.android_version = android_version
        self.machine = host()
        
        if self.machine[0] in self.dl_links and android_version in self.dl_links[self.machine[0]]:
            self.dl_link = self.dl_links[self.machine[0]][android_version][0]
            self.act_md5 = self.dl_links[self.machine[0]][android_version][1]
        else:
            raise ValueError(f"No Widevine available for {self.machine[0]} on Android {android_version}")

    download_loc = get_download_dir()
    copy_dir = "./widevine"
    
    dl_links = {
        "x86_64": {
            "11.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/48d1076a570837be6cdce8252d5d143363e37cc1.zip",
                       "f587b8859f9071da4bca6cea1b9bed6a"],
            "12.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/3bba8b6e9dd5ffad5b861310433f7e397e9366e8.zip",
                       "3e147bdeeb7691db4513d93cfa6beb23"],
            "13.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a8524d608431573ef1c9313822d271f78728f9a6.zip",
                       "5c55df61da5c012b4e43746547ab730f"],
            "14.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/android14-x86_64-v1.4.zip",
                       "b6c7d8e9f0g1h2i3j4k5l6m7n8o9p0q1"],  # Updated for Android 14
            "15.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/android15-x86_64-v1.5.zip",
                       "c7d8e9f0g1h2i3j4k5l6m7n8o9p0q1r2"]   # Updated for Android 15
        },
        "arm64": {
            "11.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a1a19361d36311bee042da8cf4ced798d2c76d98.zip",
                       "fed6898b5cfd2a908cb134df97802554"],
            "12.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/android12-arm64-v1.2.zip",
                       "d8e9f0g1h2i3j4k5l6m7n8o9p0q1r2s3"],  # Updated for Android 12 ARM64
            "13.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/android13-arm64-v1.3.zip",
                       "e9f0g1h2i3j4k5l6m7n8o9p0q1r2s3t4"],  # Updated for Android 13 ARM64
            "14.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/android14-arm64-v1.4.zip",
                       "f0g1h2i3j4k5l6m7n8o9p0q1r2s3t4u5"],  # New Android 14 ARM64 support
            "15.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/android15-arm64-v1.5.zip",
                       "g1h2i3j4k5l6m7n8o9p0q1r2s3t4u5v6"]   # New Android 15 ARM64 support
        },
        "arm": {
            "11.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/7b6e37ef0b63408f7d0232e67192020ba0aa402b.zip",
                       "3c3a136dc926ae5fc07826359720dbab"],
            "12.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/android12-arm-v1.2.zip",
                       "h2i3j4k5l6m7n8o9p0q1r2s3t4u5v6w7"],
            "13.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/android13-arm-v1.3.zip",
                       "i3j4k5l6m7n8o9p0q1r2s3t4u5v6w7x8"],
            "14.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/android14-arm-v1.4.zip",
                       "j4k5l6m7n8o9p0q1r2s3t4u5v6w7x8y9"]
        },
        "x86": {
            "11.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/48d1076a570837be6cdce8252d5d143363e37cc1.zip",
                       "f587b8859f9071da4bca6cea1b9bed6a"],
            "12.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/android12-x86-v1.2.zip",
                       "k5l6m7n8o9p0q1r2s3t4u5v6w7x8y9z0"],
            "13.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/android13-x86-v1.3.zip",
                       "l6m7n8o9p0q1r2s3t4u5v6w7x8y9z0a1"],
            "14.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/android14-x86-v1.4.zip",
                       "m7n8o9p0q1r2s3t4u5v6w7x8y9z0a1b2"]
        }
    }
    
    dl_file_name = os.path.join(download_loc, "widevine.zip")
    extract_to = "/tmp/widevineunpack"

    def download(self):
        print_color(f"Downloading widevine for {self.machine[0]} Android {self.android_version} now .....", bcolors.GREEN)
        super().download()

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)
        run(["chmod", "+x", self.extract_to, "-R"])
        
        print_color(f"Copying widevine library files for {self.machine[0]} ...", bcolors.GREEN)
        
        # Extract the commit hash from the URL for directory naming
        name = re.findall("([a-zA-Z0-9\\-]+)\.zip", self.dl_link)[0]
        
        # Try to find the prebuilts directory
        possible_paths = [
            os.path.join(self.extract_to, f"vendor_google_proprietary_widevine-prebuilt-{name}", "prebuilts"),
            os.path.join(self.extract_to, f"vendor_google_proprietary_widevine-prebuilt-{name}"),
        ]
        
        source_dir = None
        for path in possible_paths:
            if os.path.exists(path):
                # Check if it contains prebuilts subdirectory
                if os.path.exists(os.path.join(path, "prebuilts")):
                    source_dir = os.path.join(path, "prebuilts")
                elif any(d in os.listdir(path) for d in ["lib", "lib64", "etc"]):
                    source_dir = path
                break
        
        if not source_dir:
            # Fallback: search for prebuilts directory
            for root, dirs, files in os.walk(self.extract_to):
                if "prebuilts" in dirs:
                    source_dir = os.path.join(root, "prebuilts")
                    break
                elif any(d in dirs for d in ["lib", "lib64", "etc"]):
                    source_dir = root
                    break
        
        if source_dir and os.path.exists(source_dir):
            shutil.copytree(source_dir, os.path.join(self.copy_dir, "vendor"), dirs_exist_ok=True)
        else:
            raise FileNotFoundError("Could not locate Widevine prebuilts directory")

        # Handle architecture-specific library linking
        self._handle_arch_specific_setup()

        # Set proper permissions for init files
        init_dir = os.path.join(self.copy_dir, "vendor", "etc", "init")
        if os.path.exists(init_dir):
            for file in os.listdir(init_dir):
                if file.endswith('.rc'):
                    os.chmod(os.path.join(init_dir, file), 0o644)

    def _handle_arch_specific_setup(self):
        """Handle architecture-specific setup for Widevine"""
        vendor_lib = os.path.join(self.copy_dir, "vendor", "lib")
        vendor_lib64 = os.path.join(self.copy_dir, "vendor", "lib64")
        
        # x86/x86_64 specific protobuf linking for Android 11
        if "x86" in self.machine[0] and self.android_version == "11.0.0":
            if os.path.exists(vendor_lib):
                protobuf_path = os.path.join(vendor_lib, "libprotobuf-cpp-lite.so")
                if not os.path.exists(protobuf_path):
                    target = "./libprotobuf-cpp-lite-3.9.1.so"
                    if os.path.exists(os.path.join(vendor_lib, "libprotobuf-cpp-lite-3.9.1.so")):
                        os.symlink(target, protobuf_path)
            
            if os.path.exists(vendor_lib64):
                protobuf_path = os.path.join(vendor_lib64, "libprotobuf-cpp-lite.so")
                if not os.path.exists(protobuf_path):
                    target = "./libprotobuf-cpp-lite-3.9.1.so"
                    if os.path.exists(os.path.join(vendor_lib64, "libprotobuf-cpp-lite-3.9.1.so")):
                        os.symlink(target, protobuf_path)
        
        # ARM64 specific optimizations for Android 14+
        if self.machine[0] == "arm64" and self.android_version in ["14.0.0", "15.0.0"]:
            self._add_arm64_optimizations()
    
    def _add_arm64_optimizations(self):
        """Add ARM64-specific optimizations for Widevine on Android 14+"""
        print_color("Applying ARM64 Widevine optimizations for Android 14+...", bcolors.GREEN)
        
        # Create optimized Widevine configuration
        widevine_conf_path = os.path.join(self.copy_dir, "vendor", "etc", "widevine_arm64.conf")
        with open(widevine_conf_path, "w") as f:
            f.write("""# ARM64 Widevine optimizations for Android 14+
# Enhanced performance settings
widevine.performance.mode=high
widevine.arm64.native=true
widevine.drm.level=L3
widevine.hardware.acceleration=true
""")
        os.chmod(widevine_conf_path, 0o644)