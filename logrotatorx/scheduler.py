"""
scheduler.py

Application scheduler.
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------

from collections.abc import Callable

# -----------------------------------------------------------------------------
# Third Party
# -----------------------------------------------------------------------------

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# -----------------------------------------------------------------------------
# Local Imports
# -----------------------------------------------------------------------------

from logrotatorx.config import (
    get_archive_scheduler,
    get_cleanup_scheduler,
    get_rotate_scheduler,
    is_archive_enabled,
    is_cleanup_enabled,
    is_rotate_enabled,
)

from logrotatorx.exceptions import SchedulerError
from logrotatorx.logger import get_logger

logger = get_logger()

_scheduler: BackgroundScheduler | None = None


# -----------------------------------------------------------------------------
# Safe Execution
# -----------------------------------------------------------------------------

def safe_execute(
    job_name: str,
    job: Callable[[], None],
) -> None:
    """
    Execute a scheduled job safely.
    """

    try:

        job()

    except Exception:

        logger.exception("%s failed.", job_name)


# -----------------------------------------------------------------------------
# Job Registration
# -----------------------------------------------------------------------------

def register_job(
    scheduler: BackgroundScheduler,
    job_id: str,
    schedule: dict,
    job_name: str,
    job: Callable[[], None],
) -> None:
    """
    Register a scheduler job.
    """

    job_type = schedule["type"]

    if job_type == "interval":

        scheduler.add_job(
            safe_execute,
            trigger="interval",
            seconds=schedule["seconds"],
            id=job_id,
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            args=(job_name, job),
        )

        return

    if job_type == "cron":

        scheduler.add_job(
            safe_execute,
            trigger=CronTrigger.from_crontab(
                schedule["cron"]
            ),
            id=job_id,
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            args=(job_name, job),
        )

        return

    raise SchedulerError(
        f"Unsupported scheduler type '{job_type}'."
    )


# -----------------------------------------------------------------------------
# Scheduler Lifecycle
# -----------------------------------------------------------------------------

def initialize_scheduler(
    *,
    config: dict,
    rotate_job: Callable[[], None],
    archive_job: Callable[[], None],
    cleanup_job: Callable[[], None],
) -> None:
    """
    Initialize APScheduler.
    """

    global _scheduler

    if _scheduler is not None:
        return

    scheduler = BackgroundScheduler()

    if is_rotate_enabled(config):

        register_job(
            scheduler=scheduler,
            job_id="rotate-job",
            schedule=get_rotate_scheduler(config),
            job_name="Rotate Job",
            job=rotate_job,
        )

    if is_archive_enabled(config):

        register_job(
            scheduler=scheduler,
            job_id="archive-job",
            schedule=get_archive_scheduler(config),
            job_name="Archive Job",
            job=archive_job,
        )

    if is_cleanup_enabled(config):

        register_job(
            scheduler=scheduler,
            job_id="cleanup-job",
            schedule=get_cleanup_scheduler(config),
            job_name="Cleanup Job",
            job=cleanup_job,
        )

    _scheduler = scheduler

    logger.info("Scheduler initialized.")


def start_scheduler() -> None:
    """
    Start scheduler.
    """

    if _scheduler is None:

        raise SchedulerError(
            "Scheduler is not initialized."
        )

    _scheduler.start()

    logger.info("Scheduler started.")


def shutdown_scheduler() -> None:
    """
    Shutdown scheduler.
    """

    global _scheduler

    if _scheduler is None:
        return

    logger.info("Stopping scheduler...")

    _scheduler.shutdown(wait=True)

    logger.info("Scheduler stopped.")

    _scheduler = None
