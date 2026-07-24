"""
utils.py

Common utility functions.
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------

from datetime import datetime
from pathlib import Path


# -----------------------------------------------------------------------------
# Date & Time
# -----------------------------------------------------------------------------

def timestamp() -> str:
    """
    Return current timestamp.

    Example
    -------
    20260708_235959
    """

    return datetime.now().strftime("%Y%m%d_%H%M%S")


# -----------------------------------------------------------------------------
# File Utilities
# -----------------------------------------------------------------------------

def size_mb(
    file_path: str | Path,
) -> float:
    """
    Return file size in megabytes.
    """

    path = Path(file_path)

    return path.stat().st_size / (1024 * 1024)


def age_days(
    file_path: str | Path,
) -> int:
    """
    Return file age in whole days.
    """

    path = Path(file_path)

    modified = datetime.fromtimestamp(
        path.stat().st_mtime
    )

    return (datetime.now() - modified).days


def ensure_directory(
    directory: str | Path,
) -> None:
    """
    Create directory if it does not already exist.
    """

    Path(directory).mkdir(
        parents=True,
        exist_ok=True,
    )


# -----------------------------------------------------------------------------
# ZIP Utilities
# -----------------------------------------------------------------------------

def is_zip_file(
    file_path: str | Path,
) -> bool:
    """
    Return True if the file has a .zip extension.
    """

    return Path(file_path).suffix.lower() == ".zip"


def is_temp_zip(
    file_path: str | Path,
) -> bool:
    """
    Return True if the file is a temporary ZIP.
    """

    return Path(file_path).name.endswith(".zip.tmp")