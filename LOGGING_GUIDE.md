# 📋 Enhanced ReDroid Logging & Debugging Guide

The enhanced ReDroid script includes comprehensive logging to help debug issues when running on servers or encountering problems during the build process.

## 🚀 Quick Start

### Enable Detailed Logging
```bash
# Verbose logging (recommended)
python redroid_enhanced.py -v -a 15.0.0_64only -d pixel7 -me -lg

# Debug logging (very detailed)
python redroid_enhanced.py --debug -a 15.0.0_64only -d pixel7 -me -lg

# Custom log directory
python redroid_enhanced.py -v --log-dir /path/to/logs -a 15.0.0_64only -d pixel7 -me
```

### Analyze Logs After Failed Build
```bash
# Quick error analysis
python analyze_logs.py --errors-only

# Full analysis
python analyze_logs.py

# Analyze specific session
python analyze_logs.py --session 20241215_143022

# Create debug package for sharing
python analyze_logs.py --create-debug-package
```

## 📁 Log File Structure

The script creates multiple log files in the `logs/` directory:

```
logs/
├── detailed_20241215_143022.log    # Complete detailed log
├── errors_20241215_143022.log      # Errors only
├── structured_20241215_143022.json # Machine-readable JSON log
├── issue_report_20241215_143022.json # Auto-generated issue report
├── latest_detailed.log             # Symlink to latest detailed log
├── latest_errors.log               # Symlink to latest error log
└── latest_structured.json          # Symlink to latest JSON log
```

## 📊 Log Types Explained

### 1. Detailed Log (`detailed_*.log`)
- **Purpose**: Complete build process with timestamps
- **Contains**: All INFO, WARNING, ERROR messages with context
- **Format**: Human-readable with file/line references
- **Use case**: Understanding the complete build flow

**Example:**
```
2024-12-15 14:30:22,123 - redroid_enhanced - INFO - [redroid_enhanced.py:145] - Starting Magisk Enhanced v30.2 installation
2024-12-15 14:30:25,456 - redroid_enhanced - ERROR - [magisk_enhanced.py:89] - Download failed: Connection timeout
```

### 2. Error Log (`errors_*.log`)
- **Purpose**: Errors and critical issues only
- **Contains**: ERROR and CRITICAL level messages
- **Format**: Same as detailed but filtered
- **Use case**: Quick error identification

### 3. Structured Log (`structured_*.json`)
- **Purpose**: Machine-readable logging for automated analysis
- **Contains**: All events in JSON format with metadata
- **Format**: One JSON object per line
- **Use case**: Automated debugging, metrics, integration

**Example:**
```json
{
  "timestamp": "2024-12-15T14:30:22.123456",
  "level": "ERROR",
  "logger": "redroid_enhanced",
  "message": "Download failed: Connection timeout",
  "module": "magisk_enhanced",
  "action": "download_error",
  "url": "https://github.com/topjohnwu/Magisk/releases/download/v30.2/Magisk-v30.2.apk",
  "error": "ConnectionTimeout",
  "filename": "magisk.apk"
}
```

### 4. Issue Report (`issue_report_*.json`)
- **Purpose**: Comprehensive debugging information
- **Generated**: Automatically when build fails
- **Contains**: System info, environment, error context, all logs
- **Use case**: Sharing with developers for bug reports

## 🔍 Log Analysis Features

The `analyze_logs.py` script provides intelligent analysis:

### Error Pattern Detection
- **Import Errors**: Missing Python modules
- **File Not Found**: Missing files or incorrect paths
- **Permission Errors**: File/directory access issues
- **Command Failures**: Shell command execution problems
- **Network Errors**: Download and connectivity issues

### Module Analysis
- **Installation Status**: Success/failure for each module
- **Error Context**: Specific errors for failed modules
- **Dependencies**: Missing dependencies detection

### Download Analysis
- **Success Rate**: Completed vs. failed downloads
- **Incomplete Downloads**: Started but not finished
- **Network Issues**: Connection problems, timeouts

### Docker Build Analysis
- **Build Progress**: Start/completion tracking
- **Resource Issues**: Memory, disk space problems
- **Command Failures**: Specific Docker command errors

## 🛠️ Common Issues & Solutions

### 1. Download Failures
**Symptoms:**
```
ERROR - Download failed: Connection timeout
ERROR - URLError: <urlopen error [Errno 110] Connection timed out>
```

**Analysis:**
```bash
python analyze_logs.py --errors-only
```

**Solutions:**
- Check internet connection
- Try again later (servers may be down)
- Use VPN if region-blocked
- Check firewall/proxy settings

### 2. Permission Errors
**Symptoms:**
```
ERROR - Permission denied: /path/to/file
ERROR - [Errno 13] Permission denied: 'docker'
```

**Solutions:**
- Add user to docker group: `sudo usermod -aG docker $USER`
- Check file ownership: `ls -la`
- Run with proper permissions
- Verify Docker daemon is running

### 3. Missing Dependencies
**Symptoms:**
```
ERROR - Command not found: lzip
ERROR - ImportError: No module named 'requests'
```

**Solutions:**
```bash
# Install system dependencies
sudo apt-get install lzip tar unzip

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Disk Space Issues
**Symptoms:**
```
ERROR - No space left on device
WARNING - Low disk space: 2.1 GB available, 5 GB recommended
```

**Solutions:**
- Free up disk space
- Use external storage
- Clean Docker images: `docker system prune`

### 5. Module Installation Failures
**Symptoms:**
```
ERROR - Failed to install ReZygisk: File not found
ERROR - Module installation timeout
```

**Analysis:**
```bash
python analyze_logs.py
# Look for "Module Installation Analysis" section
```

**Solutions:**
- Check module URLs are accessible
- Verify extracted files exist
- Check module-specific requirements

## 📤 Sharing Logs for Support

### Create Debug Package
```bash
# Latest build
python analyze_logs.py --create-debug-package

# Specific session
python analyze_logs.py --create-debug-package --session 20241215_143022
```

This creates a single file containing all relevant logs and system information.

### Manual Log Sharing
If you need to share logs manually:

1. **Always include:**
   - `latest_detailed.log` - Complete build log
   - `latest_errors.log` - Error summary
   - `issue_report_*.json` - System information

2. **Optionally include:**
   - `latest_structured.json` - For detailed analysis
   - Output of `analyze_logs.py` - For pre-analysis

### Sensitive Information
The logging system automatically:
- ✅ Excludes tokens and passwords from environment variables
- ✅ Truncates long paths for privacy
- ✅ Includes only necessary system information
- ⚠️ **Still review logs before sharing publicly**

## 🔧 Advanced Debugging

### Enable Maximum Logging
```bash
python redroid_enhanced.py \
  --debug \
  --log-dir /tmp/redroid-debug \
  -a 15.0.0_64only \
  -d pixel7 \
  -me -lg -n -w
```

### Real-time Log Monitoring
```bash
# In one terminal, start build
python redroid_enhanced.py --debug -a 15.0.0_64only -d pixel7 -me

# In another terminal, monitor logs
tail -f logs/latest_detailed.log

# Monitor errors only
tail -f logs/latest_errors.log
```

### Session Management
```bash
# List all build sessions
python analyze_logs.py --list-sessions

# Analyze specific session
python analyze_logs.py --session 20241215_143022

# Compare multiple sessions
python analyze_logs.py --session 20241215_143022 > session1.txt
python analyze_logs.py --session 20241215_150000 > session2.txt
diff session1.txt session2.txt
```

## 🎯 Log Integration

### CI/CD Integration
The structured JSON logs can be parsed by CI/CD systems:

```bash
# Extract build status
grep '"action":"docker_build_complete"' logs/latest_structured.json

# Check for critical errors
grep '"level":"CRITICAL"' logs/latest_structured.json

# Extract build metrics
grep '"build_time"' logs/latest_structured.json | jq '.build_time'
```

### Monitoring Integration
Set up alerts based on log patterns:

```bash
# Check for repeated failures
grep "BUILD FAILED" logs/detailed_*.log | wc -l

# Monitor disk space warnings
grep "Low disk space" logs/latest_detailed.log

# Track download success rate
python -c "
import json
successes = sum(1 for line in open('logs/latest_structured.json')
                if 'download_complete' in line)
failures = sum(1 for line in open('logs/latest_structured.json')
               if 'download' in line and 'ERROR' in line)
print(f'Success rate: {successes/(successes+failures)*100:.1f}%')
"
```

## 🚨 Emergency Debugging

When builds fail completely:

1. **Immediate steps:**
   ```bash
   python analyze_logs.py --errors-only
   python analyze_logs.py --create-debug-package
   ```

2. **Check system resources:**
   ```bash
   df -h                    # Disk space
   free -h                 # Memory
   docker system df        # Docker space usage
   docker ps -a            # Running containers
   ```

3. **Validate environment:**
   ```bash
   python test_build.py    # Run test suite
   docker --version        # Docker availability
   python --version        # Python version
   ```

4. **Manual cleanup:**
   ```bash
   docker system prune -f  # Clean Docker cache
   rm -rf gapps/ magisk*/ ndk/ widevine/  # Clean build artifacts
   ```

The comprehensive logging system ensures you have all the information needed to debug issues and get help from the community! 🎉