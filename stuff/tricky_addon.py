import os
import shutil
from stuff.general import General
from tools.helper import bcolors, get_download_dir, print_color

class TrickyAddon(General):
    download_loc = get_download_dir()
    dl_link = "https://github.com/KOWX712/Tricky-Addon-Update-Target-List/releases/download/v4.1/Tricky-Addon-Update-Target-List-v4.1.zip"
    dl_file_name = os.path.join(download_loc, "tricky_addon.zip")
    act_md5 = ""  # Will be set after first download
    extract_to = "/tmp/tricky_addon_unpack"
    copy_dir = "./tricky_addon"

    def download(self):
        print_color("Downloading Tricky-Addon-Update-Target-List v4.1 .....", bcolors.GREEN)
        super().download()

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)

        # Create module directory structure
        module_dir = os.path.join(self.copy_dir, "data", "adb", "modules", "TrickyAddonUpdateTargetList")
        os.makedirs(module_dir, exist_ok=True)

        print_color("Installing Tricky-Addon-Update-Target-List module...", bcolors.GREEN)

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

        print_color("Tricky-Addon-Update-Target-List module installed successfully", bcolors.GREEN)