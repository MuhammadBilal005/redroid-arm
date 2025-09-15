#!/usr/bin/env python3

import json
import os
import sys
import argparse
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

class LogAnalyzer:
    """Analyze ReDroid Enhanced build logs for debugging"""

    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        if not self.log_dir.exists():
            print(f"❌ Log directory {log_dir} not found")
            sys.exit(1)

    def find_latest_logs(self):
        """Find the latest log files"""
        latest_files = {}

        # Look for latest symlinks first
        symlinks = {
            'detailed': 'latest_detailed.log',
            'errors': 'latest_errors.log',
            'structured': 'latest_structured.json'
        }

        for log_type, symlink in symlinks.items():
            symlink_path = self.log_dir / symlink
            if symlink_path.exists():
                latest_files[log_type] = symlink_path
            else:
                # Fallback: find most recent file
                pattern = f"{log_type}_*.{'json' if log_type == 'structured' else 'log'}"
                files = list(self.log_dir.glob(pattern))
                if files:
                    latest_files[log_type] = max(files, key=os.path.getctime)

        return latest_files

    def find_session_logs(self, session_id):
        """Find logs for a specific session ID"""
        session_files = {}
        patterns = {
            'detailed': f'detailed_{session_id}.log',
            'errors': f'errors_{session_id}.log',
            'structured': f'structured_{session_id}.json'
        }

        for log_type, pattern in patterns.items():
            file_path = self.log_dir / pattern
            if file_path.exists():
                session_files[log_type] = file_path

        return session_files

    def list_sessions(self):
        """List all available sessions"""
        sessions = set()
        pattern = re.compile(r'(detailed|errors|structured)_(\d{8}_\d{6})\.(log|json)')

        for file_path in self.log_dir.iterdir():
            match = pattern.match(file_path.name)
            if match:
                sessions.add(match.group(2))

        return sorted(list(sessions), reverse=True)

    def analyze_errors(self, log_files):
        """Analyze error patterns"""
        print("🔍 Error Analysis")
        print("=" * 50)

        error_file = log_files.get('errors')
        if not error_file or not error_file.exists():
            print("❌ No error log file found")
            return

        error_patterns = defaultdict(list)
        module_errors = defaultdict(list)

        with open(error_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if ' ERROR ' in line:
                    # Extract error type
                    if 'ImportError' in line:
                        error_patterns['Import Errors'].append((line_num, line))
                    elif 'FileNotFoundError' in line:
                        error_patterns['File Not Found'].append((line_num, line))
                    elif 'PermissionError' in line:
                        error_patterns['Permission Errors'].append((line_num, line))
                    elif 'CalledProcessError' in line:
                        error_patterns['Command Failures'].append((line_num, line))
                    elif 'ConnectionError' in line or 'URLError' in line:
                        error_patterns['Network Errors'].append((line_num, line))
                    else:
                        error_patterns['Other Errors'].append((line_num, line))

                    # Extract module name if present
                    module_match = re.search(r'module=([^\\s]+)', line)
                    if module_match:
                        module_errors[module_match.group(1)].append((line_num, line))

        # Display error summary
        if not error_patterns:
            print("✅ No errors found!")
            return

        print(f"📊 Found {sum(len(errors) for errors in error_patterns.values())} errors")
        print()

        for error_type, errors in error_patterns.items():
            if errors:
                print(f"🚨 {error_type} ({len(errors)} occurrences):")
                for line_num, error in errors[-3:]:  # Show last 3 of each type
                    # Extract just the error message
                    error_msg = error.split(' - ')[-1] if ' - ' in error else error
                    print(f"   Line {line_num}: {error_msg}")
                print()

        # Module-specific errors
        if module_errors:
            print("📦 Module-specific errors:")
            for module, errors in module_errors.items():
                print(f"   {module}: {len(errors)} error(s)")
            print()

    def analyze_downloads(self, log_files):
        """Analyze download issues"""
        print("📥 Download Analysis")
        print("=" * 50)

        structured_file = log_files.get('structured')
        if not structured_file or not structured_file.exists():
            print("❌ No structured log file found")
            return

        downloads = {
            'started': [],
            'completed': [],
            'failed': []
        }

        try:
            with open(structured_file, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        action = log_entry.get('action', '')

                        if action == 'download_start':
                            downloads['started'].append(log_entry)
                        elif action == 'download_complete':
                            downloads['completed'].append(log_entry)
                        elif 'download' in action and log_entry.get('level') == 'ERROR':
                            downloads['failed'].append(log_entry)

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"❌ Error reading structured log: {e}")
            return

        print(f"📊 Downloads started: {len(downloads['started'])}")
        print(f"✅ Downloads completed: {len(downloads['completed'])}")
        print(f"❌ Downloads failed: {len(downloads['failed'])}")
        print()

        # Show failed downloads
        if downloads['failed']:
            print("🚨 Failed downloads:")
            for download in downloads['failed']:
                print(f"   {download.get('filename', 'Unknown')}: {download.get('message', 'Unknown error')}")
            print()

        # Show incomplete downloads
        started_files = {d.get('filename') for d in downloads['started']}
        completed_files = {d.get('filename') for d in downloads['completed']}
        incomplete = started_files - completed_files

        if incomplete:
            print("⚠️  Incomplete downloads:")
            for filename in incomplete:
                print(f"   {filename}")
            print()

    def analyze_docker_build(self, log_files):
        """Analyze Docker build issues"""
        print("🐳 Docker Build Analysis")
        print("=" * 50)

        structured_file = log_files.get('structured')
        if not structured_file or not structured_file.exists():
            print("❌ No structured log file found")
            return

        docker_events = []

        try:
            with open(structured_file, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        action = log_entry.get('action', '')

                        if 'docker' in action or 'command' in action:
                            docker_events.append(log_entry)

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"❌ Error reading structured log: {e}")
            return

        if not docker_events:
            print("ℹ️  No Docker build events found")
            return

        for event in docker_events:
            action = event.get('action', '')
            timestamp = event.get('timestamp', '')
            level = event.get('level', '')

            if action == 'docker_build_start':
                print(f"🏁 Build started: {event.get('image_name', 'Unknown')}")
            elif action == 'docker_build_complete':
                build_time = event.get('build_time', 0)
                print(f"✅ Build completed in {build_time:.2f}s: {event.get('image_name', 'Unknown')}")
            elif action == 'command_error':
                print(f"❌ Command failed: {event.get('command', 'Unknown')}")
                if event.get('stderr'):
                    print(f"   Error: {event.get('stderr')}")

    def analyze_modules(self, log_files):
        """Analyze module installation"""
        print("📦 Module Installation Analysis")
        print("=" * 50)

        structured_file = log_files.get('structured')
        if not structured_file or not structured_file.exists():
            print("❌ No structured log file found")
            return

        modules = defaultdict(list)

        try:
            with open(structured_file, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        module = log_entry.get('module')
                        action = log_entry.get('action')

                        if module and action:
                            modules[module].append((action, log_entry))

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"❌ Error reading structured log: {e}")
            return

        if not modules:
            print("ℹ️  No module installation events found")
            return

        print("📊 Module Installation Summary:")
        for module, events in modules.items():
            actions = [event[0] for event in events]
            if 'success' in actions:
                status = "✅ SUCCESS"
            elif 'error' in actions:
                status = "❌ FAILED"
            elif 'start' in actions:
                status = "⚠️  INCOMPLETE"
            else:
                status = "❓ UNKNOWN"

            print(f"   {module}: {status}")

            # Show errors for failed modules
            if 'error' in actions:
                error_events = [event[1] for event in events if event[0] == 'error']
                for error_event in error_events:
                    error_msg = error_event.get('error', 'Unknown error')
                    print(f"      Error: {error_msg}")

    def generate_summary(self, log_files):
        """Generate a summary report"""
        print("📋 Build Summary")
        print("=" * 50)

        # Check if build completed successfully
        detailed_file = log_files.get('detailed')
        if detailed_file and detailed_file.exists():
            with open(detailed_file, 'r') as f:
                content = f.read()
                if "BUILD COMPLETED SUCCESSFULLY" in content:
                    print("✅ Build Status: SUCCESS")
                elif "BUILD FAILED" in content:
                    print("❌ Build Status: FAILED")
                else:
                    print("⚠️  Build Status: INCOMPLETE")

        # Extract basic info from structured log
        structured_file = log_files.get('structured')
        if structured_file and structured_file.exists():
            try:
                with open(structured_file, 'r') as f:
                    first_line = f.readline()
                    if first_line:
                        first_entry = json.loads(first_line.strip())
                        if 'android_version' in first_entry:
                            print(f"🤖 Android Version: {first_entry.get('android_version')}")
                        if 'device_profile' in first_entry:
                            print(f"📱 Device Profile: {first_entry.get('device_profile')}")
                        if 'container_type' in first_entry:
                            print(f"🐳 Container: {first_entry.get('container_type')}")

            except:
                pass

        print()

    def create_debug_package(self, session_id=None):
        """Create a debug package for sharing"""
        if session_id:
            log_files = self.find_session_logs(session_id)
            package_name = f"debug_package_{session_id}.txt"
        else:
            log_files = self.find_latest_logs()
            package_name = f"debug_package_latest.txt"

        if not log_files:
            print("❌ No log files found for debug package")
            return

        package_path = self.log_dir / package_name

        with open(package_path, 'w') as f:
            f.write("ReDroid Enhanced Debug Package\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            if session_id:
                f.write(f"Session ID: {session_id}\n")
            f.write("\n")

            # Include all log files
            for log_type, log_file in log_files.items():
                f.write(f"\n{'='*20} {log_type.upper()} LOG {'='*20}\n")
                try:
                    with open(log_file, 'r') as log_f:
                        f.write(log_f.read())
                except Exception as e:
                    f.write(f"Error reading {log_file}: {e}\n")

        print(f"📦 Debug package created: {package_path}")
        print(f"📧 Share this file when reporting issues")
        return package_path

    def analyze_all(self, session_id=None):
        """Run all analyses"""
        if session_id:
            log_files = self.find_session_logs(session_id)
            print(f"🔍 Analyzing session: {session_id}")
        else:
            log_files = self.find_latest_logs()
            print("🔍 Analyzing latest logs")

        if not log_files:
            print("❌ No log files found")
            return

        print(f"📁 Log directory: {self.log_dir.absolute()}")
        print()

        self.generate_summary(log_files)
        self.analyze_errors(log_files)
        self.analyze_downloads(log_files)
        self.analyze_modules(log_files)
        self.analyze_docker_build(log_files)

        print("💡 Recommendations:")
        print("=" * 50)
        print("1. If downloads failed, check internet connection and retry")
        print("2. If permissions errors, check file ownership and Docker permissions")
        print("3. If module errors, verify all required files are present")
        print("4. For Docker build failures, ensure Docker is running and has sufficient resources")
        print("5. Use --debug flag for more detailed logging in future runs")
        print()

def main():
    parser = argparse.ArgumentParser(description="Analyze ReDroid Enhanced build logs")
    parser.add_argument('--log-dir', default='logs', help='Log directory path')
    parser.add_argument('--session', help='Analyze specific session ID')
    parser.add_argument('--list-sessions', action='store_true', help='List all available sessions')
    parser.add_argument('--create-debug-package', action='store_true', help='Create debug package for sharing')
    parser.add_argument('--errors-only', action='store_true', help='Show only error analysis')

    args = parser.parse_args()

    analyzer = LogAnalyzer(args.log_dir)

    if args.list_sessions:
        sessions = analyzer.list_sessions()
        if sessions:
            print("📅 Available sessions:")
            for session in sessions:
                print(f"   {session}")
        else:
            print("❌ No sessions found")
        return

    if args.create_debug_package:
        analyzer.create_debug_package(args.session)
        return

    if args.errors_only:
        log_files = analyzer.find_session_logs(args.session) if args.session else analyzer.find_latest_logs()
        analyzer.analyze_errors(log_files)
        return

    analyzer.analyze_all(args.session)

if __name__ == "__main__":
    main()