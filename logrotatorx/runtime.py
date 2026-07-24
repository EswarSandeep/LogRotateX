"""
runtime.py

Runtime environment validation.
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------

import copy
import glob
import platform
from pathlib import Path

# -----------------------------------------------------------------------------
# Local Imports
# -----------------------------------------------------------------------------

from logrotatorx.config import get_services

from logrotatorx.context import (
    ValidationResult,
    ValidationSummary,
)

from logrotatorx.logger import get_logger

logger = get_logger()


# -----------------------------------------------------------------------------
# Runtime Validation
# -----------------------------------------------------------------------------

def validate_runtime(
    config: dict,
) -> dict:
    """
    Validate runtime configuration.

    Wildcard log patterns are NOT expanded here.

    Runtime validation verifies that:

    * configured directories exist
    * exact log files exist
    * wildcard parent directories exist

    Missing log files do not terminate
    the application.
    """

    logger.info(
        "Runtime validation started."
    )

    validated_config = copy.deepcopy(
        config
    )

    summary = ValidationSummary()

    services = []

    for service in get_services(
        validated_config
    ):

        validated_service = _validate_service(
            service,
            summary,
        )

        if validated_service is not None:

            services.append(
                validated_service
            )

    os_name = platform.system().lower()

    if os_name.startswith(
        "win"
    ):

        validated_config[
            "services"
        ][
            "windows"
        ] = services

    else:

        validated_config[
            "services"
        ][
            "linux"
        ] = services

    _print_summary(
        summary
    )

    if summary.services_enabled == 0:

        logger.warning(
            "No valid services currently available."
        )

    logger.info(
        "Runtime validation completed."
    )

    return validated_config





# -----------------------------------------------------------------------------
# Internal Helpers
# -----------------------------------------------------------------------------

def _validate_service(
    service: dict,
    summary: ValidationSummary,
) -> dict | None:
    """
    Validate one configured service.

    Wildcard patterns are validated but
    NOT expanded.

    Expansion happens during scheduled
    processing.
    """

    summary.services_configured += 1

    service_name = service["name"]

    validated_logs = []

    for log in service["logs"]:

        summary.logs_configured += 1

        result = _validate_log(
            service_name,
            log,
        )

        if result.valid:

            validated_logs.append(
                log
            )

            summary.logs_enabled += 1

        else:

            summary.logs_disabled += 1

            logger.warning(
                "[%s/%s] Disabled. Reason: %s",
                service_name,
                log["name"],
                result.reason,
            )

    if not validated_logs:

        summary.services_disabled += 1

        logger.warning(
            "[%s] No valid logs currently available.",
            service_name,
        )

        return None

    validated_service = service.copy()

    validated_service["logs"] = validated_logs

    summary.services_enabled += 1

    return validated_service



def _validate_log(
    service_name: str,
    log: dict,
) -> ValidationResult:
    """
    Validate one configured log.

    Exact files must exist.

    Wildcard patterns only require the
    parent directory to exist.
    """

    log_name = log["name"]

    log_path = Path(
        log["file"]
    )

    #
    # Wildcard pattern
    #

    if glob.has_magic(
        str(log_path)
    ):

        parent_dir = log_path.parent

        result = _validate_path(
            service_name,
            log_name,
            "Log directory",
            parent_dir,
        )

        if not result.valid:
            return result

        if not parent_dir.is_dir():

            logger.warning(
                "[%s/%s] Log directory is not a directory (%s)",
                service_name,
                log_name,
                parent_dir,
            )

            return ValidationResult(
                valid=False,
                reason="Invalid log directory",
            )

    #
    # Exact file
    #

    else:

        result = _validate_path(
            service_name,
            log_name,
            "Log file",
            log_path,
        )

        if not result.valid:
            return result

        if not log_path.is_file():

            logger.warning(
                "[%s/%s] Log file is not a regular file (%s)",
                service_name,
                log_name,
                log_path,
            )

            return ValidationResult(
                valid=False,
                reason="Invalid log file",
            )

    #
    # Destination directory
    #

    destination_dir = Path(
        log["destination_dir"]
    )

    result = _validate_path(
        service_name,
        log_name,
        "Destination directory",
        destination_dir,
    )

    if not result.valid:
        return result

    if not destination_dir.is_dir():

        logger.warning(
            "[%s/%s] Destination is not a directory (%s)",
            service_name,
            log_name,
            destination_dir,
        )

        return ValidationResult(
            valid=False,
            reason="Invalid destination directory",
        )

    #
    # Archive directory
    #

    archive_dir = Path(
        log["archive_dir"]
    )

    result = _validate_path(
        service_name,
        log_name,
        "Archive directory",
        archive_dir,
    )

    if not result.valid:
        return result

    if not archive_dir.is_dir():

        logger.warning(
            "[%s/%s] Archive path is not a directory (%s)",
            service_name,
            log_name,
            archive_dir,
        )

        return ValidationResult(
            valid=False,
            reason="Invalid archive directory",
        )

    logger.info(
        "[%s/%s] Runtime validation passed.",
        service_name,
        log_name,
    )

    return ValidationResult(
        valid=True,
    )





def _validate_path(
    service_name: str,
    log_name: str,
    label: str,
    path: Path,
) -> ValidationResult:
    """
    Validate a filesystem path.
    """

    if path.exists():

        logger.info(
            "[%s/%s] %s found.",
            service_name,
            log_name,
            label,
        )

        return ValidationResult(
            valid=True,
        )

    logger.warning(
        "[%s/%s] %s not found: %s",
        service_name,
        log_name,
        label,
        path,
    )

    return ValidationResult(
        valid=False,
        reason=f"{label} not found",
    )


def _print_summary(
    summary: ValidationSummary,
) -> None:
    """
    Print runtime validation summary.
    """

    logger.info("=" * 60)
    logger.info("Runtime Validation Summary")
    logger.info("=" * 60)

    logger.info(
        "Services Configured : %d",
        summary.services_configured,
    )

    logger.info(
        "Services Enabled    : %d",
        summary.services_enabled,
    )

    logger.info(
        "Services Disabled   : %d",
        summary.services_disabled,
    )

    logger.info("-" * 60)

    logger.info(
        "Logs Configured     : %d",
        summary.logs_configured,
    )

    logger.info(
        "Logs Enabled        : %d",
        summary.logs_enabled,
    )

    logger.info(
        "Logs Disabled       : %d",
        summary.logs_disabled,
    )

    logger.info("=" * 60)


