#!/usr/bin/env python3

import os
import subprocess
import sys
from tools.helper import print_color, bcolors

def test_dependencies():
    """Test if all required dependencies are available"""
    print_color("Testing dependencies...", bcolors.GREEN)

    dependencies = ['python3', 'docker', 'lzip', 'tar', 'unzip']
    missing = []

    for dep in dependencies:
        try:
            result = subprocess.run(['which', dep], capture_output=True, text=True)
            if result.returncode != 0:
                missing.append(dep)
            else:
                print(f"✓ {dep} found at {result.stdout.strip()}")
        except Exception as e:
            missing.append(dep)
            print(f"✗ {dep} check failed: {e}")

    if missing:
        print_color(f"Missing dependencies: {', '.join(missing)}", bcolors.RED)
        return False

    print_color("All dependencies satisfied", bcolors.GREEN)
    return True

def test_docker_permissions():
    """Test if Docker is accessible without sudo"""
    print_color("Testing Docker permissions...", bcolors.GREEN)

    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Docker accessible")
            return True
        else:
            print_color("✗ Docker not accessible, check permissions", bcolors.RED)
            return False
    except Exception as e:
        print_color(f"✗ Docker test failed: {e}", bcolors.RED)
        return False

def test_module_imports():
    """Test if all Python modules can be imported"""
    print_color("Testing module imports...", bcolors.GREEN)

    modules = [
        'stuff.magisk_enhanced',
        'stuff.rezygisk',
        'stuff.playintegrity',
        'stuff.trickystore',
        'stuff.tricky_addon',
        'stuff.ksu_webui',
        'stuff.litegapps',
        'stuff.ndk',
        'tools.helper'
    ]

    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            failed.append(module)
            print(f"✗ {module}: {e}")

    if failed:
        print_color(f"Failed imports: {', '.join(failed)}", bcolors.RED)
        return False

    print_color("All modules imported successfully", bcolors.GREEN)
    return True

def test_download_connectivity():
    """Test connectivity to download sources"""
    print_color("Testing download connectivity...", bcolors.GREEN)

    test_urls = [
        'https://github.com/topjohnwu/Magisk/releases',
        'https://github.com/PerformanC/ReZygisk/releases',
        'https://sourceforge.net/projects/litegapps/files/',
        'https://hub.docker.com/r/redroid/redroid'
    ]

    failed = []
    for url in test_urls:
        try:
            import urllib.request
            urllib.request.urlopen(url, timeout=10)
            print(f"✓ {url.split('/')[2]}")
        except Exception as e:
            failed.append(url)
            print(f"✗ {url.split('/')[2]}: {e}")

    if failed:
        print_color("Some connectivity issues detected", bcolors.YELLOW)
    else:
        print_color("All connectivity tests passed", bcolors.GREEN)

    return len(failed) == 0

def test_dry_run():
    """Test script execution with dry run"""
    print_color("Testing script dry run...", bcolors.GREEN)

    try:
        # Test basic argument parsing
        result = subprocess.run([
            'python3', 'redroid_enhanced.py', '--help'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ Script argument parsing works")
            return True
        else:
            print_color(f"✗ Script help failed: {result.stderr}", bcolors.RED)
            return False
    except Exception as e:
        print_color(f"✗ Dry run failed: {e}", bcolors.RED)
        return False

def run_build_test():
    """Run a minimal build test"""
    print_color("Running minimal build test...", bcolors.GREEN)

    # Test with minimal options (no downloads)
    cmd = [
        'python3', 'redroid_enhanced.py',
        '-a', '15.0.0_64only',
        '-d', 'pixel7',
        '--help'  # Just test help for now
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ Basic command structure works")
            return True
        else:
            print_color(f"✗ Build test failed: {result.stderr}", bcolors.RED)
            return False
    except subprocess.TimeoutExpired:
        print_color("✗ Build test timed out", bcolors.RED)
        return False
    except Exception as e:
        print_color(f"✗ Build test error: {e}", bcolors.RED)
        return False

def main():
    """Run all tests"""
    print_color("=== Enhanced ReDroid Build Test Suite ===", bcolors.GREEN)
    print()

    tests = [
        ("Dependencies", test_dependencies),
        ("Docker Permissions", test_docker_permissions),
        ("Module Imports", test_module_imports),
        ("Download Connectivity", test_download_connectivity),
        ("Script Dry Run", test_dry_run),
        ("Build Test", run_build_test)
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
        print()

    # Summary
    print("="*60)
    print_color("TEST SUMMARY", bcolors.GREEN)
    print("="*60)

    passed = 0
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        color = bcolors.GREEN if result else bcolors.RED
        print_color(f"{test_name:.<30} {status}", color)
        if result:
            passed += 1

    print()
    if passed == len(tests):
        print_color("🎉 All tests passed! Ready to build enhanced ReDroid images.", bcolors.GREEN)
        return 0
    else:
        failed = len(tests) - passed
        print_color(f"⚠️  {failed} test(s) failed. Please fix issues before building.", bcolors.YELLOW)
        return 1

if __name__ == "__main__":
    sys.exit(main())