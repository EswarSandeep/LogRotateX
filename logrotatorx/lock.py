"""
lock.py

Application lock handling.
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------

from pathlib import Path
from typing import TextIO

# -----------------------------------------------------------------------------
# Third Party
# -----------------------------------------------------------------------------

import portalocker

# -----------------------------------------------------------------------------
# Local Imports
# -----------------------------------------------------------------------------

from logrotatorx.constants import (
    DEFAULT_ENCODING,
    DEFAULT_LOCK_FILE_NAME,
)

from logrotatorx.exceptions import LockError
from logrotatorx.logger import get_logger

logger = get_logger()


# -----------------------------------------------------------------------------
# Lock Management
# -----------------------------------------------------------------------------

def acquire_lock(
    state_dir: str | Path,
) -> TextIO | None:
    """
    Acquire an exclusive application lock.

    Parameters
    ----------
    state_dir : str | Path
        Directory used to store the lock file.

    Returns
    -------
    TextIO | None
        Open lock file if acquired,
        otherwise None.
    """

    state_dir = Path(state_dir)

    state_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    lock_path = (
        state_dir
        / DEFAULT_LOCK_FILE_NAME
    )

    try:

        lock_file = open(
            lock_path,
            mode="w",
            encoding=DEFAULT_ENCODING,
        )

    except OSError as exc:

        raise LockError(
            f"Unable to open lock file '{lock_path}'."
        ) from exc

    try:

        portalocker.lock(
            lock_file,
            portalocker.LOCK_EX
            | portalocker.LOCK_NB,
        )

    except portalocker.LockException:

        logger.warning(
            "Another LogRotator instance is already running."
        )

        lock_file.close()

        return None

    logger.info(
        "Application lock acquired."
    )

    return lock_file


def release_lock(
    lock_file: TextIO | None,
) -> None:
    """
    Release application lock.
    """

    if lock_file is None:
        return

    try:

        portalocker.unlock(
            lock_file
        )

    except portalocker.LockException as exc:

        raise LockError(
            "Failed to release application lock."
        ) from exc

    finally:

        try:
            lock_file.close()
        except Exception:
            pass

    logger.info(
        "Application lock released."
    )
