import logging
import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path
from tools.helper import bcolors

class EnhancedLogger:
    """Enhanced logging system for ReDroid Enhanced script"""

    def __init__(self, name="redroid_enhanced", log_dir="logs", log_level=logging.INFO):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create timestamp for this session
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Setup loggers
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Setup formatters
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        self.simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        self.json_formatter = JsonFormatter()

        # Setup handlers
        self._setup_handlers()

        # Session info
        self.session_info = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "platform": sys.platform,
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "arguments": sys.argv,
            "environment": {
                "USER": os.environ.get("USER", "unknown"),
                "HOME": os.environ.get("HOME", "unknown"),
                "PATH": os.environ.get("PATH", "unknown")[:200] + "...",  # Truncate PATH
                "DOCKER_HOST": os.environ.get("DOCKER_HOST", "not_set"),
                "XDG_CACHE_HOME": os.environ.get("XDG_CACHE_HOME", "not_set")
            }
        }

        # Log session start
        self.info("=" * 80)
        self.info(f"Starting ReDroid Enhanced - Session ID: {self.session_id}")
        self.info(f"Platform: {sys.platform} | Python: {sys.version.split()[0]}")
        self.info(f"Working Directory: {os.getcwd()}")
        self.info(f"Arguments: {' '.join(sys.argv)}")
        self.info("=" * 80)

    def _setup_handlers(self):
        """Setup all logging handlers"""

        # Console handler (colored output)
        console_handler = ColoredConsoleHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.simple_formatter)
        self.logger.addHandler(console_handler)

        # Detailed file handler
        detailed_file = self.log_dir / f"detailed_{self.session_id}.log"
        detailed_handler = logging.FileHandler(detailed_file)
        detailed_handler.setLevel(logging.DEBUG)
        detailed_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(detailed_handler)

        # Error file handler
        error_file = self.log_dir / f"errors_{self.session_id}.log"
        error_handler = logging.FileHandler(error_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(error_handler)

        # JSON structured log handler
        json_file = self.log_dir / f"structured_{self.session_id}.json"
        json_handler = logging.FileHandler(json_file)
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(self.json_formatter)
        self.logger.addHandler(json_handler)

        # Latest symlinks (for easy access to most recent logs)
        self._create_latest_symlinks()

    def _create_latest_symlinks(self):
        """Create symlinks to latest log files"""
        symlinks = [
            ("latest_detailed.log", f"detailed_{self.session_id}.log"),
            ("latest_errors.log", f"errors_{self.session_id}.log"),
            ("latest_structured.json", f"structured_{self.session_id}.json")
        ]

        for symlink, target in symlinks:
            symlink_path = self.log_dir / symlink
            target_path = self.log_dir / target

            # Remove existing symlink
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()

            # Create new symlink
            try:
                symlink_path.symlink_to(target)
            except OSError:
                # Fallback for systems that don't support symlinks
                pass

    def debug(self, message, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)

    def info(self, message, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)

    def warning(self, message, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)

    def error(self, message, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)

    def critical(self, message, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra=kwargs)

    def exception(self, message, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, extra=kwargs)

    def log_module_start(self, module_name, version=None):
        """Log module installation start"""
        msg = f"Starting {module_name} installation"
        if version:
            msg += f" (version: {version})"
        self.info(msg, module=module_name, action="start", version=version)

    def log_module_success(self, module_name, details=None):
        """Log successful module installation"""
        msg = f"Successfully installed {module_name}"
        if details:
            msg += f" - {details}"
        self.info(msg, module=module_name, action="success", details=details)

    def log_module_error(self, module_name, error, details=None):
        """Log module installation error"""
        msg = f"Failed to install {module_name}: {error}"
        if details:
            msg += f" - {details}"
        self.error(msg, module=module_name, action="error", error=str(error), details=details)

    def log_download_start(self, url, filename):
        """Log download start"""
        self.info(f"Starting download: {filename}",
                 action="download_start", url=url, filename=filename)

    def log_download_progress(self, filename, progress, total):
        """Log download progress"""
        self.debug(f"Download progress: {filename} - {progress}/{total} bytes",
                  action="download_progress", filename=filename, progress=progress, total=total)

    def log_download_complete(self, filename, size, md5_hash):
        """Log download completion"""
        self.info(f"Download complete: {filename} ({size} bytes, MD5: {md5_hash})",
                 action="download_complete", filename=filename, size=size, md5=md5_hash)

    def log_system_info(self, info_dict):
        """Log system information"""
        self.info("System Information", action="system_info", **info_dict)

    def log_docker_build_start(self, image_name, dockerfile_content):
        """Log Docker build start"""
        self.info(f"Starting Docker build: {image_name}",
                 action="docker_build_start", image_name=image_name,
                 dockerfile_size=len(dockerfile_content))

    def log_docker_build_complete(self, image_name, build_time):
        """Log Docker build completion"""
        self.info(f"Docker build complete: {image_name} (took {build_time:.2f}s)",
                 action="docker_build_complete", image_name=image_name, build_time=build_time)

    def log_command_execution(self, command, returncode, stdout=None, stderr=None):
        """Log command execution"""
        if returncode == 0:
            self.info(f"Command executed successfully: {' '.join(command) if isinstance(command, list) else command}",
                     action="command_success", command=command, returncode=returncode)
        else:
            self.error(f"Command failed: {' '.join(command) if isinstance(command, list) else command}",
                      action="command_error", command=command, returncode=returncode,
                      stdout=stdout, stderr=stderr)

    def create_issue_report(self, error_context=None):
        """Create a comprehensive issue report for debugging"""
        report_file = self.log_dir / f"issue_report_{self.session_id}.json"

        # Collect all relevant information
        report = {
            "session_info": self.session_info,
            "error_context": error_context,
            "system_info": {
                "platform": sys.platform,
                "python_version": sys.version,
                "cwd": os.getcwd(),
                "env_vars": {k: v for k, v in os.environ.items() if not k.upper().endswith('TOKEN')}
            },
            "log_files": {
                "detailed": f"detailed_{self.session_id}.log",
                "errors": f"errors_{self.session_id}.log",
                "structured": f"structured_{self.session_id}.json"
            },
            "generated_at": datetime.now().isoformat()
        }

        # Write report
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        self.info(f"Issue report created: {report_file}")
        return report_file

    def finalize(self):
        """Finalize logging session"""
        end_time = datetime.now()
        session_duration = (end_time - datetime.fromisoformat(self.session_info["start_time"])).total_seconds()

        self.info("=" * 80)
        self.info(f"Session completed - Duration: {session_duration:.2f}s")
        self.info(f"Log files location: {self.log_dir}")
        self.info("=" * 80)


class ColoredConsoleHandler(logging.StreamHandler):
    """Console handler with colored output"""

    COLORS = {
        'DEBUG': bcolors.ENDC,
        'INFO': bcolors.GREEN,
        'WARNING': bcolors.YELLOW,
        'ERROR': bcolors.RED,
        'CRITICAL': bcolors.RED
    }

    def emit(self, record):
        try:
            color = self.COLORS.get(record.levelname, bcolors.ENDC)
            record.levelname = f"{color}{record.levelname}{bcolors.ENDC}"
            super().emit(record)
        except Exception:
            self.handleError(record)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }

        # Add extra fields if present
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'levelname', 'levelno', 'pathname', 'filename',
                              'module', 'lineno', 'funcName', 'created', 'msecs',
                              'relativeCreated', 'thread', 'threadName', 'processName',
                              'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info',
                              'message', 'args']:
                    log_entry[key] = value

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


# Global logger instance
_logger = None

def get_logger(name="redroid_enhanced", log_level=logging.INFO):
    """Get or create global logger instance"""
    global _logger
    if _logger is None:
        _logger = EnhancedLogger(name, log_level=log_level)
    return _logger

def setup_logging(verbose=False, debug=False):
    """Setup logging with different verbosity levels"""
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    return get_logger(log_level=log_level)