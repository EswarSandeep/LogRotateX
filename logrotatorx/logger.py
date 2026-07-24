"""
logger.py

Application logging.
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# -----------------------------------------------------------------------------
# Local Imports
# -----------------------------------------------------------------------------

from logrotatorx.constants import (
    DEFAULT_ENCODING,
    DEFAULT_LOG_FORMAT,
)

logger = logging.getLogger("LogRotatorX")


# -----------------------------------------------------------------------------
# Logger Setup
# -----------------------------------------------------------------------------

def setup_logger(
    log_file: str | Path,
    log_level: str,
) -> logging.Logger:
    """
    Configure the application logger.

    Parameters
    ----------
    log_file : str | Path
        Application log file.

    log_level : str
        DEBUG | INFO | WARNING | ERROR | CRITICAL

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """

    #
    # Always update logger level.
    #

    level = getattr(
        logging,
        log_level.upper(),
        logging.INFO,
    )

    logger.setLevel(level)

    #
    # Prevent duplicate handlers.
    #

    if logger.handlers:

        for handler in logger.handlers:

            handler.setLevel(level)

        return logger

    log_file = Path(log_file)

    log_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    formatter = logging.Formatter(
        DEFAULT_LOG_FORMAT
    )

    #
    # File logger
    #

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding=DEFAULT_ENCODING,
    )

    file_handler.setLevel(
        level
    )

    file_handler.setFormatter(
        formatter
    )

    #
    # Console logger
    #

    console_handler = logging.StreamHandler()

    console_handler.setLevel(
        level
    )

    console_handler.setFormatter(
        formatter
    )

    #
    # Logger
    #

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )

    logger.propagate = False

    logger.info(
        "Logger initialized."
    )

    return logger


# -----------------------------------------------------------------------------
# Logger Access
# -----------------------------------------------------------------------------

def get_logger() -> logging.Logger:
    """
    Return application logger.
    """

    return logger