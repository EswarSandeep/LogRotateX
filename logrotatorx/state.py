"""
state.py

Persistent rotation state.
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------

import json
from pathlib import Path
from threading import Lock

# -----------------------------------------------------------------------------
# Local Imports
# -----------------------------------------------------------------------------

from logrotatorx.logger import get_logger
from logrotatorx.exceptions import StateError


logger = get_logger()

_lock = Lock()

_state: dict = {}

_state_file: Path | None = None


# -----------------------------------------------------------------------------
# Initialization
# -----------------------------------------------------------------------------

def initialize_state(
    state_dir: str | Path,
) -> None:
    """
    Initialize rotation state.
    """

    global _state_file

    state_dir = Path(
        state_dir
    )

    state_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    _state_file = (
        state_dir
        / "rotation_state.json"
    )

    _load()


# -----------------------------------------------------------------------------
# Load
# -----------------------------------------------------------------------------

def _load() -> None:
    """
    Load rotation state.
    """

    global _state

    if (
        _state_file is None
        or not _state_file.exists()
    ):

        _state = {}

        return

    try:

        with _state_file.open(
            "r",
            encoding="utf-8",
        ) as fp:

            _state = json.load(
                fp
            )

    except Exception:

        logger.exception(
            "Failed to load rotation state."
        )

        _state = {}


# -----------------------------------------------------------------------------
# Save
# -----------------------------------------------------------------------------

def _save() -> None:
    """
    Save rotation state.
    """

    if _state_file is None:

        raise StateError(
            "Rotation state is not initialized."
        )

    tmp = Path(
        str(_state_file) + ".tmp"
    )

    try:

        with tmp.open(
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(
                _state,
                fp,
                indent=2,
                sort_keys=True,
            )

        tmp.replace(
            _state_file
        )

    except Exception as exc:

        raise StateError(
            f"Failed to save rotation state '{_state_file}'."
        ) from exc


# -----------------------------------------------------------------------------
# API
# -----------------------------------------------------------------------------

def get_last_rotation(
    log_file: str,
) -> str | None:

    with _lock:

        entry = _state.get(log_file)

        if entry is None:
            return None

        return entry.get(
            "last_rotation"
        )


def set_last_rotation(
    log_file: str,
    marker: str,
) -> None:

    with _lock:

        _state[log_file] = {
            "last_rotation": marker
        }

        _save()