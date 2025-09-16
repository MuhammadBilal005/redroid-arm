import os
import shutil
from stuff.general import General
from tools.helper import bcolors, get_download_dir, print_color, run

class Ndk(General):
    download_loc = get_download_dir()
    copy_dir = "./ndk"
    
    # Using the original working NDK translation link for all architectures
    # The original NDK translation works on ARM64 hosts as well as x86
    dl_link = "https://github.com/supremegamers/vendor_google_proprietary_ndk_translation-prebuilt/archive/9324a8914b649b885dad6f2bfd14a67e5d1520bf.zip"
    dl_file_name = os.path.join(download_loc, "libndktranslation.zip")
    extract_to = "/tmp/libndkunpack"
    act_md5 = "c9572672d1045594448068079b34c350"
    
    def download(self):
        print_color("Downloading libndk now .....", bcolors.GREEN)
        super().download()

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)
        run(["chmod", "+x", self.extract_to, "-R"])
    
        print_color("Copying libndk library files ...", bcolors.GREEN)
        shutil.copytree(
            os.path.join(
                self.extract_to, 
                "vendor_google_proprietary_ndk_translation-prebuilt-9324a8914b649b885dad6f2bfd14a67e5d1520bf", 
                "prebuilts"
            ), 
            os.path.join(self.copy_dir, "system"), 
            dirs_exist_ok=True
        )

        init_path = os.path.join(self.copy_dir, "system", "etc", "init", "ndk_translation.rc")
        if os.path.exists(init_path):
            os.chmod(init_path, 0o644)