"""
Logging Configuration for Autonomous Scientific Agent
=====================================================
Sets up loguru-based logging with console and file output.
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "1 week",
    enable_console: bool = True
):
    """
    Configure and return a logger instance with file and console handlers.

    Args:
        log_level: Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses logs/app.log in project root
        rotation: When to rotate log file (e.g., "10 MB", "1 day")
        retention: How long to keep old log files (e.g., "1 week", "30 days")
        enable_console: Whether to log to console (default: True)

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logger(log_level="DEBUG")
        >>> logger.info("Application started")
        >>> logger.error("An error occurred", exc_info=True)
    """
    # Remove default handler
    logger.remove()

    # Add console handler with color formatting
    if enable_console:
        logger.add(
            sys.stderr,
            level=log_level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            colorize=True,
        )

    # Determine log file path
    if log_file is None:
        # Find project root (look for logs/ directory)
        current_dir = Path(__file__).resolve().parent
        for parent in [current_dir] + list(current_dir.parents):
            logs_dir = parent / "logs"
            if logs_dir.exists():
                log_file = str(logs_dir / "app.log")
                break

        # If logs directory doesn't exist, create it
        if log_file is None:
            logs_dir = current_dir.parents[1] / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            log_file = str(logs_dir / "app.log")

    # Add file handler with rotation
    logger.add(
        log_file,
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
        rotation=rotation,
        retention=retention,
        compression="zip",  # Compress rotated logs
        enqueue=True,  # Thread-safe logging
    )

    logger.info(f"Logger initialized - Level: {log_level}, File: {log_file}")
    return logger


def get_logger():
    """
    Get the configured logger instance.

    Returns:
        The global logger instance

    Example:
        >>> from src.utils.logger import get_logger
        >>> logger = get_logger()
        >>> logger.debug("Debug message")
    """
    return logger
