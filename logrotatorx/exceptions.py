"""
exceptions.py

Custom exceptions used by LogRotatorX.
"""


class LogRotatorError(Exception):
    """
    Base exception for all LogRotatorX errors.
    """
    pass


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

class ConfigError(LogRotatorError):
    """
    Configuration file is invalid.
    """
    pass


# -----------------------------------------------------------------------------
# Startup / Runtime
# -----------------------------------------------------------------------------

class StartupError(LogRotatorError):
    """
    Application startup failed.
    """
    pass


class RuntimeValidationError(LogRotatorError):
    """
    Runtime environment validation failed.
    """
    pass


class LockError(LogRotatorError):
    """
    Unable to acquire application lock.
    """
    pass


class LoggerError(LogRotatorError):
    """
    Logger initialization failed.
    """
    pass


class SchedulerError(LogRotatorError):
    """
    Scheduler initialization or execution failed.
    """
    pass


class StateError(LogRotatorError):
    """
    Persistent rotation state operation failed.
    """
    pass


# -----------------------------------------------------------------------------
# Log Processing
# -----------------------------------------------------------------------------

class RotationError(LogRotatorError):
    """
    Log rotation failed.
    """
    pass


class CompressionError(LogRotatorError):
    """
    ZIP compression failed.
    """
    pass


class ArchiveError(LogRotatorError):
    """
    Archive movement failed.
    """
    pass


class CleanupError(LogRotatorError):
    """
    Cleanup operation failed.
    """
    pass