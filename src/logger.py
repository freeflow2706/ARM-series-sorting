"""
Logging module for ARM DVD Rip Organizer.
Provides centralized logging to console and log file.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class Logger:
    """Logger class for centralized logging."""

    def __init__(self, log_level="INFO", log_dir=None):
        """
        Initialize logger.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_dir: Directory for log file. If None, uses output directory.
        """
        # Fix Windows console encoding for Unicode symbols
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                pass  # Fall back to default if reconfigure fails

        self.log_level = getattr(logging, log_level, logging.INFO)
        self.log_dir = Path(log_dir) if log_dir else Path.cwd() / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger("ARMOrganizer")
        self.logger.setLevel(self.log_level)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler (with UTF-8 encoding for Unicode symbols)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        # Set encoding to UTF-8 to support Unicode symbols (✓, ⚠️, ❌, etc.)
        if hasattr(console_handler, "setEncoding"):
            console_handler.setEncoding("utf-8")
        self.logger.addHandler(console_handler)

        # File handler
        log_file = (
            self.log_dir / f"process_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info(f"Logging initialized. Log file: {log_file}")

    def debug(self, message):
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message):
        """Log info message."""
        self.logger.info(message)

    def warning(self, message):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message):
        """Log error message."""
        self.logger.error(message)

    def critical(self, message):
        """Log critical message."""
        self.logger.critical(message)


# Global logger instance (initialized in main)
_logger_instance = None


def get_logger(log_level="INFO", log_dir=None):
    """
    Get or create global logger instance.

    Args:
        log_level: Logging level
        log_dir: Directory for log file

    Returns:
        Logger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger(log_level, log_dir)
    return _logger_instance
