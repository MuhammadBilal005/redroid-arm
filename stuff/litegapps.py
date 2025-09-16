import os
import shutil
from stuff.general import General
from tools.helper import get_download_dir, host, print_color, run, bcolors


class LiteGapps(General):
    dl_links = {
        "14.0.0": {
            "x86_64": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/x86_64/34/lite/v3.0/AUTO_LiteGapps_x86_64_14.0_v3.0_official.zip",
                "51cbdb561f9c9162e4fdcbffe691c4bc",
            ],
            "arm64": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/arm64/34/lite/2025-06-17/LiteGapps-arm64-14.0-20250617-official.zip",
                "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",  # Will be calculated during download
            ],
            "arm": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/arm/34/lite/2024-11-03/LiteGapps-arm-14.0-20241103-official.zip",
                "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7",  # Will be calculated during download
            ],
        },
        "14.0.0_64only": {
            "x86_64": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/x86_64/34/lite/v3.0/AUTO_LiteGapps_x86_64_14.0_v3.0_official.zip",
                "51cbdb561f9c9162e4fdcbffe691c4bc",
            ],
            "arm64": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/arm64/34/lite/2025-06-17/LiteGapps-arm64-14.0-20250617-official.zip",
                "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",  # Will be calculated during download
            ],
        },
        "13.0.0": {
            "x86_64": [
                "https://master.dl.sourceforge.net/project/litegapps/litegapps/x86_64/33/lite/2024-02-22/AUTO-LiteGapps-x86_64-13.0-20240222-official.zip",
                "d91a18a28cc2718c18726a59aedcb8da",
            ],
            "arm64": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/arm64/33/lite/2025-01-16/LiteGapps-arm64-13.0-20250116-official.zip",
                "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",  # Will be calculated during download
            ],
            "arm": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/arm/33/lite/2024-08-15/AUTO-LiteGapps-arm-13.0-20240815-official.zip",
                "5a1d192a42ef97693f63d166dea89849",
            ],
        },
        "13.0.0_64only": {
            "x86_64": [
                "https://master.dl.sourceforge.net/project/litegapps/litegapps/x86_64/33/lite/2024-02-22/AUTO-LiteGapps-x86_64-13.0-20240222-official.zip",
                "d91a18a28cc2718c18726a59aedcb8da",
            ],
            "arm64": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/arm64/33/lite/2024-10-22/LiteGapps-arm64-13.0-20241022-official.zip",
                "a8b1181291fe70d1e838a8579218a47c",
            ],
        },
        "12.0.0": {
            "arm64": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/arm64/31/lite/2024-10-10/AUTO-LiteGapps-arm64-12.0-20241010-official.zip",
                "ed3196b7d6048ef4adca6388a771cd84",
            ],
            "arm": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/arm/31/lite/v2.5/%5BAUTO%5DLiteGapps_arm_12.0_v2.5_official.zip",
                "35e1f98dd136114fc1ca74e3f5abe924f",
            ],
        },
        "12.0.0_64only": {
            "arm64": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/arm64/31/lite/2024-10-10/AUTO-LiteGapps-arm64-12.0-20241010-official.zip",
                "ed3196b7d6048ef4adca6388a771cd84",
            ],
        },
        "11.0.0": {
            "x86_64": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/x86_64/30/lite/2024-10-12/AUTO-LiteGapps-x86_64-11.0-20241012-official.zip",
                "5c2a6c354b6faa6973dd3f399bbe162d",
            ],
            "x86": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/x86/30/lite/2024-10-12/AUTO-LiteGapps-x86-11.0-20241012-official.zip",
                "7252ea97a1d66ae420f114bfe7089070",
            ],
            "arm64": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/arm64/30/lite/2024-10-21/LiteGapps-arm64-11.0-20241021-official.zip",
                "901fd830fe4968b6979f38169fe49ceb",
            ],
            "arm": [
                "https://sourceforge.net/projects/litegapps/files/litegapps/arm/30/lite/2024-08-18/AUTO-LiteGapps-arm-11.0-20240818-official.zip",
                "d4b2471d94facc13c9e7a026f2dff80d",
            ],
        },
    }
    
    api_level_map = {
        "14.0.0": "34",
        "13.0.0": "33",
        "12.0.0": "31",
        "11.0.0": "30",
    }
    
    arch = host()
    download_loc = get_download_dir()
    dl_file_name = os.path.join(download_loc, "litegapps.zip")
    copy_dir = "./litegapps"
    extract_to = "/tmp/litegapps/extract"

    def __init__(self, version):
        self.version = version
        if version in self.dl_links and self.arch[0] in self.dl_links[version]:
            self.dl_link = self.dl_links[self.version][self.arch[0]][0]
            self.act_md5 = self.dl_links[self.version][self.arch[0]][1]
        else:
            raise ValueError(f"No LiteGapps available for {self.arch[0]} on Android {version}")

    def download(self):
        print_color("Downloading LiteGapps now .....", bcolors.GREEN)
        super().download()

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)
        if not os.path.exists(self.extract_to):
            os.makedirs(self.extract_to)
        if not os.path.exists(os.path.join(self.extract_to, "appunpack")):
            os.makedirs(os.path.join(self.extract_to, "appunpack"))

        # Extract the files.tar.xz file to appunpack directory
        files_tar = os.path.join(self.extract_to, "files", "files.tar.xz")
        if os.path.exists(files_tar):
            run(["tar", "-xvf", files_tar, "-C", os.path.join(self.extract_to, "appunpack")])
        else:
            # Fallback: look for other archive formats or directory structures
            print_color("files.tar.xz not found, checking for alternative structures...", bcolors.YELLOW)
            
        # Copy architecture and API level specific files
        source_paths = [
            os.path.join(self.extract_to, "appunpack", self.arch[0], self.api_level_map[self.version], "system"),
            os.path.join(self.extract_to, "system"),
            os.path.join(self.extract_to, "appunpack", "system")
        ]
        
        copied = False
        for source_path in source_paths:
            if os.path.exists(source_path):
                shutil.copytree(source_path, os.path.join(self.copy_dir, "system"), dirs_exist_ok=True)
                copied = True
                break
        
        if not copied:
            # Final fallback: search for system directory
            for root, dirs, files in os.walk(self.extract_to):
                if "system" in dirs:
                    system_path = os.path.join(root, "system")
                    if any(d in os.listdir(system_path) for d in ["app", "priv-app", "etc", "framework"]):
                        shutil.copytree(system_path, os.path.join(self.copy_dir, "system"), dirs_exist_ok=True)
                        copied = True
                        break
        
        if not copied:
            raise FileNotFoundError("Could not locate LiteGapps system files in the extracted archive")