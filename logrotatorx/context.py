"""
context.py

Application runtime context objects.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


Config = dict[str, Any]


# -----------------------------------------------------------------------------
# Application Context
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class AppContext:
    """
    Shared application context.
    """

    config: Config


@dataclass(frozen=True)
class LogContext:
    """
    Represents one configured log.
    """

    #
    # Service name from configuration.
    #

    service_name: str

    #
    # Logical group name from config.yaml.
    #

    log_name: str

    #
    # Actual filename being processed.
    #

    matched_log_name: str

    #
    # Full path.
    #

    file: Path

    destination_dir: Path

    archive_dir: Path

    #
    # Effective rotation policy.
    #

    rotation_type: str

    #
    # Used only for
    # rotation_type == "size"
    #

    max_size_mb: int | None

    #
    # Used only for
    # rotation_type == "cron"
    #

    cron_expression: str | None



# -----------------------------------------------------------------------------
# Runtime Validation
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class ValidationResult:
    """
    Result of runtime validation for one configured log.
    """

    valid: bool

    reason: str | None = None


@dataclass
class ValidationSummary:
    """
    Runtime validation statistics.
    """

    services_configured: int = 0
    services_enabled: int = 0
    services_disabled: int = 0

    logs_configured: int = 0
    logs_enabled: int = 0
    logs_disabled: int = 0


# -----------------------------------------------------------------------------
# Job Summaries
# -----------------------------------------------------------------------------

@dataclass
class RotationSummary:
    """
    Rotation job statistics.
    """

    services_processed: int = 0
    logs_processed: int = 0

    logs_rotated: int = 0
    logs_skipped: int = 0

    compression_queued: int = 0

    errors: int = 0


@dataclass
class JobSummary:
    """
    Generic scheduled job statistics.

    Used by archive, cleanup and future jobs.
    """

    services_processed: int = 0
    logs_processed: int = 0

    successful: int = 0

    errors: int = 0