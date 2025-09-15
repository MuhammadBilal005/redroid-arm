import os
import shutil
from stuff.general import General
from tools.helper import bcolors, get_download_dir, print_color

class TrickyStore(General):
    download_loc = get_download_dir()
    dl_link = "https://github.com/5ec1cff/TrickyStore/releases/download/1.3.0/TrickyStore-v1.3.0-release.zip"
    dl_file_name = os.path.join(download_loc, "trickystore.zip")
    act_md5 = ""  # Will be set after first download
    extract_to = "/tmp/trickystore_unpack"
    copy_dir = "./trickystore"

    def download(self):
        print_color("Downloading TrickyStore v1.3.0 .....", bcolors.GREEN)
        super().download()

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)

        # Create module directory structure
        module_dir = os.path.join(self.copy_dir, "data", "adb", "modules", "TrickyStore")
        os.makedirs(module_dir, exist_ok=True)

        print_color("Installing TrickyStore module...", bcolors.GREEN)

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

        # Set executable permissions for scripts
        for script in ["service.sh", "post-fs-data.sh", "uninstall.sh"]:
            script_path = os.path.join(module_dir, script)
            if os.path.exists(script_path):
                os.chmod(script_path, 0o755)

        print_color("TrickyStore module installed successfully", bcolors.GREEN)