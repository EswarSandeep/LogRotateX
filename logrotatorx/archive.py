"""
archive.py

Archive management.
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------

import shutil
from pathlib import Path

# -----------------------------------------------------------------------------
# Local Imports
# -----------------------------------------------------------------------------

from logrotatorx.exceptions import ArchiveError
from logrotatorx.logger import get_logger
from logrotatorx.utils import (
    age_days,
    ensure_directory,
    is_temp_zip,
    is_zip_file,
)

logger = get_logger()


# -----------------------------------------------------------------------------
# Archive Movement
# -----------------------------------------------------------------------------

def move_archives(
    source_dir: str | Path,
    archive_dir: str | Path,
    move_after_days: int,
) -> None:
    """
    Move ZIP files from destination directory to archive directory.
    """

    source = Path(source_dir)
    archive = Path(archive_dir)

    if not source.exists():
        return

    ensure_directory(archive)

    for file in source.iterdir():

        if not file.is_file():
            continue

        if not is_zip_file(file):
            continue

        if is_temp_zip(file):
            continue

        if age_days(file) < move_after_days:
            continue

        destination = archive / file.name

        logger.info(
            "Moving %s -> %s",
            file.name,
            archive,
        )

        try:

            shutil.move(
                str(file),
                str(destination),
            )

        except Exception as exc:

            raise ArchiveError(
                f"Failed to move '{file}' "
                f"to '{destination}'."
            ) from exc

        logger.info(
            "Moved %s",
            file.name,
        )


# -----------------------------------------------------------------------------
# Retention Cleanup
# -----------------------------------------------------------------------------

def cleanup_retention(
    archive_dir: str | Path,
    retention_days: int,
) -> None:
    """
    Delete archived ZIP files older than the retention period.
    """

    archive = Path(archive_dir)

    if not archive.exists():
        return

    for file in archive.iterdir():

        if not file.is_file():
            continue

        if not is_zip_file(file):
            continue

        if is_temp_zip(file):
            continue

        if age_days(file) < retention_days:
            continue

        logger.info(
            "Deleting %s",
            file.name,
        )

        try:

            file.unlink()

        except Exception as exc:

            raise ArchiveError(
                f"Failed to delete '{file}'."
            ) from exc

        logger.info(
            "Deleted %s",
            file.name,
        )
