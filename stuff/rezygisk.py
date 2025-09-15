import os
import shutil
from stuff.general import General
from tools.helper import bcolors, get_download_dir, print_color

class ReZygisk(General):
    download_loc = get_download_dir()
    dl_link = "https://github.com/PerformanC/ReZygisk/releases/download/v1.0.0-rc.3/ReZygisk-v1.0.0-rc.3.zip"
    dl_file_name = os.path.join(download_loc, "rezygisk.zip")
    act_md5 = ""  # Will be set after first download
    extract_to = "/tmp/rezygisk_unpack"
    copy_dir = "./rezygisk"

    def download(self):
        print_color("Downloading ReZygisk v1.0.0-rc.3 .....", bcolors.GREEN)
        super().download()

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)

        # Create module directory structure
        module_dir = os.path.join(self.copy_dir, "data", "adb", "modules", "ReZygisk")
        os.makedirs(module_dir, exist_ok=True)

        print_color("Installing ReZygisk module...", bcolors.GREEN)

        # Copy extracted module files
        if os.path.exists(self.extract_to):
            for item in os.listdir(self.extract_to):
                src_path = os.path.join(self.extract_to, item)
                dst_path = os.path.join(module_dir, item)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_path, dst_path)

        # Create enable file for auto-mounting
        with open(os.path.join(module_dir, "auto_mount"), "w") as f:
            f.write("")

        print_color("ReZygisk module installed successfully", bcolors.GREEN)