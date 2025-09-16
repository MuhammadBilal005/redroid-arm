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
    
    # Using known working Widevine download links
    dl_links = {
        "x86_64": {
            "11.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/48d1076a570837be6cdce8252d5d143363e37cc1.zip",
                       "f587b8859f9071da4bca6cea1b9bed6a"],
            "12.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/3bba8b6e9dd5ffad5b861310433f7e397e9366e8.zip",
                       "3e147bdeeb7691db4513d93cfa6beb23"],
            "13.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a8524d608431573ef1c9313822d271f78728f9a6.zip",
                       "5c55df61da5c012b4e43746547ab730f"],
            # For Android 14, we'll use the Android 13 version as fallback
            "14.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a8524d608431573ef1c9313822d271f78728f9a6.zip",
                       "5c55df61da5c012b4e43746547ab730f"]
        },
        "arm64": {
            "11.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a1a19361d36311bee042da8cf4ced798d2c76d98.zip",
                       "fed6898b5cfd2a908cb134df97802554"],
            # For other versions, we'll use the 11.0.0 version as it's the most stable for ARM64
            "12.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a1a19361d36311bee042da8cf4ced798d2c76d98.zip",
                       "fed6898b5cfd2a908cb134df97802554"],
            "13.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a1a19361d36311bee042da8cf4ced798d2c76d98.zip",
                       "fed6898b5cfd2a908cb134df97802554"],
            "14.0.0": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a1a19361d36311bee042da8cf4ced798d2c76d98.zip",
                       "fed6898b5cfd2a908cb134df97802554"]
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
        
        # Fixed regex pattern to avoid SyntaxWarning
        name = re.findall(r"([a-zA-Z0-9\-]+)\.zip", self.dl_link)[0]
        
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

        # Handle architecture-specific library linking for Android 11 x86
        if "x86" in self.machine[0] and self.android_version == "11.0.0":
            vendor_lib = os.path.join(self.copy_dir, "vendor", "lib")
            vendor_lib64 = os.path.join(self.copy_dir, "vendor", "lib64")
            
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

        # Set proper permissions for init files
        init_dir = os.path.join(self.copy_dir, "vendor", "etc", "init")
        if os.path.exists(init_dir):
            for file in os.listdir(init_dir):
                if file.endswith('.rc'):
                    os.chmod(os.path.join(init_dir, file), 0o644)