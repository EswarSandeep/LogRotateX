"""
processor.py

Coordinates log processing.
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------

from collections.abc import Callable
from fnmatch import fnmatch
import glob
from pathlib import Path




# -----------------------------------------------------------------------------
# Local Imports
# -----------------------------------------------------------------------------

from logrotatorx.archive import (
    cleanup_retention,
    move_archives,
)

from logrotatorx.compressor import start_zip

from logrotatorx.config import (
    get_compress,
    get_effective_rotation,
    get_move_after_days,
    get_retention_days,
    get_services,
    get_zip_level,
)

from logrotatorx.context import (
    AppContext,
    JobSummary,
    LogContext,
    RotationSummary,
)

from logrotatorx.logger import get_logger

from logrotatorx.rotator import rotate_log

logger = get_logger()


# -----------------------------------------------------------------------------
# Common Processing
# -----------------------------------------------------------------------------

               
# -----------------------------------------------------------------------------
# Common Processing
# -----------------------------------------------------------------------------


def process_all_logs(
    app_context: AppContext,
    callback: Callable,
    summary,
) -> None:
    """
    Iterate through all configured logs.

    Supports both:

    - exact log files
    - wildcard patterns

    Wildcard expansion occurs at every
    scheduled execution.
    """

    config = app_context.config

    services = get_services(
        config
    )

    if not services:

        logger.info(
            "No enabled log sources."
        )

        return

    for service in services:

        if not service.get(
            "enabled",
            True,
        ):
            continue

        summary.services_processed += 1

        service_name = service["name"]

        for log in service["logs"]:

            files = _expand_log_files(
                log
            )

            if not files:

                if glob.has_magic(
                    log["file"]
                ):

                    logger.info(
                        "[%s/%s] No files currently match '%s'.",
                        service_name,
                        log["name"],
                        log["file"],
                    )

                continue

            #
            # Resolve effective rotation policy
            #

            rotation = get_effective_rotation(
                config,
                log,
            )

            for file_path in files:

                summary.logs_processed += 1

                context = LogContext(
                    service_name=service_name,
                    log_name=log["name"],
                    matched_log_name=file_path.name,
                    file=file_path,
                    destination_dir=Path(
                        log["destination_dir"]
                        ),
                    archive_dir=Path(
                        log["archive_dir"]
                        ),
                    rotation_type=rotation["type"],
                    max_size_mb=rotation.get(
                        "max_size_mb",
                        ),
                    cron_expression=rotation.get(
                        "cron",
                        ),
                )
                
                
                
                
                
                
                    

                try:

                    callback(
                        app_context,
                        context,
                        summary,
                    )

                except Exception:

                    summary.errors += 1

                    logger.exception(
                        "[%s/%s] Processing failed.",
                        context.service_name,
                        context.log_name,
                    )


# -----------------------------------------------------------------------------
# File Expansion
# -----------------------------------------------------------------------------

def _expand_log_files(
    log: dict,
) -> list[Path]:
    """
    Expand configured log file(s).

    Supports:

    - Exact file
    - Wildcard pattern

    Optional:

    - exclude
    """

    file_pattern = log["file"]

    #
    # Exact file
    #

    if not glob.has_magic(
        file_pattern
    ):

        path = Path(
            file_pattern
        )

        if path.exists():

            return [path]

        return []

    #
    # Wildcard
    #

    matched_files = sorted(

        Path(path)

        for path in glob.glob(
            file_pattern,
            recursive=True,
        )

        if Path(path).is_file()

    )

    exclude_patterns = log.get(
        "exclude",
        [],
    )

    if not exclude_patterns:

        return matched_files

    filtered_files = []

    for file_path in matched_files:

        excluded = False

        for pattern in exclude_patterns:

            if fnmatch(
                file_path.name,
                pattern,
            ):

                excluded = True

                logger.info(
                    "Excluded: %s",
                    file_path.name,
                )

                break

        if not excluded:

            filtered_files.append(
                file_path
            )

    return filtered_files












# -----------------------------------------------------------------------------
# Rotation
# -----------------------------------------------------------------------------


def process_rotation(
    app_context: AppContext,
    log_context: LogContext,
    summary: RotationSummary,
) -> None:
    """
    Rotate one configured log.
    """

    config = app_context.config

    logger.info(
        "[%s/%s] Rotation started.",
        log_context.service_name,
        log_context.log_name,
    )

    rotated_file = rotate_log(
        log_file=log_context.file,
        destination_dir=log_context.destination_dir,
        rotation_type=log_context.rotation_type,
        max_size_mb=log_context.max_size_mb,
        cron_expression=log_context.cron_expression,
    )

    if rotated_file is None:

        summary.logs_skipped += 1

        logger.info(
            "[%s/%s] Rotation skipped.",
            log_context.service_name,
            log_context.log_name,
        )

        return

    summary.logs_rotated += 1

    if get_compress(config):

        start_zip(
            source_file=rotated_file,
            zip_level=get_zip_level(config),
        )

        summary.compression_queued += 1

        logger.info(
            "[%s/%s] Compression queued.",
            log_context.service_name,
            log_context.log_name,
        )

    logger.info(
        "[%s/%s] Rotation completed.",
        log_context.service_name,
        log_context.log_name,
    )




# -----------------------------------------------------------------------------
# Archive
# -----------------------------------------------------------------------------

def process_archive(
    app_context: AppContext,
    log_context: LogContext,
    summary: JobSummary,
) -> None:
    """
    Move ZIP files from destination directory to archive directory.
    """

    config = app_context.config

    if not log_context.destination_dir.exists():
        return

    logger.info(
        "[%s/%s] Archive started.",
        log_context.service_name,
        log_context.log_name,
    )

    move_archives(
        source_dir=log_context.destination_dir,
        archive_dir=log_context.archive_dir,
        move_after_days=get_move_after_days(config),
    )

    summary.successful += 1

    logger.info(
        "[%s/%s] Archive completed.",
        log_context.service_name,
        log_context.log_name,
    )


# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------

def process_cleanup(
    app_context: AppContext,
    log_context: LogContext,
    summary: JobSummary,
) -> None:
    """
    Delete archived ZIP files beyond the configured retention period.
    """

    config = app_context.config

    if not log_context.archive_dir.exists():
        return

    logger.info(
        "[%s/%s] Cleanup started.",
        log_context.service_name,
        log_context.log_name,
    )

    cleanup_retention(
        archive_dir=log_context.archive_dir,
        retention_days=get_retention_days(config),
    )

    summary.successful += 1

    logger.info(
        "[%s/%s] Cleanup completed.",
        log_context.service_name,
        log_context.log_name,
    )
    
# -----------------------------------------------------------------------------
# Scheduler Jobs
# -----------------------------------------------------------------------------
def rotate_job(
    app_context: AppContext,
) -> None:
    """
    Execute rotation job.
    """

    logger.info(
        "Rotation job started."
    )

    summary = RotationSummary()

    process_all_logs(
        app_context,
        process_rotation,
        summary,
    )

    #
    # Print summary only when
    # actual work was performed.
    #

    if (
        summary.logs_rotated > 0
        or summary.compression_queued > 0
        or summary.errors > 0
    ):

        _print_rotation_summary(
            summary,
        )

    logger.info(
        "Rotation job completed."
    )

def archive_job(
    app_context: AppContext,
) -> None:
    """
    Execute archive job.
    """

    logger.info(
        "Archive job started."
    )

    summary = JobSummary()

    process_all_logs(
        app_context,
        process_archive,
        summary,
    )

    #
    # Print summary only when
    # files were archived.
    #

    if (
        summary.successful > 0
        or summary.errors > 0
    ):

        _print_archive_summary(
            summary,
        )

    logger.info(
        "Archive job completed."
    )

def cleanup_job(
    app_context: AppContext,
) -> None:
    """
    Execute cleanup job.
    """

    logger.info(
        "Cleanup job started."
    )

    summary = JobSummary()

    process_all_logs(
        app_context,
        process_cleanup,
        summary,
    )

    #
    # Print summary only when
    # files were deleted.
    #

    if (
        summary.successful > 0
        or summary.errors > 0
    ):

        _print_cleanup_summary(
            summary,
        )

    logger.info(
        "Cleanup job completed."
    )


# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------

def _print_rotation_summary(
    summary: RotationSummary,
) -> None:
    """
    Print rotation summary.
    """

    logger.info("=" * 60)
    logger.info("Rotation Summary")
    logger.info("=" * 60)

    logger.info(
        "Services Processed : %d",
        summary.services_processed,
    )

    logger.info(
        "Logs Processed     : %d",
        summary.logs_processed,
    )

    logger.info(
        "Logs Rotated       : %d",
        summary.logs_rotated,
    )

    logger.info(
        "Logs Skipped       : %d",
        summary.logs_skipped,
    )

    logger.info(
        "Compression Queued : %d",
        summary.compression_queued,
    )

    logger.info(
        "Errors             : %d",
        summary.errors,
    )

    logger.info("=" * 60)


def _print_archive_summary(
    summary: JobSummary,
) -> None:
    """
    Print archive summary.
    """

    logger.info("=" * 60)
    logger.info("Archive Summary")
    logger.info("=" * 60)

    logger.info(
        "Services Processed : %d",
        summary.services_processed,
    )

    logger.info(
        "Logs Processed     : %d",
        summary.logs_processed,
    )

    logger.info(
        "Successful         : %d",
        summary.successful,
    )

    logger.info(
        "Errors             : %d",
        summary.errors,
    )

    logger.info("=" * 60)


def _print_cleanup_summary(
    summary: JobSummary,
) -> None:
    """
    Print cleanup summary.
    """

    logger.info("=" * 60)
    logger.info("Cleanup Summary")
    logger.info("=" * 60)

    logger.info(
        "Services Processed : %d",
        summary.services_processed,
    )

    logger.info(
        "Logs Processed     : %d",
        summary.logs_processed,
    )

    logger.info(
        "Successful         : %d",
        summary.successful,
    )

    logger.info(
        "Errors             : %d",
        summary.errors,
    )

    logger.info("=" * 60)
