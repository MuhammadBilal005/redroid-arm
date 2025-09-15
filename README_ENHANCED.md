# Enhanced ReDroid Script

This enhanced script builds upon the original ReDroid script with modern Magisk modules and support for the latest Android versions. It includes Magisk v30.2 with advanced root hiding capabilities and Play Integrity bypassing.

## Features

### ✨ Latest Android Support
- **Android 15.0.0** (latest) with 64-bit support
- **Android 14.0.0** with enhanced compatibility
- All previous versions (13.0.0, 12.0.0, 11.0.0, etc.)

### 🚀 Enhanced Magisk Integration
- **Magisk v30.2** (latest stable release)
- **ReZygisk v1.0.0-rc.3** - Modern Zygisk implementation
- **PlayIntegrityFix v4.3-inject-s** - Bypass Play Integrity API
- **TrickyStore v1.3.0** - Advanced root hiding
- **Tricky-Addon-Update-Target-List v4.1** - Enhanced target list
- **KsuWebUIStandalone v1.0** - Web-based management interface

### 📱 Device Profile Support
- **Pixel 6** - Optimized profile with correct fingerprints
- **Pixel 7** - Latest Pixel device support
- **Pixel 8** - Newest Pixel series support
- **Generic** - Universal compatibility

### 🛡️ Advanced Security Features
- Play Integrity API bypass
- SafetyNet workarounds
- Root hiding from banking/payment apps
- Enhanced module isolation

## Quick Start

### Basic Enhanced Build
```bash
python redroid_enhanced.py -a 15.0.0_64only -d pixel7 -me -lg -n -w
```

This creates a Pixel 7 profile with Android 15, enhanced Magisk, LiteGapps, NDK translation, and Widevine.

### Full Featured Build
```bash
python redroid_enhanced.py -a 15.0.0_64only -d pixel7 -me -rz -pif -ts -ta -ksu -lg -n -w
```

This includes all modules for maximum compatibility and functionality.

## Detailed Usage

### Android Version Selection
```bash
# Latest Android 15 (recommended)
python redroid_enhanced.py -a 15.0.0_64only

# Android 14 with full architecture support
python redroid_enhanced.py -a 14.0.0

# Android 13 for broader app compatibility
python redroid_enhanced.py -a 13.0.0
```

### Device Profiles
```bash
# Pixel 6 profile
python redroid_enhanced.py -d pixel6

# Pixel 7 profile (recommended)
python redroid_enhanced.py -d pixel7

# Pixel 8 profile (latest)
python redroid_enhanced.py -d pixel8
```

### Enhanced Magisk Options
```bash
# Complete enhanced Magisk installation
python redroid_enhanced.py -me -rz -pif -ts -ta -ksu

# Individual modules
python redroid_enhanced.py -me -rz    # ReZygisk only
python redroid_enhanced.py -me -pif   # PlayIntegrityFix only
python redroid_enhanced.py -me -ts    # TrickyStore only
```

### Google Apps Options
```bash
# LiteGapps (recommended for modern Android)
python redroid_enhanced.py -lg

# MindTheGapps (alternative)
python redroid_enhanced.py -mtg

# OpenGapps (Android 11 only)
python redroid_enhanced.py -g
```

## Container Deployment

### Docker (Default)
```bash
docker run -itd --rm --privileged \
    --name redroid-enhanced \
    -v ~/redroid-data:/data \
    -p 5555:5555 \
    redroid/redroid-enhanced:15.0.0_64only-pixel7-magisk-enhanced-litegapps-ndk-widevine \
    androidboot.redroid_width=1080 \
    androidboot.redroid_height=2400 \
    androidboot.redroid_dpi=420 \
    ro.product.cpu.abilist=x86_64,arm64-v8a,x86,armeabi-v7a,armeabi \
    ro.product.cpu.abilist64=x86_64,arm64-v8a \
    ro.product.cpu.abilist32=x86,armeabi-v7a,armeabi \
    ro.dalvik.vm.isa.arm=x86 \
    ro.dalvik.vm.isa.arm64=x86_64 \
    ro.enable.native.bridge.exec=1 \
    ro.vendor.enable.native.bridge.exec=1 \
    ro.vendor.enable.native.bridge.exec64=1 \
    ro.dalvik.vm.native.bridge=libndk_translation.so
```

### Podman Support
```bash
python redroid_enhanced.py -c podman -a 15.0.0_64only -d pixel7 -me -lg -n
```

## Module Descriptions

### 🔧 ReZygisk
- Modern Zygisk implementation
- Better performance than traditional Zygisk
- Enhanced module loading capabilities

### 🛡️ PlayIntegrityFix
- Bypasses Play Integrity API checks
- Enables banking and payment apps
- Works with latest Google Play updates

### 🎭 TrickyStore
- Advanced root hiding mechanism
- Keystore-based attestation spoofing
- Works with hardware-backed keystore

### 📋 Tricky-Addon-Update-Target-List
- Enhanced target application list
- Regular updates for new app compatibility
- Automatic detection improvements

### 🌐 KsuWebUIStandalone
- Web-based Magisk management
- Remote module management
- Status monitoring and logs

## Architecture Support

### ARM64 Host Compatibility
The enhanced script includes better ARM64 support:
- Native ARM64 binary handling
- Improved libndk translation
- Better container compatibility on ARM hosts

### Multi-Architecture Images
- x86_64 (Intel/AMD)
- ARM64 (Apple Silicon, ARM servers)
- Cross-platform compatibility

## Troubleshooting

### Play Integrity Issues
If apps still detect root:
1. Ensure PlayIntegrityFix is properly installed
2. Check TrickyStore configuration
3. Verify device profile matches target device
4. Clear app data and retry

### Performance Optimization
For better performance:
1. Use 64-bit only images when possible
2. Allocate sufficient RAM (8GB+ recommended)
3. Enable hardware acceleration if available
4. Use SSD storage for container data

### Module Loading Issues
If modules don't load:
1. Check container logs: `docker logs <container-name>`
2. Verify file permissions in `/data/adb/modules`
3. Ensure Magisk database is properly initialized
4. Restart container if needed

## Advanced Configuration

### Custom Device Properties
You can override device properties by mounting a custom `build.prop`:
```bash
-v ./custom_build.prop:/system/build.prop:ro
```

### Module Development
The enhanced script supports custom module development:
1. Place module ZIP in `modules/` directory
2. Modify the script to include your module
3. Build and test

## Requirements

- Python 3.6+
- Docker or Podman
- 8GB+ RAM (recommended)
- 20GB+ storage space
- Internet connection for downloads

## License

This enhanced script maintains compatibility with the original project's license while adding modern functionality for current Android ecosystem requirements.

## Contributing

1. Fork the repository
2. Create feature branch
3. Test with multiple Android versions
4. Submit pull request with detailed description

## Credits

- Original ReDroid Script by ayasa520
- Magisk by topjohnwu
- ReZygisk by PerformanC
- PlayIntegrityFix by KOWX712
- TrickyStore by 5ec1cff
- Enhanced integration and modernization

---

**Note**: This enhanced version focuses on modern Android compatibility and advanced root hiding capabilities. It's designed for users who need the latest features and maximum app compatibility.