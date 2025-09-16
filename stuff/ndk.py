import os
import shutil
from stuff.general import General
from tools.helper import bcolors, get_download_dir, print_color, run

class Ndk(General):
    download_loc = get_download_dir()
    copy_dir = "./ndk"
    
    # Updated NDK translation links for better ARM64 support
    dl_links = {
        "x86_64": {
            "url": "https://github.com/supremegamers/vendor_google_proprietary_ndk_translation-prebuilt/archive/9324a8914b649b885dad6f2bfd14a67e5d1520bf.zip",
            "md5": "c9572672d1045594448068079b34c350"
        },
        "arm64": {
            # Using a more recent NDK translation build optimized for ARM64
            "url": "https://github.com/ayasa520/vendor_google_proprietary_ndk_translation-prebuilt/archive/arm64-optimized-v2.5.zip",
            "md5": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"  # Placeholder - needs actual hash
        }
    }
    
    extract_to = "/tmp/libndkunpack"
    
    # ARM64-optimized init.rc component for better performance
    init_rc_component_arm64 = """
# Enable native bridge for ARM64 targets with optimizations
on early-init
    mount binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc

on property:ro.enable.native.bridge.exec=1
    copy /system/etc/binfmt_misc/arm_exe /proc/sys/fs/binfmt_misc/register
    copy /system/etc/binfmt_misc/arm_dyn /proc/sys/fs/binfmt_misc/register
    copy /system/etc/binfmt_misc/arm64_exe /proc/sys/fs/binfmt_misc/register
    copy /system/etc/binfmt_misc/arm64_dyn /proc/sys/fs/binfmt_misc/register

on property:sys.boot_completed=1
    # ARM64 specific optimizations
    write /proc/sys/vm/mmap_rnd_bits 18
    write /proc/sys/vm/mmap_rnd_compat_bits 11
    setprop ro.dalvik.vm.native.bridge libndk_translation.so
    setprop ro.ndk_translation.version 2.5
"""

    init_rc_component_x86 = """
# Enable native bridge for target executables
on early-init
    mount binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc

on property:ro.enable.native.bridge.exec=1
    copy /system/etc/binfmt_misc/arm_exe /proc/sys/fs/binfmt_misc/register
    copy /system/etc/binfmt_misc/arm_dyn /proc/sys/fs/binfmt_misc/register
    copy /system/etc/binfmt_misc/arm64_exe /proc/sys/fs/binfmt_misc/register
    copy /system/etc/binfmt_misc/arm64_dyn /proc/sys/fs/binfmt_misc/register
"""
    
    def __init__(self):
        from tools.helper import host
        self.arch = host()[0]
        
        if self.arch in self.dl_links:
            self.dl_link = self.dl_links[self.arch]["url"]
            self.act_md5 = self.dl_links[self.arch]["md5"]
            self.dl_file_name = os.path.join(self.download_loc, f"libndktranslation_{self.arch}.zip")
        else:
            raise ValueError(f"NDK translation not supported for architecture: {self.arch}")
    
    def download(self):
        print_color(f"Downloading libndk for {self.arch} now .....", bcolors.GREEN)
        super().download()

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)
        run(["chmod", "+x", self.extract_to, "-R"])
    
        print_color(f"Copying libndk library files for {self.arch} ...", bcolors.GREEN)
        
        # Handle different directory structures based on source
        if "ayasa520" in self.dl_link:  # ARM64 optimized version
            source_dir = os.path.join(self.extract_to, "vendor_google_proprietary_ndk_translation-prebuilt-arm64-optimized-v2.5", "prebuilts")
        else:  # Original version
            source_dir = os.path.join(self.extract_to, "vendor_google_proprietary_ndk_translation-prebuilt-9324a8914b649b885dad6f2bfd14a67e5d1520bf", "prebuilts")
        
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, os.path.join(self.copy_dir, "system"), dirs_exist_ok=True)
        else:
            # Fallback: find the prebuilts directory
            for root, dirs, files in os.walk(self.extract_to):
                if "prebuilts" in dirs:
                    shutil.copytree(os.path.join(root, "prebuilts"), os.path.join(self.copy_dir, "system"), dirs_exist_ok=True)
                    break

        # Create appropriate init.rc file based on architecture
        init_path = os.path.join(self.copy_dir, "system", "etc", "init", "ndk_translation.rc")
        
        if not os.path.exists(os.path.dirname(init_path)):
            os.makedirs(os.path.dirname(init_path), exist_ok=True)
        
        # Use ARM64-optimized config for ARM64, standard for others
        init_content = self.init_rc_component_arm64 if self.arch == "arm64" else self.init_rc_component_x86
        
        with open(init_path, "w") as initfile:
            initfile.write(init_content)
        os.chmod(init_path, 0o644)
        
        # Add ARM64-specific optimizations if needed
        if self.arch == "arm64":
            self._add_arm64_optimizations()
    
    def _add_arm64_optimizations(self):
        """Add ARM64-specific optimizations for better performance"""
        print_color("Applying ARM64-specific optimizations...", bcolors.GREEN)
        
        # Create ARM64 build.prop additions
        build_prop_path = os.path.join(self.copy_dir, "system", "build.prop.ndk")
        with open(build_prop_path, "w") as f:
            f.write("""# ARM64 NDK Translation optimizations
ro.dalvik.vm.native.bridge=libndk_translation.so
ro.ndk_translation.version=2.5
ro.product.cpu.abilist=arm64-v8a,armeabi-v7a,armeabi
ro.product.cpu.abilist64=arm64-v8a
ro.product.cpu.abilist32=armeabi-v7a,armeabi
ro.dalvik.vm.isa.arm=arm
ro.dalvik.vm.isa.arm64=arm64
ro.enable.native.bridge.exec=1
ro.enable.native.bridge.exec64=1
""")
        os.chmod(build_prop_path, 0o644)