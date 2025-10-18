"""
Logging Utilities
Provides consistent logging across all Sleep Soundscape Synthesizer modules.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "soundscape",
    level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up a logger with consistent formatting.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "soundscape") -> logging.Logger:
    """
    Get an existing logger or create a new one.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger hasn't been set up yet, set it up with defaults
    if not logger.handlers:
        return setup_logger(name)

    return logger


class ProgressLogger:
    """Helper class for logging progress through stages."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or get_logger()

    def stage_start(self, stage_num: int, total_stages: int, stage_name: str):
        """Log the start of a pipeline stage."""
        separator = "=" * 70
        self.logger.info(separator)
        self.logger.info(f"STAGE {stage_num}/{total_stages}: {stage_name.upper()}")
        self.logger.info(separator)

    def stage_complete(self, stage_name: str):
        """Log the completion of a stage."""
        self.logger.info(f"✓ {stage_name} complete!")

    def progress(self, current: int, total: int, item_name: str):
        """Log progress through a sequence of items."""
        self.logger.info(f"[{current:2d}/{total}] {item_name}")

    def section(self, title: str):
        """Log a section header."""
        self.logger.info(f"\n{title}")

    def success(self, message: str):
        """Log a success message."""
        self.logger.info(f"✓ {message}")

    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)


if __name__ == "__main__":
    # Test logging
    print("Testing logger...")

    logger = setup_logger("test", logging.DEBUG)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    print("\nTesting progress logger...")
    progress = ProgressLogger(logger)
    progress.stage_start(1, 3, "Test Stage")
    progress.section("Processing items...")
    for i in range(3):
        progress.progress(i + 1, 3, f"Item {i + 1}")
    progress.success("All items processed")
    progress.stage_complete("Test Stage")
