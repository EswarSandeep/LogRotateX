"""
constants.py

Application constants.
"""

# -----------------------------------------------------------------------------
# Runtime Defaults
# -----------------------------------------------------------------------------

DEFAULT_ENCODING = "utf-8"

DEFAULT_LOG_FORMAT = (
    "%(asctime)s "
    "%(levelname)s "
    "%(message)s"
)

# -----------------------------------------------------------------------------
# Default Runtime Names
# -----------------------------------------------------------------------------

DEFAULT_LOG_FILE_NAME = "logrotatorx.log"

DEFAULT_LOCK_FILE_NAME = "logrotatorx.lock"

# -----------------------------------------------------------------------------
# Supported Values
# -----------------------------------------------------------------------------

VALID_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}

VALID_SCHEDULER_TYPES = {
    "interval",
    "cron",
}

VALID_ROTATION_TYPES = (
    "size",
    "hourly",
    "half_daily",
    "daily",
    "cron",
)

