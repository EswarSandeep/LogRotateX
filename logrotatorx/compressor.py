"""
compressor.py

Background ZIP compression.
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------

import os
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# -----------------------------------------------------------------------------
# Local Imports
# -----------------------------------------------------------------------------

from logrotatorx.exceptions import CompressionError
from logrotatorx.logger import get_logger

logger = get_logger()

_executor: ThreadPoolExecutor | None = None


# -----------------------------------------------------------------------------
# Executor Management
# -----------------------------------------------------------------------------

def initialize_compressor(
    workers: int,
) -> None:
    """
    Initialize background compression executor.
    """

    global _executor

    if _executor is not None:
        return

    _executor = ThreadPoolExecutor(
        max_workers=workers,
        thread_name_prefix="zip-worker",
    )

    logger.info(
        "Compression executor initialized with %d worker(s).",
        workers,
    )


def shutdown_compressor() -> None:
    """
    Shutdown compression executor.
    """

    global _executor

    if _executor is None:
        return

    logger.info(
        "Waiting for compression workers..."
    )

    _executor.shutdown(wait=True)

    _executor = None

    logger.info(
        "Compression executor stopped."
    )


# -----------------------------------------------------------------------------
# Compression
# -----------------------------------------------------------------------------

def zip_worker(
    source_file: str | Path,
    zip_level: int,
) -> None:
    """
    Compress a rotated log file.
    """

    source = Path(source_file)

    if not source.exists():

        logger.warning(
            "Compression skipped. File does not exist: %s",
            source,
        )

        return

    tmp_zip = source.with_suffix(
        source.suffix + ".zip.tmp"
    )

    final_zip = source.with_suffix(
        source.suffix + ".zip"
    )

    try:

        logger.info(
            "Compression started: %s",
            source.name,
        )

        with zipfile.ZipFile(
            tmp_zip,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=zip_level,
        ) as archive:

            archive.write(
                source,
                arcname=source.name,
            )

        os.replace(
            tmp_zip,
            final_zip,
        )

        source.unlink()

        logger.info(
            "Compression completed: %s",
            final_zip.name,
        )

    except Exception as exc:

        if tmp_zip.exists():

            try:
                tmp_zip.unlink()
            except Exception:
                pass

        raise CompressionError(
            f"Compression failed for '{source}'."
        ) from exc


def start_zip(
    source_file: str | Path,
    zip_level: int,
):
    """
    Submit background compression task.

    Returns
    -------
    concurrent.futures.Future
    """

    if _executor is None:

        raise CompressionError(
            "Compression executor is not initialized."
        )

    logger.info(
        "Compression queued: %s",
        Path(source_file).name,
    )

    return _executor.submit(
        zip_worker,
        source_file,
        zip_level,
    )
