import gzip
import os
import shutil
import re
import zipfile
from stuff.general import General
from tools.helper import bcolors, download_file, host, print_color, run, get_download_dir

class MagiskEnhanced(General):
    download_loc = get_download_dir()

    # Updated links for latest versions - ARM64 compatible
    dl_links = {
        "magisk": {
            "url": "https://github.com/topjohnwu/Magisk/releases/download/v30.2/Magisk-v30.2.apk",
            "md5": ""  # Skip MD5 check for now
        },
        "rezygisk": {
            "url": "https://github.com/PerformanC/ReZygisk/releases/download/v1.0.0-rc.3/ReZygisk-v1.0.0-rc.3.zip",
            "md5": ""
        },
        "playintegrity": {
            "url": "https://github.com/KOWX712/PlayIntegrityFix/releases/download/v4.3-inject-s/PlayIntegrityFix_v4.3-inject-s.zip",
            "md5": ""
        },
        "trickystore": {
            "url": "https://github.com/5ec1cff/TrickyStore/releases/download/1.3.0/TrickyStore-v1.3.0-release.zip",
            "md5": ""
        },
        "tricky_addon": {
            "url": "https://github.com/KOWX712/Tricky-Addon-Update-Target-List/releases/download/v4.1/Tricky-Addon-Update-Target-List-v4.1.zip",
            "md5": ""
        },
        "ksu_webui": {
            "url": "https://github.com/5ec1cff/KsuWebUIStandalone/releases/download/v1.0/KsuWebUIStandalone-v1.0.zip",
            "md5": ""
        }
    }

    dl_file_name = os.path.join(download_loc, "magisk_enhanced.apk")
    modules_dir = os.path.join(download_loc, "modules")
    act_md5 = ""  # Will be set dynamically
    extract_to = "/tmp/magisk_enhanced_unpack"
    copy_dir = "./magisk_enhanced"
    magisk_dir = os.path.join(copy_dir, "system", "etc", "init", "magisk")
    modules_install_dir = os.path.join(copy_dir, "data", "adb", "modules")
    machine = host()

    original_bootanim = """
service bootanim /system/bin/bootanimation
    class core animation
    user graphics
    group graphics audio
    disabled
    oneshot
    ioprio rt 0
    task_profiles MaxPerformance

"""

    bootanim_component = """
on post-fs-data
    start logd
    exec u:r:su:s0 root root -- {MAGISKSYSTEMDIR}/magiskpolicy --live --magisk
    exec u:r:magisk:s0 root root -- {MAGISKSYSTEMDIR}/magiskpolicy --live --magisk
    exec u:r:update_engine:s0 root root -- {MAGISKSYSTEMDIR}/magiskpolicy --live --magisk
    exec u:r:su:s0 root root -- {MAGISKSYSTEMDIR}/{magisk_name} --auto-selinux --setup-sbin {MAGISKSYSTEMDIR} {MAGISKTMP}
    exec u:r:su:s0 root root -- {MAGISKTMP}/magisk --auto-selinux --post-fs-data

on nonencrypted
    exec u:r:su:s0 root root -- {MAGISKTMP}/magisk --auto-selinux --service

on property:vold.decrypt=trigger_restart_framework
    exec u:r:su:s0 root root -- {MAGISKTMP}/magisk --auto-selinux --service

on property:sys.boot_completed=1
    mkdir /data/adb/magisk 755
    mkdir /data/adb/modules 755
    exec u:r:su:s0 root root -- {MAGISKTMP}/magisk --auto-selinux --boot-complete
    exec -- /system/bin/sh -c "if [ ! -e /data/data/com.topjohnwu.magisk ] ; then pm install /system/etc/init/magisk/magisk.apk ; fi"
    exec -- /system/bin/sh -c "if [ -d /data/adb/modules ] ; then /system/etc/init/magisk/install_modules.sh ; fi"

on property:init.svc.zygote=restarting
    exec u:r:su:s0 root root -- {MAGISKTMP}/magisk --auto-selinux --zygote-restart

on property:init.svc.zygote=stopped
    exec u:r:su:s0 root root -- {MAGISKTMP}/magisk --auto-selinux --zygote-restart
    """.format(MAGISKSYSTEMDIR="/system/etc/init/magisk", MAGISKTMP="/sbin", magisk_name="magisk")

    module_install_script = """#!/system/bin/sh
# Magisk Enhanced Modules Auto-Installer

MODULES_DIR="/data/adb/modules"
MAGISK_DIR="/system/etc/init/magisk"

# Function to install a module
install_module() {
    local module_name=$1
    local module_path="$MAGISK_DIR/modules/$module_name"
    local install_path="$MODULES_DIR/$module_name"

    if [ -f "$module_path" ]; then
        echo "Installing module: $module_name"
        mkdir -p "$install_path"
        cd "$install_path"
        unzip -o "$module_path"

        # Set proper permissions
        if [ -f "service.sh" ]; then
            chmod 755 "service.sh"
        fi
        if [ -f "post-fs-data.sh" ]; then
            chmod 755 "post-fs-data.sh"
        fi
        if [ -f "uninstall.sh" ]; then
            chmod 755 "uninstall.sh"
        fi

        # Create enable file
        touch "$install_path/auto_mount"

        echo "Module $module_name installed successfully"
    else
        echo "Module $module_name not found at $module_path"
    fi
}

# Install all available modules
install_module "ReZygisk"
install_module "PlayIntegrityFix"
install_module "TrickyStore"
install_module "TrickyAddonUpdateTargetList"
install_module "KsuWebUIStandalone"

echo "All modules installation completed"
"""

    def __init__(self):
        super().__init__()
        self.dl_link = self.dl_links["magisk"]["url"]
        self.act_md5 = self.dl_links["magisk"]["md5"]

    def download(self):
        print_color("Downloading Magisk Enhanced (v30.2) and modules .....", bcolors.GREEN)

        # Create modules directory
        if not os.path.exists(self.modules_dir):
            os.makedirs(self.modules_dir)

        # Download Magisk
        super().download()

        # Download all modules
        for module_name, module_info in self.dl_links.items():
            if module_name != "magisk":
                module_file = os.path.join(self.modules_dir, f"{module_name}.zip")
                print_color(f"Downloading {module_name}...", bcolors.GREEN)
                download_file(module_info["url"], module_file)

    def extract(self):
        print_color("Extracting Magisk APK...", bcolors.GREEN)
        print(self.dl_file_name)
        print(self.extract_to)
        
        # Create extract directory
        if not os.path.exists(self.extract_to):
            os.makedirs(self.extract_to)
        
        # Extract APK (which is actually a ZIP file)
        with zipfile.ZipFile(self.dl_file_name) as z:
            z.extractall(self.extract_to)

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)
        if not os.path.exists(self.magisk_dir):
            os.makedirs(self.magisk_dir, exist_ok=True)
        if not os.path.exists(self.modules_install_dir):
            os.makedirs(self.modules_install_dir, exist_ok=True)

        if not os.path.exists(os.path.join(self.copy_dir, "sbin")):
            os.makedirs(os.path.join(self.copy_dir, "sbin"), exist_ok=True)

        print_color("Copying Magisk Enhanced libs now ...", bcolors.GREEN)

        arch_map = {
            "x86": "x86",
            "x86_64": "x86_64",
            "arm": "armeabi-v7a",
            "arm64": "arm64-v8a"
        }

        lib_dir = os.path.join(self.extract_to, "lib", arch_map[self.machine[0]])
        for parent, dirnames, filenames in os.walk(lib_dir):
            for filename in filenames:
                o_path = os.path.join(lib_dir, filename)
                filename_match = re.search(r'lib(.*)\.so', filename)
                if filename_match:
                    n_path = os.path.join(self.magisk_dir, filename_match.group(1))
                    shutil.copyfile(o_path, n_path)
                    run(["chmod", "+x", n_path])

        # Copy Magisk APK
        shutil.copyfile(self.dl_file_name, os.path.join(self.magisk_dir, "magisk.apk"))

        # Copy modules to magisk directory
        modules_magisk_dir = os.path.join(self.magisk_dir, "modules")
        if not os.path.exists(modules_magisk_dir):
            os.makedirs(modules_magisk_dir)

        for module_file in os.listdir(self.modules_dir):
            if module_file.endswith('.zip'):
                src_path = os.path.join(self.modules_dir, module_file)
                dst_path = os.path.join(modules_magisk_dir, module_file)
                shutil.copyfile(src_path, dst_path)

        # Create module installation script
        install_script_path = os.path.join(self.magisk_dir, "install_modules.sh")
        with open(install_script_path, "w") as script_file:
            script_file.write(self.module_install_script)
        os.chmod(install_script_path, 0o755)

        # Backup original bootanim.rc
        bootanim_path = os.path.join(self.copy_dir, "system", "etc", "init", "bootanim.rc")
        gz_filename = os.path.join(bootanim_path) + ".gz"

        if not os.path.exists(os.path.dirname(bootanim_path)):
            os.makedirs(os.path.dirname(bootanim_path))

        with gzip.open(gz_filename, 'wb') as f_gz:
            f_gz.write(self.original_bootanim.encode('utf-8'))

        with open(bootanim_path, "w") as initfile:
            initfile.write(self.original_bootanim + self.bootanim_component)

        os.chmod(bootanim_path, 0o644)

        print_color("Magisk Enhanced with modules copied successfully", bcolors.GREEN)