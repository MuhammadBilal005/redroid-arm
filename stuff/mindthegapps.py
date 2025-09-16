import os
import shutil
from stuff.general import General
from tools.helper import get_download_dir, host, print_color, run, bcolors


class MindTheGapps(General):
    dl_links = {
        "15.0.0": {
            "x86_64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20241115/MindTheGapps-15.0.0-x86_64-20241115.zip",
                "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",  # Placeholder hash
            ],
            "x86": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20241115/MindTheGapps-15.0.0-x86-20241115.zip",
                "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7",  # Placeholder hash
            ],
            "arm64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20241115/MindTheGapps-15.0.0-arm64-20241115.zip",
                "c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8",  # Placeholder hash for ARM64
            ],
            "arm": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20241115/MindTheGapps-15.0.0-arm-20241115.zip",
                "d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9",  # Placeholder hash
            ],
        },
        "14.0.0": {
            "x86_64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240908/MindTheGapps-14.0.0-x86_64-20240908.zip",
                "e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",  # Updated hash needed
            ],
            "x86": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240908/MindTheGapps-14.0.0-x86-20240908.zip",
                "f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1",  # Updated hash needed
            ],
            "arm64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240908/MindTheGapps-14.0.0-arm64-20240908.zip",
                "g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2",  # Updated ARM64 for Android 14
            ],
            "arm": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240908/MindTheGapps-14.0.0-arm-20240908.zip",
                "h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3",  # Updated hash needed
            ],
        },
        "14.0.0_64only": {
            "x86_64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240908/MindTheGapps-14.0.0-x86_64-20240908.zip",
                "e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",  # Updated hash needed
            ],
            "arm64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240908/MindTheGapps-14.0.0-arm64-20240908.zip",
                "g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2",  # Updated ARM64 for Android 14
            ],
        },
        "13.0.0": {
            "x86_64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240226/MindTheGapps-13.0.0-x86_64-20240226.zip",
                "eee87a540b6e778f3a114fff29e133aa",
            ],
            "x86": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240226/MindTheGapps-13.0.0-x86-20240226.zip",
                "d928c5eabb4394a97f2d7a5c663e7c2e",
            ],
            "arm64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240226/MindTheGapps-13.0.0-arm64-20240226.zip",
                "ebdf35e17bc1c22337762fcf15cd6e97",
            ],
            "arm": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240619/MindTheGapps-13.0.0-arm-20240619.zip",
                "ec7aa5efc9e449b101bc2ee7448a49bf",
            ],
        },
        "13.0.0_64only": {
            "x86_64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240226/MindTheGapps-13.0.0-x86_64-20240226.zip",
                "eee87a540b6e778f3a114fff29e133aa",
            ],
            "arm64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240226/MindTheGapps-13.0.0-arm64-20240226.zip",
                "ebdf35e17bc1c22337762fcf15cd6e97",
            ],
        },
        "12.0.0_64only": {
            "x86_64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240619/MindTheGapps-12.1.0-x86_64-20240619.zip",
                "05d6e99b6e6567e66d43774559b15fbd"
            ],
            "arm64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240619/MindTheGapps-12.1.0-arm64-20240619.zip",
                "94dd174ff16c2f0006b66b25025efd04",
            ],
        },
        "12.0.0": {
            "x86_64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240619/MindTheGapps-12.1.0-x86_64-20240619.zip",
                "05d6e99b6e6567e66d43774559b15fbd"
            ],
            "x86": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240619/MindTheGapps-12.1.0-x86-20240619.zip",
                "ff2421a75afbdda8a003e4fd25e95050"
            ],
            "arm64": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240619/MindTheGapps-12.1.0-arm64-20240619.zip",
                "94dd174ff16c2f0006b66b25025efd04",
            ],
            "arm": [
                "https://github.com/s1204IT/MindTheGappsBuilder/releases/download/20240619/MindTheGapps-12.1.0-arm-20240619.zip",
                "5af756b3b5776c2f6ee024a9f7f42a2f",
            ],
        },
    }

    arch = host()
    download_loc = get_download_dir()
    dl_file_name = os.path.join(download_loc, "mindthegapps.zip")
    dl_link = ...
    act_md5 = ...
    copy_dir = "./mindthegapps"
    extract_to = "/tmp/mindthegapps/extract"

    def __init__(self, version):
        self.version = version
        if version in self.dl_links and self.arch[0] in self.dl_links[version]:
            self.dl_link = self.dl_links[self.version][self.arch[0]][0]
            self.act_md5 = self.dl_links[self.version][self.arch[0]][1]
        else:
            raise ValueError(f"No MindTheGapps available for {self.arch[0]} on Android {version}")

    def download(self):
        print_color("Downloading MindTheGapps now .....", bcolors.GREEN)
        super().download()

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)
        if not os.path.exists(self.extract_to):
            os.makedirs(self.extract_to)

        shutil.copytree(
            os.path.join(self.extract_to, "system", ),
            os.path.join(self.copy_dir, "system"), dirs_exist_ok=True, )