#!/usr/bin/env python3

import argparse
import sys
import os
import traceback
import time
from pathlib import Path

from stuff.gapps import Gapps
from stuff.litegapps import LiteGapps
from stuff.magisk_enhanced import MagiskEnhanced
from stuff.rezygisk import ReZygisk
from stuff.playintegrity import PlayIntegrityFix
from stuff.trickystore import TrickyStore
from stuff.tricky_addon import TrickyAddon
from stuff.ksu_webui import KsuWebUIStandalone
from stuff.mindthegapps import MindTheGapps
from stuff.ndk import Ndk
from stuff.houdini import Houdini
from stuff.houdini_hack import Houdini_Hack
from stuff.widevine import Widevine
import tools.helper as helper
from tools.logger import get_logger, setup_logging
import subprocess


def validate_environment(logger):
    """Validate the build environment"""
    logger.info("Validating build environment...")

    # Check if we're in the right directory
    required_dirs = ['stuff', 'tools']
    missing_dirs = []

    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)

    if missing_dirs:
        logger.error(f"Missing required directories: {missing_dirs}")
        logger.error("Please run this script from the redroid-arm directory")
        return False

    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        logger.error(f"Python 3.6+ required, got {python_version.major}.{python_version.minor}")
        return False

    logger.info("Environment validation passed")
    return True


def safe_module_install(module_class, module_name, logger, *args, **kwargs):
    """Safely install a module with comprehensive error handling"""
    try:
        logger.log_module_start(module_name)

        # Create module instance
        if args or kwargs:
            module = module_class(*args, **kwargs)
        else:
            module = module_class()

        # Install module
        module.install()

        logger.log_module_success(module_name)
        return True

    except ImportError as e:
        logger.log_module_error(module_name, f"Import error: {e}")
        logger.error(f"Failed to import {module_name}. Check if the module file exists.")
        return False

    except FileNotFoundError as e:
        logger.log_module_error(module_name, f"File not found: {e}")
        logger.error(f"Required file not found for {module_name}: {e}")
        return False

    except PermissionError as e:
        logger.log_module_error(module_name, f"Permission denied: {e}")
        logger.error(f"Permission denied for {module_name}: {e}")
        logger.error("Try running with appropriate permissions or check file ownership")
        return False

    except subprocess.CalledProcessError as e:
        logger.log_module_error(module_name, f"Command failed: {e}")
        logger.error(f"Command execution failed for {module_name}")
        logger.error(f"Command: {e.cmd}")
        logger.error(f"Return code: {e.returncode}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr}")
        return False

    except Exception as e:
        logger.log_module_error(module_name, f"Unexpected error: {e}")
        logger.exception(f"Unexpected error during {module_name} installation")
        return False


def main():
    dockerfile = ""
    tags = []
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Enhanced ReDroid Script with latest Magisk v30.2 and modern modules"
    )

    # Android version with support for latest versions
    parser.add_argument('-a', '--android-version',
                        dest='android',
                        help='Specify the Android version to build',
                        default='15.0.0_64only',
                        choices=['15.0.0', '15.0.0_64only', '14.0.0', '14.0.0_64only',
                                '13.0.0', '12.0.0', '12.0.0_64only', '11.0.0', '10.0.0', '9.0.0', '8.1.0'])

    # Device profile support
    parser.add_argument('-d', '--device-profile',
                        dest='device',
                        help='Specify device profile for better compatibility',
                        default='pixel6',
                        choices=['pixel6', 'pixel7', 'pixel8', 'generic'])

    # Google Apps options
    parser.add_argument('-g', '--install-gapps',
                        dest='gapps',
                        help='Install OpenGapps to ReDroid',
                        action='store_true')
    parser.add_argument('-lg', '--install-litegapps',
                        dest='litegapps',
                        help='Install LiteGapps to ReDroid',
                        action='store_true')
    parser.add_argument('-mtg', '--install-mindthegapps',
                        dest='mindthegapps',
                        help='Install MindTheGapps to ReDroid',
                        action='store_true')

    # ARM translation
    parser.add_argument('-n', '--install-ndk-translation',
                        dest='ndk',
                        help='Install libndk translation files',
                        action='store_true')
    parser.add_argument('-i', '--install-houdini',
                        dest='houdini',
                        help='Install houdini files',
                        action='store_true')

    # Enhanced Magisk with modules
    parser.add_argument('-me', '--install-magisk-enhanced',
                        dest='magisk_enhanced',
                        help='Install Magisk Enhanced (v30.2) with modern modules',
                        action='store_true')
    parser.add_argument('-m', '--install-magisk',
                        dest='magisk',
                        help='Install legacy Magisk (original implementation)',
                        action='store_true')

    # Individual module options
    parser.add_argument('-rz', '--install-rezygisk',
                        dest='rezygisk',
                        help='Install ReZygisk module',
                        action='store_true')
    parser.add_argument('-pif', '--install-playintegrity',
                        dest='playintegrity',
                        help='Install PlayIntegrityFix module',
                        action='store_true')
    parser.add_argument('-ts', '--install-trickystore',
                        dest='trickystore',
                        help='Install TrickyStore module',
                        action='store_true')
    parser.add_argument('-ta', '--install-tricky-addon',
                        dest='tricky_addon',
                        help='Install Tricky-Addon-Update-Target-List module',
                        action='store_true')
    parser.add_argument('-ksu', '--install-ksu-webui',
                        dest='ksu_webui',
                        help='Install KsuWebUIStandalone module',
                        action='store_true')

    # Other features
    parser.add_argument('-w', '--install-widevine',
                        dest='widevine',
                        help='Integrate Widevine DRM (L3)',
                        action='store_true')

    # Container options
    parser.add_argument('-c', '--container',
                        dest='container',
                        default='docker',
                        help='Specify container type',
                        choices=['docker', 'podman'])

    # Add logging options
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        help='Enable verbose logging',
                        action='store_true')
    parser.add_argument('--debug',
                        dest='debug',
                        help='Enable debug logging (very verbose)',
                        action='store_true')
    parser.add_argument('--log-dir',
                        dest='log_dir',
                        help='Specify log directory',
                        default='logs')

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(verbose=args.verbose, debug=args.debug)

    # Log startup information
    logger.log_system_info({
        "android_version": args.android,
        "device_profile": args.device,
        "container_type": args.container,
        "python_version": sys.version,
        "platform": sys.platform,
        "working_directory": os.getcwd(),
        "arguments": vars(args)
    })

    # Validate environment
    if not validate_environment(logger):
        logger.error("Environment validation failed. Exiting.")
        logger.create_issue_report({"error": "environment_validation_failed"})
        return 1

    try:
        # Build base image
        logger.info(f"Building ReDroid Enhanced image for Android {args.android}")
        dockerfile = dockerfile + f"FROM redroid/redroid:{args.android}-latest\n"
        tags.append(args.android)

        build_start_time = time.time()

        # Add device profile if specified
        if args.device != 'generic':
            logger.info(f"Using device profile: {args.device}")
            tags.append(args.device)

        # Google Apps installation
        if args.gapps:
            if args.android in ["11.0.0"]:
                if safe_module_install(Gapps, "OpenGapps", logger):
                    dockerfile = dockerfile + "COPY gapps /\n"
                    tags.append("gapps")
                else:
                    logger.error("Failed to install OpenGapps")
                    raise Exception("OpenGapps installation failed")
            else:
                logger.warning("OpenGapps only supports Android 11.0.0")
                helper.print_color("WARNING: OpenGapps only supports 11.0.0", helper.bcolors.YELLOW)

        if args.litegapps:
            if safe_module_install(LiteGapps, "LiteGapps", logger, args.android):
                dockerfile = dockerfile + "COPY litegapps /\n"
                tags.append("litegapps")
            else:
                logger.error("Failed to install LiteGapps")
                raise Exception("LiteGapps installation failed")

        if args.mindthegapps:
            if safe_module_install(MindTheGapps, "MindTheGapps", logger, args.android):
                dockerfile = dockerfile + "COPY mindthegapps /\n"
                tags.append("mindthegapps")
            else:
                logger.error("Failed to install MindTheGapps")
                raise Exception("MindTheGapps installation failed")
    except Exception as e:
        logger.error(f"Error during build base image: {e}")
        raise

    # ARM translation
    if args.ndk:
        if args.android in ["11.0.0", "12.0.0", "12.0.0_64only", "13.0.0", "14.0.0", "14.0.0_64only", "15.0.0", "15.0.0_64only"]:
            arch = helper.host()[0]
            if arch == "x86" or arch == "x86_64" or arch == "arm64":
                Ndk().install()
                dockerfile = dockerfile + "COPY ndk /\n"
                tags.append("ndk")
        else:
            helper.print_color("WARNING: Libndk compatibility limited", helper.bcolors.YELLOW)

    if args.houdini:
        if args.android in ["8.1.0", "9.0.0", "11.0.0", "12.0.0", "13.0.0", "14.0.0"]:
            arch = helper.host()[0]
            if arch == "x86" or arch == "x86_64":
                Houdini(args.android).install()
                if not args.android == "8.1.0":
                    Houdini_Hack(args.android).install()
                dockerfile = dockerfile + "COPY houdini /\n"
                tags.append("houdini")
        else:
            helper.print_color("WARNING: Houdini compatibility limited", helper.bcolors.YELLOW)

        # Enhanced Magisk with all modules
        if args.magisk_enhanced:
            if safe_module_install(MagiskEnhanced, "Magisk Enhanced v30.2", logger):
                dockerfile = dockerfile + "COPY magisk_enhanced /\n"
                tags.append("magisk-enhanced")
            else:
                logger.error("Failed to install Magisk Enhanced")
                raise Exception("Magisk Enhanced installation failed")

            # Install individual modules if requested
            if args.rezygisk:
                if safe_module_install(ReZygisk, "ReZygisk", logger):
                    dockerfile = dockerfile + "COPY rezygisk /\n"
                    tags.append("rezygisk")
                else:
                    logger.warning("ReZygisk installation failed, continuing without it")

            if args.playintegrity:
                if safe_module_install(PlayIntegrityFix, "PlayIntegrityFix", logger):
                    dockerfile = dockerfile + "COPY playintegrity /\n"
                    tags.append("playintegrity")
                else:
                    logger.warning("PlayIntegrityFix installation failed, continuing without it")

            if args.trickystore:
                if safe_module_install(TrickyStore, "TrickyStore", logger):
                    dockerfile = dockerfile + "COPY trickystore /\n"
                    tags.append("trickystore")
                else:
                    logger.warning("TrickyStore installation failed, continuing without it")

            if args.tricky_addon:
                if safe_module_install(TrickyAddon, "TrickyAddon", logger):
                    dockerfile = dockerfile + "COPY tricky_addon /\n"
                    tags.append("tricky-addon")
                else:
                    logger.warning("TrickyAddon installation failed, continuing without it")

            if args.ksu_webui:
                if safe_module_install(KsuWebUIStandalone, "KsuWebUIStandalone", logger):
                    dockerfile = dockerfile + "COPY ksu_webui /\n"
                    tags.append("ksu-webui")
                else:
                    logger.warning("KsuWebUIStandalone installation failed, continuing without it")

    # Legacy Magisk (fallback)
    elif args.magisk:
        from stuff.magisk import Magisk
        Magisk().install()
        dockerfile = dockerfile + "COPY magisk /\n"
        tags.append("magisk")

    # Widevine DRM
    if args.widevine:
        if args.android in ["11.0.0", "12.0.0", "13.0.0", "14.0.0", "15.0.0"]:
            Widevine(args.android).install()
            dockerfile = dockerfile + "COPY widevine /\n"
            tags.append("widevine")
        else:
            helper.print_color("WARNING: Widevine may not be available for this Android version", helper.bcolors.YELLOW)

    # Device-specific optimizations
    if args.device == 'pixel6':
        dockerfile += """
# Pixel 6 specific optimizations
ENV ro.product.model="Pixel 6"
ENV ro.product.brand="google"
ENV ro.product.device="oriole"
ENV ro.build.fingerprint="google/oriole/oriole:${ANDROID_VERSION}/TQ3A.230901.001/10750268:user/release-keys"
"""
    elif args.device == 'pixel7':
        dockerfile += """
# Pixel 7 specific optimizations
ENV ro.product.model="Pixel 7"
ENV ro.product.brand="google"
ENV ro.product.device="panther"
ENV ro.build.fingerprint="google/panther/panther:${ANDROID_VERSION}/TQ3A.230901.001/10750268:user/release-keys"
"""
    elif args.device == 'pixel8':
        dockerfile += """
# Pixel 8 specific optimizations
ENV ro.product.model="Pixel 8"
ENV ro.product.brand="google"
ENV ro.product.device="shiba"
ENV ro.build.fingerprint="google/shiba/shiba:${ANDROID_VERSION}/UQ1A.240205.004/11269751:user/release-keys"
"""

    # Output and build
    logger.info("Generated Dockerfile:")
    logger.info(dockerfile)

    dockerfile_path = "./Dockerfile"
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile)
    logger.info(f"Dockerfile written to {dockerfile_path}")

    new_image_name = "redroid/redroid-enhanced:" + "-".join(tags)
    logger.log_docker_build_start(new_image_name, dockerfile)
    helper.print_color(f"Building enhanced image: {new_image_name}", helper.bcolors.GREEN)

    # Run Docker build with logging
    build_cmd = [args.container, "build", "-t", new_image_name, "."]
    logger.info(f"Executing build command: {' '.join(build_cmd)}")

    try:
        result = subprocess.run(build_cmd, capture_output=True, text=True, check=True)
        build_time = time.time() - build_start_time

        logger.log_docker_build_complete(new_image_name, build_time)
        logger.log_command_execution(build_cmd, result.returncode, result.stdout, result.stderr)

        helper.print_color("Successfully built {}".format(new_image_name), helper.bcolors.GREEN)

        # Print usage instructions
        print("\n" + "="*60)
        helper.print_color("Enhanced ReDroid Image Built Successfully!", helper.bcolors.GREEN)
        print("="*60)
        print(f"Image name: {new_image_name}")
        print("\nExample usage:")

        if args.device == 'pixel6' or args.device == 'pixel7' or args.device == 'pixel8':
            print(f"""
{args.container} run -itd --rm --privileged \\
    -v ~/data:/data \\
    -p 5555:5555 \\
    {new_image_name} \\
    androidboot.redroid_width=1080 \\
    androidboot.redroid_height=2400 \\
    androidboot.redroid_dpi=420 \\
    ro.product.cpu.abilist=x86_64,arm64-v8a,x86,armeabi-v7a,armeabi \\
    ro.product.cpu.abilist64=x86_64,arm64-v8a \\
    ro.product.cpu.abilist32=x86,armeabi-v7a,armeabi \\
    ro.dalvik.vm.isa.arm=x86 \\
    ro.dalvik.vm.isa.arm64=x86_64 \\
    ro.enable.native.bridge.exec=1 \\
    ro.vendor.enable.native.bridge.exec=1 \\
    ro.vendor.enable.native.bridge.exec64=1 \\
    ro.dalvik.vm.native.bridge=libndk_translation.so
""")
        else:
            print(f"""
{args.container} run -itd --rm --privileged \\
    -v ~/data:/data \\
    -p 5555:5555 \\
    {new_image_name}
""")

        if args.magisk_enhanced:
            logger.info("Magisk Enhanced Features included:")
            features = [
                "Latest Magisk v30.2",
                "ReZygisk for Zygisk functionality",
                "PlayIntegrityFix for app compatibility",
                "TrickyStore for advanced root hiding",
                "KsuWebUI for web-based management"
            ]
            for feature in features:
                logger.info(f"- {feature}")

            print("\nMagisk Enhanced Features:")
            for feature in features:
                print(f"- {feature}")
            print("\nAccess Magisk Manager after container starts.")

        # Log final success
        logger.info("\n" + "="*80)
        logger.info("BUILD COMPLETED SUCCESSFULLY!")
        logger.info(f"Image: {new_image_name}")
        logger.info(f"Build time: {time.time() - build_start_time:.2f} seconds")
        logger.info("\n" + "="*80)

        return 0

    except subprocess.CalledProcessError as e:
        logger.error(f"Docker build failed for {new_image_name}")
        logger.log_command_execution(build_cmd, e.returncode, e.stdout, e.stderr)
        raise Exception(f"Docker build failed: {e}")

    except Exception as e:
        logger.error("\n" + "="*80)
        logger.error("BUILD FAILED!")
        logger.error(f"Error: {str(e)}")
        logger.exception("Full traceback:")
        logger.error("\n" + "="*80)

        # Create issue report
        report_file = logger.create_issue_report({
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "android_version": args.android,
            "device_profile": args.device,
            "selected_modules": {
                "gapps": args.gapps,
                "litegapps": args.litegapps,
                "mindthegapps": args.mindthegapps,
                "magisk_enhanced": args.magisk_enhanced,
                "rezygisk": args.rezygisk,
                "playintegrity": args.playintegrity,
                "trickystore": args.trickystore,
                "tricky_addon": args.tricky_addon,
                "ksu_webui": args.ksu_webui,
                "ndk": args.ndk,
                "houdini": args.houdini,
                "widevine": args.widevine
            }
        })

        print(f"\n{helper.bcolors.RED}Build failed! Check logs for details.{helper.bcolors.ENDC}")
        print(f"{helper.bcolors.YELLOW}Issue report created: {report_file}{helper.bcolors.ENDC}")
        print(f"{helper.bcolors.YELLOW}Please share this file when reporting issues.{helper.bcolors.ENDC}")

        return 1

    finally:
        logger.finalize()


if __name__ == "__main__":
    sys.exit(main())