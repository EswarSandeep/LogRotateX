"""
rotator.py
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------

import shutil
from datetime import datetime
from pathlib import Path

# -----------------------------------------------------------------------------
# Third Party
# -----------------------------------------------------------------------------

from croniter import croniter

# -----------------------------------------------------------------------------
# Local Imports
# -----------------------------------------------------------------------------

from logrotatorx.exceptions import RotationError

from logrotatorx.logger import get_logger

from logrotatorx.state import (
    get_last_rotation,
    set_last_rotation,
)

from logrotatorx.utils import (
    ensure_directory,
    size_mb,
    timestamp,
)




logger = get_logger()


# -----------------------------------------------------------------------------
# Log Rotation
# -----------------------------------------------------------------------------


def rotate_log(
    log_file: str | Path,
    destination_dir: str | Path,
    rotation_type: str,
    max_size_mb: int | None = None,
    cron_expression: str | None = None,
) -> Path | None:
    """
    Rotate a log according to the configured
    rotation policy.
    """

    source = Path(log_file)

    destination = Path(
        destination_dir
    )

    if not source.exists():
        return None

    if not source.is_file():
        return None

    ensure_directory(
        destination
    )

    if rotation_type == "size":

        return _rotate_size(
            source,
            destination,
            max_size_mb,
        )

    if rotation_type == "hourly":

        return _rotate_hourly(
            source,
            destination,
        )

    if rotation_type == "half_daily":

        return _rotate_half_daily(
            source,
            destination,
        )

    if rotation_type == "daily":

        return _rotate_daily(
            source,
            destination,
        )

    if rotation_type == "cron":

        return _rotate_cron(
            source,
            destination,
            cron_expression,
        )

    raise RotationError(
        f"Unsupported rotation type "
        f"'{rotation_type}'."
    )
    

# -----------------------------------------------------------------------------
# Rotation Policies
# -----------------------------------------------------------------------------

def _rotate_size(
    source: Path,
    destination: Path,
    max_size_mb: int | None,
) -> Path | None:
    """
    Size-based rotation.
    """

    if (
        max_size_mb is None
        or size_mb(source) < max_size_mb
    ):

        return None

    return _perform_rotation(
        source=source,
        destination=destination,
        rotated_name=f"{source.name}.{timestamp()}",
        marker=None,
    )


def _rotate_hourly(
    source: Path,
    destination: Path,
) -> Path | None:
    """
    Hourly rotation.
    """

    marker = datetime.now().strftime(
        "%Y%m%d_%H"
    )

    last_rotation = get_last_rotation(
        str(source)
    )

    if last_rotation == marker:

        return None

    return _perform_rotation(
        source=source,
        destination=destination,
        rotated_name=f"{source.name}.{marker}",
        marker=marker,
    )


def _rotate_half_daily(
    source: Path,
    destination: Path,
) -> Path | None:
    """
    Rotate twice per day.
    """

    now = datetime.now()

    period = (
        "AM"
        if now.hour < 12
        else "PM"
    )

    marker = (
        now.strftime("%Y%m%d")
        + "_"
        + period
    )

    last_rotation = get_last_rotation(
        str(source)
    )

    if last_rotation == marker:

        return None

    return _perform_rotation(
        source=source,
        destination=destination,
        rotated_name=f"{source.name}.{marker}",
        marker=marker,
    )


def _rotate_daily(
    source: Path,
    destination: Path,
) -> Path | None:
    """
    Daily rotation.
    """

    marker = datetime.now().strftime(
        "%Y%m%d"
    )

    last_rotation = get_last_rotation(
        str(source)
    )

    if last_rotation == marker:

        return None

    return _perform_rotation(
        source=source,
        destination=destination,
        rotated_name=f"{source.name}.{marker}",
        marker=marker,
    )




def _rotate_cron(
    source: Path,
    destination: Path,
    cron_expression: str | None,
) -> Path | None:
    """
    Cron-based rotation.

    Rotation occurs once for each scheduled
    execution time, regardless of scheduler
    delays or application restarts.
    """

    if not cron_expression:

        raise RotationError(
            "Missing cron expression."
        )

    now = datetime.now()

    #
    # Determine the most recent scheduled
    # execution time.
    #

    scheduled = croniter(
        cron_expression,
        now,
    ).get_prev(
        datetime,
        start_time=True,
    )

    #
    # Use the scheduled execution time
    # as the persistent marker.
    #

    marker = scheduled.strftime(
        "%Y%m%d_%H%M"
    )

    last_rotation = get_last_rotation(
        str(source)
    )

    #
    # Already rotated for this scheduled
    # execution.
    #

    if last_rotation == marker:

        logger.info(
            "Cron rotation skipped: "
            "already rotated for schedule %s.",
            marker,
        )

        return None

    logger.info(
        "Cron schedule matched: %s",
        marker,
    )

    return _perform_rotation(
        source=source,
        destination=destination,
        rotated_name=f"{source.name}.{marker}",
        marker=marker,
    )




    
# -----------------------------------------------------------------------------
# Rotation Execution
# -----------------------------------------------------------------------------

def _perform_rotation(
    source: Path,
    destination: Path,
    rotated_name: str,
    marker: str | None,
) -> Path:
    """
    Perform copy-truncate rotation.

    Rotation state is updated only after a
    successful rotation.
    """

    rotated_file = (
        destination
        / rotated_name
    )

    logger.info(
        "Rotating %s",
        source,
    )

    try:

        #
        # Copy current log
        #

        shutil.copy2(
            source,
            rotated_file,
        )

        #
        # Copy-truncate
        #

        with source.open(
            "r+b",
        ) as file:

            file.truncate(
                0
            )

        #
        # Persist state only after a
        # successful rotation.
        #

        if marker is not None:

            set_last_rotation(
                str(source),
                marker,
            )

    except Exception as exc:

        if rotated_file.exists():

            try:

                rotated_file.unlink()

            except Exception:

                pass

        raise RotationError(
            f"Failed to rotate '{source}'."
        ) from exc

    logger.info(
        "Rotation completed: %s",
        rotated_file,
    )

    return rotated_file
