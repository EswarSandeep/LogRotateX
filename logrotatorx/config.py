"""
config.py

Loads and validates config.yaml.
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------

from pathlib import Path
import platform

# -----------------------------------------------------------------------------
# Third Party
# -----------------------------------------------------------------------------

import yaml

# -----------------------------------------------------------------------------
# Local Imports
# -----------------------------------------------------------------------------

from logrotatorx.constants import VALID_LOG_LEVELS

from logrotatorx.exceptions import ConfigError



from logrotatorx.constants import (
    VALID_LOG_LEVELS,
    VALID_ROTATION_TYPES,
)



# -----------------------------------------------------------------------------
# Configuration Loading
# -----------------------------------------------------------------------------

def load_config(
    config_file: str | Path,
) -> dict:
    """
    Load configuration from a YAML file.

    Parameters
    ----------
    config_file : str | Path
        Path to config.yaml.

    Returns
    -------
    dict

    Raises
    ------
    ConfigError
    """

    config_file = Path(config_file)

    try:

        with config_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            config = yaml.safe_load(file)

    except FileNotFoundError:

        raise ConfigError(
            f"Configuration file not found: {config_file}"
        )

    except yaml.YAMLError as exc:

        raise ConfigError(
            f"Invalid YAML: {exc}"
        )

    if not isinstance(config, dict):

        raise ConfigError(
            "Invalid configuration format."
        )

    return config


# -----------------------------------------------------------------------------
# Configuration Validation
# -----------------------------------------------------------------------------

def validate_config(
    config: dict,
) -> None:
    """
    Validate complete configuration.
    """

    validate_application(config)

    validate_paths(config)

    validate_defaults(config)

    validate_scheduler(config)

    validate_services(config)


def validate_application(
    config: dict,
) -> None:
    """
    Validate application section.
    """

    application = config.get("application")

    if application is None:

        raise ConfigError(
            "Missing 'application' section."
        )

    if not application.get("name"):

        raise ConfigError(
            "application.name missing."
        )

    if not application.get("version"):

        raise ConfigError(
            "application.version missing."
        )


def validate_paths(
    config: dict,
) -> None:
    """
    Validate runtime paths.
    """

    paths = config.get("paths")

    if paths is None:

        raise ConfigError(
            "Missing 'paths' section."
        )

    if not paths.get("log_file"):

        raise ConfigError(
            "paths.log_file missing."
        )

    if not paths.get("state_dir"):

        raise ConfigError(
            "paths.state_dir missing."
        )



def validate_defaults(
    config: dict,
) -> None:
    """
    Validate defaults section.
    """

    defaults = config.get("defaults")

    if defaults is None:

        raise ConfigError(
            "Missing 'defaults' section."
        )

    #
    # Rotation
    #

    rotation = defaults.get(
        "rotation"
    )

    if rotation is None:

        raise ConfigError(
            "defaults.rotation missing."
        )

    if not isinstance(
        rotation,
        dict,
    ):

        raise ConfigError(
            "defaults.rotation must be an object."
        )

    rotation_type = rotation.get(
        "type"
    )

    if rotation_type not in VALID_ROTATION_TYPES:

        raise ConfigError(
            "defaults.rotation.type must be "
            "'size', 'hourly', 'daily', 'half_daily' or 'cron'."
        )

    if rotation_type == "size":

        value = rotation.get(
            "max_size_mb"
        )

        if (
            not isinstance(
                value,
                int,
            )
            or value <= 0
        ):

            raise ConfigError(
                "defaults.rotation.max_size_mb "
                "must be greater than zero."
            )
    elif rotation_type == "cron":
        cron = rotation.get(
            "cron"
            )
        if (
            not isinstance(
                cron,
                str,
                )
            or not cron.strip()
            ):
            raise ConfigError(
                "defaults.rotation.cron is required "
                "when rotation.type='cron'."
            )

    #
    # Compression
    #

    value = defaults.get(
        "compress"
    )

    if not isinstance(
        value,
        bool,
    ):

        raise ConfigError(
            "defaults.compress must be true/false."
        )

    #
    # ZIP level
    #

    value = defaults.get(
        "zip_level"
    )

    if not isinstance(
        value,
        int,
    ):

        raise ConfigError(
            "defaults.zip_level must be an integer."
        )

    if value < 0 or value > 9:

        raise ConfigError(
            "defaults.zip_level must be between 0 and 9."
        )

    #
    # Archive
    #

    value = defaults.get(
        "move_after_days"
    )

    if (
        not isinstance(
            value,
            int,
        )
        or value < 0
    ):

        raise ConfigError(
            "defaults.move_after_days "
            "must be zero or greater."
        )

    #
    # Retention
    #

    value = defaults.get(
        "retention_days"
    )

    if (
        not isinstance(
            value,
            int,
        )
        or value <= 0
    ):

        raise ConfigError(
            "defaults.retention_days "
            "must be greater than zero."
        )

    #
    # Compression workers
    #

    value = defaults.get(
        "compression_workers"
    )

    if (
        not isinstance(
            value,
            int,
        )
        or value <= 0
    ):

        raise ConfigError(
            "defaults.compression_workers "
            "must be greater than zero."
        )

    #
    # Log level
    #

    level = str(
        defaults.get(
            "log_level",
            "",
        )
    ).upper()

    if level not in VALID_LOG_LEVELS:

        raise ConfigError(
            f"Invalid log level '{level}'."
        )






def validate_scheduler(
    config: dict,
) -> None:
    """
    Validate scheduler section.
    """

    scheduler = config.get("scheduler")

    if scheduler is None:

        raise ConfigError(
            "Missing 'scheduler' section."
        )

    for job in (
        "rotate",
        "archive",
        "cleanup",
    ):

        if job not in scheduler:

            raise ConfigError(
                f"Missing scheduler.{job}"
            )

        data = scheduler[job]

        enabled = data.get(
            "enabled",
            True,
        )

        if not isinstance(enabled, bool):

            raise ConfigError(
                f"scheduler.{job}.enabled must be true/false."
            )

        job_type = data.get("type")

        if job_type not in (
            "interval",
            "cron",
        ):

            raise ConfigError(
                f"scheduler.{job}.type must be "
                "'interval' or 'cron'."
            )

        if job_type == "interval":

            seconds = data.get("seconds")

            if not isinstance(seconds, int):

                raise ConfigError(
                    f"scheduler.{job}.seconds "
                    "must be an integer."
                )

            if seconds <= 0:

                raise ConfigError(
                    f"scheduler.{job}.seconds "
                    "must be greater than zero."
                )

        else:

            cron = data.get("cron")

            if not cron:

                raise ConfigError(
                    f"Missing scheduler.{job}.cron"
                )



def validate_services(
    config: dict,
) -> None:
    """
    Validate services section.
    """

    services = config.get(
        "services"
    )

    if services is None:

        raise ConfigError(
            "Missing 'services' section."
        )

    os_name = platform.system().lower()

    if os_name.startswith(
        "win"
    ):

        service_list = services.get(
            "windows",
            [],
        )

    else:

        service_list = services.get(
            "linux",
            [],
        )

    if not isinstance(
        service_list,
        list,
    ):

        raise ConfigError(
            "services must be a list."
        )

    for service in service_list:

        service_name = service.get(
            "name",
            "<unknown>",
        )

        logs = service.get(
            "logs"
        )

        if not logs:

            raise ConfigError(
                f"{service_name}: "
                "No logs configured."
            )

        for log in logs:

            #
            # Required fields
            #

            for field in (

                "name",
                "file",
                "destination_dir",
                "archive_dir",

            ):

                value = log.get(
                    field
                )

                if (
                    value is None
                    or str(value).strip() == ""
                ):

                    raise ConfigError(
                        f"{service_name}: "
                        f"Missing '{field}'."
                    )

            #
            # Exclude patterns (optional)
            #

            exclude = log.get(
                "exclude"
            )

            if exclude is not None:

                if not isinstance(
                    exclude,
                    list,
                ):

                    raise ConfigError(
                        f"{service_name}: "
                        "exclude must be a list."
                    )

                for pattern in exclude:

                    if (
                        not isinstance(
                            pattern,
                            str,
                        )
                        or not pattern.strip()
                    ):

                        raise ConfigError(
                            f"{service_name}: "
                            "exclude entries must be non-empty strings."
                        )

            #
            # Rotation Override (optional)
            #

            rotation = log.get(
                "rotation"
            )

            if rotation is not None:

                if not isinstance(
                    rotation,
                    dict,
                ):

                    raise ConfigError(
                        f"{service_name}: "
                        "rotation must be an object."
                    )

                rotation_type = rotation.get(
                    "type"
                )

                if rotation_type is not None:

                    if rotation_type not in VALID_ROTATION_TYPES:

                        raise ConfigError(
                            f"{service_name}: "
                            "rotation.type must be "
                            "'size', 'daily' or "
                            "'half_daily'."
                        )

                if "max_size_mb" in rotation:

                    value = rotation[
                        "max_size_mb"
                    ]

                    if (
                        not isinstance(
                            value,
                            int,
                        )
                        or value <= 0
                    ):

                        raise ConfigError(
                            f"{service_name}: "
                            "rotation.max_size_mb "
                            "must be greater than zero."
                        )
                        
                if rotation_type == "cron":
                    cron = rotation.get(
                        "cron"
                        )
                    if (
                        not isinstance(
                            cron,
                            str,
                            )
                        or not cron.strip()
                        ):
                        raise ConfigError(
                            f"{service_name}: "
                            "rotation.cron is required "
                            "when rotation.type='cron'."
                        )





# -----------------------------------------------------------------------------
# Getters
# -----------------------------------------------------------------------------

def get_application(
    config: dict,
) -> dict:
    """
    Return application section.
    """

    return config["application"]


def get_paths(
    config: dict,
) -> dict:
    """
    Return runtime paths section.
    """

    return config["paths"]


def get_defaults(
    config: dict,
) -> dict:
    """
    Return defaults section.
    """

    return config["defaults"]


def get_scheduler(
    config: dict,
) -> dict:
    """
    Return scheduler section.
    """

    return config["scheduler"]


def get_services(
    config: dict,
) -> list:
    """
    Return services for the current operating system.
    """

    os_name = platform.system().lower()

    if os_name.startswith("win"):
        return config["services"]["windows"]

    return config["services"]["linux"]


# -----------------------------------------------------------------------------
# Runtime Paths
# -----------------------------------------------------------------------------

def get_log_file(
    config: dict,
) -> str:
    """
    Return application log file.
    """

    return get_paths(config)["log_file"]


def get_state_dir(
    config: dict,
) -> str:
    """
    Return application state directory.
    """

    return get_paths(config)["state_dir"]





# -----------------------------------------------------------------------------
# Default Values
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Rotation
# -----------------------------------------------------------------------------

def get_rotation(
    config: dict,
) -> dict:
    """
    Return global rotation configuration.
    """

    return get_defaults(
        config
    )["rotation"]


def get_rotation_type(
    config: dict,
) -> str:
    """
    Return global rotation type.
    """

    return get_rotation(
        config
    )["type"]


def get_max_size_mb(
    config: dict,
) -> int:
    """
    Return global max size.

    Used only for size-based rotation.
    """

    return get_rotation(
        config
    ).get(
        "max_size_mb",
        0,
    )

def get_effective_rotation(
    config: dict,
    log: dict,
) -> dict:
    """
    Return the effective rotation configuration.

    Resolution order:

        1. Per-log override
        2. Global defaults
    """

    #
    # Global rotation policy
    #

    rotation = get_rotation(
        config
    ).copy()

    #
    # Per-log override
    #

    override = log.get(
        "rotation"
    )

    if override is None:

        return rotation

    if not isinstance(
        override,
        dict,
    ):

        raise ConfigError(
            "log.rotation must be an object."
        )

    #
    # Override type
    #

    rotation_type = override.get(
        "type"
    )

    if rotation_type is not None:

        if rotation_type not in VALID_ROTATION_TYPES:

            raise ConfigError(
                "rotation.type must be "
                "'size', 'daily' or "
                "'half_daily'."
            )

        rotation["type"] = rotation_type
        
        if "cron" in override:
            cron = override["cron"]
            if (
                not isinstance(
                    cron,
                    str,
                    )
                or not cron.strip()
            ):
                raise ConfigError(
                    "rotation.cron must be a non-empty string."
                    )

    rotation["cron"] = cron

    #
    # Override max_size_mb
    #

    if "max_size_mb" in override:

        value = override[
            "max_size_mb"
        ]

        if (
            not isinstance(
                value,
                int,
            )
            or value <= 0
        ):

            raise ConfigError(
                "rotation.max_size_mb "
                "must be greater than zero."
            )

        rotation[
            "max_size_mb"
        ] = value

    return rotation



def get_compress(
    config: dict,
) -> bool:
    return get_defaults(config)["compress"]


def get_zip_level(
    config: dict,
) -> int:
    return get_defaults(config)["zip_level"]


def get_move_after_days(
    config: dict,
) -> int:
    return get_defaults(config)["move_after_days"]


def get_retention_days(
    config: dict,
) -> int:
    return get_defaults(config)["retention_days"]


def get_compression_workers(
    config: dict,
) -> int:
    return get_defaults(config)["compression_workers"]


def get_log_level(
    config: dict,
) -> str:
    """
    Return normalized log level.
    """

    return get_defaults(config)["log_level"].upper()


# -----------------------------------------------------------------------------
# Scheduler
# -----------------------------------------------------------------------------

def get_rotate_scheduler(
    config: dict,
) -> dict:
    return get_scheduler(config)["rotate"]


def get_archive_scheduler(
    config: dict,
) -> dict:
    return get_scheduler(config)["archive"]


def get_cleanup_scheduler(
    config: dict,
) -> dict:
    return get_scheduler(config)["cleanup"]


def get_rotate_interval(
    config: dict,
) -> int:
    """
    Return rotate interval in seconds.
    """

    return get_rotate_scheduler(config)["seconds"]


def get_archive_cron(
    config: dict,
) -> str:
    return get_archive_scheduler(config)["cron"]


def get_cleanup_cron(
    config: dict,
) -> str:
    return get_cleanup_scheduler(config)["cron"]


# -----------------------------------------------------------------------------
# Scheduler Enabled Flags
# -----------------------------------------------------------------------------

def is_rotate_enabled(
    config: dict,
) -> bool:
    """
    Return True if rotate scheduler is enabled.
    """

    return get_rotate_scheduler(config).get(
        "enabled",
        True,
    )


def is_archive_enabled(
    config: dict,
) -> bool:
    """
    Return True if archive scheduler is enabled.
    """

    return get_archive_scheduler(config).get(
        "enabled",
        True,
    )


def is_cleanup_enabled(
    config: dict,
) -> bool:
    """
    Return True if cleanup scheduler is enabled.
    """

    return get_cleanup_scheduler(config).get(
        "enabled",
        True,
    )
