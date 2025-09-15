#!/usr/bin/env python3
"""
ReDroid Compatible Script - 100% backward compatible with original redroid.py
while adding enhanced features when using new arguments.
"""

import argparse
import sys
import os
import traceback
import time
from pathlib import Path

# Import original modules
from stuff.gapps import Gapps
from stuff.litegapps import LiteGapps
from stuff.magisk import Magisk
from stuff.mindthegapps import MindTheGapps
from stuff.ndk import Ndk
from stuff.houdini import Houdini
from stuff.houdini_hack import Houdini_Hack
from stuff.widevine import Widevine

# Import enhanced modules
from stuff.magisk_enhanced import MagiskEnhanced
from stuff.rezygisk import ReZygisk
from stuff.playintegrity import PlayIntegrityFix
from stuff.trickystore import TrickyStore
from stuff.tricky_addon import TrickyAddon
from stuff.ksu_webui import KsuWebUIStandalone

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

    # Create parser with same format as original
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # ORIGINAL ARGUMENTS (100% compatible)
    parser.add_argument('-a', '--android-version',
                        dest='android',
                        help='Specify the Android version to build',
                        default='11.0.0',  # Keep original default
                        choices=['15.0.0', '15.0.0_64only', '14.0.0', '14.0.0_64only',
                                '13.0.0', '12.0.0', '12.0.0_64only', '11.0.0', '10.0.0', '9.0.0', '8.1.0'])
    parser.add_argument('-g', '--install-gapps',
                        dest='gapps',
                        help='Install OpenGapps to ReDroid',
                        action='store_true')
    parser.add_argument('-lg', '--install-litegapps',
                        dest='litegapps',
                        help='Install LiteGapps to ReDroid',
                        action='store_true')
    parser.add_argument('-n', '--install-ndk-translation',
                        dest='ndk',
                        help='Install libndk translation files',
                        action='store_true')
    parser.add_argument('-i', '--install-houdini',
                        dest='houdini',
                        help='Install houdini files',
                        action='store_true')
    parser.add_argument('-mtg', '--install-mindthegapps',
                        dest='mindthegapps',
                        help='Install MindTheGapps to ReDroid',
                        action='store_true')
    parser.add_argument('-m', '--install-magisk',
                        dest='magisk',
                        help='Install Magisk ( Bootless )',
                        action='store_true')
    parser.add_argument('-w', '--install-widevine',
                        dest='widevine',
                        help='Integrate Widevine DRM (L3)',
                        action='store_true')
    parser.add_argument('-c', '--container',
                        dest='container',
                        default='docker',
                        help='Specify container type',
                        choices=['docker', 'podman'])

    # ENHANCED ARGUMENTS (new features)
    parser.add_argument('-d', '--device-profile',
                        dest='device',
                        help='Specify device profile for better compatibility',
                        default='generic',
                        choices=['pixel6', 'pixel7', 'pixel8', 'generic'])

    # Enhanced Magisk with modules
    parser.add_argument('-me', '--install-magisk-enhanced',
                        dest='magisk_enhanced',
                        help='Install Magisk Enhanced (v30.2) with modern modules',
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

    # Logging options (optional)
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

    # Determine if we're in enhanced mode or legacy mode
    enhanced_features = any([
        args.device != 'generic',
        args.magisk_enhanced,
        args.rezygisk,
        args.playintegrity,
        args.trickystore,
        args.tricky_addon,
        args.ksu_webui,
        args.verbose,
        args.debug
    ])

    # Setup logging only if enhanced features are used or verbose/debug is enabled
    if enhanced_features or args.verbose or args.debug:
        logger = setup_logging(verbose=args.verbose, debug=args.debug)
        use_logging = True
    else:
        logger = None
        use_logging = False

    try:
        if use_logging:
            # Log startup information
            logger.log_system_info({
                "android_version": args.android,
                "device_profile": args.device,
                "container_type": args.container,
                "enhanced_mode": enhanced_features,
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

            logger.info(f"Building ReDroid image for Android {args.android}")
            build_start_time = time.time()

        # ORIGINAL DOCKERFILE GENERATION (matching original format exactly)
        dockerfile = dockerfile + "FROM redroid/redroid:{}-latest\n".format(args.android)
        tags.append(args.android)

        # Add device profile if specified (enhanced feature)
        if args.device != 'generic':
            if use_logging:
                logger.info(f"Using device profile: {args.device}")
            tags.append(args.device)

        # ORIGINAL GAPPS INSTALLATION (exact same logic)
        if args.gapps:
            if args.android in ["11.0.0"]:
                if use_logging:
                    if safe_module_install(Gapps, "OpenGapps", logger):
                        dockerfile = dockerfile + "COPY gapps /\n"
                        tags.append("gapps")
                    else:
                        logger.error("Failed to install OpenGapps")
                        raise Exception("OpenGapps installation failed")
                else:
                    Gapps().install()
                    dockerfile = dockerfile + "COPY gapps /\n"
                    tags.append("gapps")
            else:
                if use_logging:
                    logger.warning("OpenGapps only supports Android 11.0.0")
                helper.print_color("WARNING: OpenGapps only supports 11.0.0", helper.bcolors.YELLOW)

        if args.litegapps:
            if use_logging:
                if safe_module_install(LiteGapps, "LiteGapps", logger, args.android):
                    dockerfile = dockerfile + "COPY litegapps /\n"
                    tags.append("litegapps")
                else:
                    logger.error("Failed to install LiteGapps")
                    raise Exception("LiteGapps installation failed")
            else:
                LiteGapps(args.android).install()
                dockerfile = dockerfile + "COPY litegapps /\n"
                tags.append("litegapps")

        if args.mindthegapps:
            if use_logging:
                if safe_module_install(MindTheGapps, "MindTheGapps", logger, args.android):
                    dockerfile = dockerfile + "COPY mindthegapps /\n"
                    tags.append("mindthegapps")
                else:
                    logger.error("Failed to install MindTheGapps")
                    raise Exception("MindTheGapps installation failed")
            else:
                MindTheGapps(args.android).install()
                dockerfile = dockerfile + "COPY mindthegapps /\n"
                tags.append("mindthegapps")

        # ORIGINAL NDK INSTALLATION (exact same logic)
        if args.ndk:
            if args.android in ["11.0.0", "12.0.0", "12.0.0_64only", "13.0.0", "14.0.0", "14.0.0_64only", "15.0.0", "15.0.0_64only"]:
                arch = helper.host()[0]
                if arch == "x86" or arch == "x86_64" or arch == "arm64":
                    if use_logging:
                        if safe_module_install(Ndk, "NDK Translation", logger):
                            dockerfile = dockerfile + "COPY ndk /\n"
                            tags.append("ndk")
                        else:
                            logger.warning("NDK installation failed, continuing without it")
                    else:
                        Ndk().install()
                        dockerfile = dockerfile+"COPY ndk /\n"
                        tags.append("ndk")
            else:
                if use_logging:
                    logger.warning("Libndk compatibility limited to newer Android versions")
                helper.print_color("WARNING: Libndk seems to work only on redroid:11.0.0 or newer", helper.bcolors.YELLOW)

        # ORIGINAL HOUDINI INSTALLATION (exact same logic)
        if args.houdini:
            if args.android in ["8.1.0", "9.0.0", "11.0.0", "12.0.0", "13.0.0", "14.0.0"]:
                arch = helper.host()[0]
                if arch == "x86" or arch == "x86_64":
                    if use_logging:
                        if safe_module_install(Houdini, "Houdini", logger, args.android):
                            if not args.android == "8.1.0":
                                safe_module_install(Houdini_Hack, "Houdini_Hack", logger, args.android)
                            dockerfile = dockerfile + "COPY houdini /\n"
                            tags.append("houdini")
                        else:
                            logger.warning("Houdini installation failed, continuing without it")
                    else:
                        Houdini(args.android).install()
                        if not args.android == "8.1.0":
                            Houdini_Hack(args.android).install()
                        dockerfile = dockerfile+"COPY houdini /\n"
                        tags.append("houdini")
            else:
                if use_logging:
                    logger.warning("Houdini compatibility limited")
                helper.print_color("WARNING: Houdini seems to work only above redroid:11.0.0", helper.bcolors.YELLOW)

        # MAGISK INSTALLATION (original vs enhanced)
        if args.magisk_enhanced:
            # Enhanced Magisk with all modules
            if use_logging:
                if safe_module_install(MagiskEnhanced, "Magisk Enhanced v30.2", logger):
                    dockerfile = dockerfile + "COPY magisk_enhanced /\n"
                    tags.append("magisk-enhanced")
                else:
                    logger.error("Failed to install Magisk Enhanced")
                    raise Exception("Magisk Enhanced installation failed")
            else:
                MagiskEnhanced().install()
                dockerfile = dockerfile + "COPY magisk_enhanced /\n"
                tags.append("magisk-enhanced")

            # Install individual modules if requested
            if args.rezygisk:
                if use_logging and safe_module_install(ReZygisk, "ReZygisk", logger):
                    dockerfile = dockerfile + "COPY rezygisk /\n"
                    tags.append("rezygisk")
                elif not use_logging:
                    ReZygisk().install()
                    dockerfile = dockerfile + "COPY rezygisk /\n"
                    tags.append("rezygisk")

            if args.playintegrity:
                if use_logging and safe_module_install(PlayIntegrityFix, "PlayIntegrityFix", logger):
                    dockerfile = dockerfile + "COPY playintegrity /\n"
                    tags.append("playintegrity")
                elif not use_logging:
                    PlayIntegrityFix().install()
                    dockerfile = dockerfile + "COPY playintegrity /\n"
                    tags.append("playintegrity")

            if args.trickystore:
                if use_logging and safe_module_install(TrickyStore, "TrickyStore", logger):
                    dockerfile = dockerfile + "COPY trickystore /\n"
                    tags.append("trickystore")
                elif not use_logging:
                    TrickyStore().install()
                    dockerfile = dockerfile + "COPY trickystore /\n"
                    tags.append("trickystore")

            if args.tricky_addon:
                if use_logging and safe_module_install(TrickyAddon, "TrickyAddon", logger):
                    dockerfile = dockerfile + "COPY tricky_addon /\n"
                    tags.append("tricky-addon")
                elif not use_logging:
                    TrickyAddon().install()
                    dockerfile = dockerfile + "COPY tricky_addon /\n"
                    tags.append("tricky-addon")

            if args.ksu_webui:
                if use_logging and safe_module_install(KsuWebUIStandalone, "KsuWebUIStandalone", logger):
                    dockerfile = dockerfile + "COPY ksu_webui /\n"
                    tags.append("ksu-webui")
                elif not use_logging:
                    KsuWebUIStandalone().install()
                    dockerfile = dockerfile + "COPY ksu_webui /\n"
                    tags.append("ksu-webui")

        elif args.magisk:
            # ORIGINAL MAGISK INSTALLATION (exact same)
            if use_logging:
                if safe_module_install(Magisk, "Magisk", logger):
                    dockerfile = dockerfile + "COPY magisk /\n"
                    tags.append("magisk")
                else:
                    logger.error("Failed to install Magisk")
                    raise Exception("Magisk installation failed")
            else:
                Magisk().install()
                dockerfile = dockerfile+"COPY magisk /\n"
                tags.append("magisk")

        # ORIGINAL WIDEVINE INSTALLATION (exact same logic)
        if args.widevine:
            if use_logging:
                if safe_module_install(Widevine, "Widevine", logger, args.android):
                    dockerfile = dockerfile + "COPY widevine /\n"
                    tags.append("widevine")
                else:
                    logger.warning("Widevine installation failed, continuing without it")
            else:
                Widevine(args.android).install()
                dockerfile = dockerfile+"COPY widevine /\n"
                tags.append("widevine")

        # Device-specific optimizations (enhanced feature)
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

        # OUTPUT AND BUILD (original format vs enhanced)
        if use_logging:
            logger.info("Generated Dockerfile:")
            logger.info(dockerfile)
            dockerfile_path = "./Dockerfile"
            with open(dockerfile_path, "w") as f:
                f.write(dockerfile)
            logger.info(f"Dockerfile written to {dockerfile_path}")
        else:
            # ORIGINAL OUTPUT FORMAT
            print("\nDockerfile\n"+dockerfile)
            with open("./Dockerfile", "w") as f:
                f.write(dockerfile)

        # ORIGINAL IMAGE NAMING vs ENHANCED
        if enhanced_features:
            new_image_name = "redroid/redroid-enhanced:" + "-".join(tags)
        else:
            # ORIGINAL NAMING SCHEME
            new_image_name = "redroid/redroid:"+"_".join(tags)

        if use_logging:
            logger.log_docker_build_start(new_image_name, dockerfile)
            helper.print_color(f"Building image: {new_image_name}", helper.bcolors.GREEN)

            # Run Docker build with logging
            build_cmd = [args.container, "build", "-t", new_image_name, "."]
            logger.info(f"Executing build command: {' '.join(build_cmd)}")

            try:
                result = subprocess.run(build_cmd, capture_output=True, text=True, check=True)
                build_time = time.time() - build_start_time

                logger.log_docker_build_complete(new_image_name, build_time)
                logger.log_command_execution(build_cmd, result.returncode, result.stdout, result.stderr)

                helper.print_color("Successfully built {}".format(new_image_name), helper.bcolors.GREEN)

            except subprocess.CalledProcessError as e:
                logger.error(f"Docker build failed for {new_image_name}")
                logger.log_command_execution(build_cmd, e.returncode, e.stdout, e.stderr)
                raise Exception(f"Docker build failed: {e}")
        else:
            # ORIGINAL BUILD (exact same)
            subprocess.run([args.container, "build", "-t", new_image_name, "."])
            helper.print_color("Successfully built {}".format(new_image_name), helper.bcolors.GREEN)

        # Enhanced features info (only if enhanced mode)
        if args.magisk_enhanced and use_logging:
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

        if use_logging:
            # Log final success
            logger.info("\n" + "="*80)
            logger.info("BUILD COMPLETED SUCCESSFULLY!")
            logger.info(f"Image: {new_image_name}")
            logger.info(f"Build time: {time.time() - build_start_time:.2f} seconds")
            logger.info("\n" + "="*80)

        return 0

    except Exception as e:
        if use_logging:
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
                "enhanced_mode": enhanced_features,
                "selected_modules": {
                    "gapps": args.gapps,
                    "litegapps": args.litegapps,
                    "mindthegapps": args.mindthegapps,
                    "magisk": args.magisk,
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
        else:
            # Original error handling (minimal)
            print(f"{helper.bcolors.RED}Build failed: {str(e)}{helper.bcolors.ENDC}")
            traceback.print_exc()

        return 1

    finally:
        if use_logging:
            logger.finalize()


if __name__ == "__main__":
    sys.exit(main())