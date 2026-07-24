"""
main.py

LogRotator application entry point.
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------

import argparse
import signal
import threading

# -----------------------------------------------------------------------------
# Local Imports
# -----------------------------------------------------------------------------

from logrotatorx.compressor import (
    initialize_compressor,
    shutdown_compressor,
)

from logrotatorx.config import (
    get_compression_workers,
    get_log_file,
    get_log_level,
    get_state_dir,
    load_config,
    validate_config,
)

from logrotatorx.context import AppContext

from logrotatorx.exceptions import (
    LogRotatorError,
)

from logrotatorx.lock import (
    acquire_lock,
    release_lock,
)

from logrotatorx.logger import (
    setup_logger,
)

from logrotatorx.processor import (
    archive_job,
    cleanup_job,
    rotate_job,
)

from logrotatorx.scheduler import (
    initialize_scheduler,
    shutdown_scheduler,
    start_scheduler,
)

from logrotatorx.version import (
    APP_NAME,
    APP_VERSION,
)

from logrotatorx.state import (
    initialize_state,
)


# -----------------------------------------------------------------------------
# Runtime
# -----------------------------------------------------------------------------

stop_event = threading.Event()


def signal_handler(
    signum: int,
    frame,
) -> None:
    """
    Handle application shutdown.
    """

    stop_event.set()


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """

    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="LogRotator",
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to config.yaml",
    )

    return parser.parse_args()


def main() -> None:
    """
    Application entry point.
    """

    logger = None
    lock = None
    started = False

    try:

        #
        # Command Line
        #

        args = parse_arguments()

        #
        # Configuration
        #

        config = load_config(
            args.config
        )

        validate_config(config)

        #
        # Logging
        #

        logger = setup_logger(
            log_file=get_log_file(config),
            log_level=get_log_level(config),
        )

        logger.info(
            "%s %s starting...",
            APP_NAME,
            APP_VERSION,
        )

        logger.info(
            "Configuration : %s",
            args.config,
        )

        #
        # Application Lock
        #

        lock = acquire_lock(
            get_state_dir(config)
        )

        if lock is None:

            logger.warning(
                "Another instance is already running."
            )

            return

        #
        # Compression Executor
        #

        initialize_compressor(
            get_compression_workers(config)
        )
        
        
        #
        # Rotation State
        #
        
        initialize_state(
            get_state_dir(config)
        )

        #
        # Application Context
        #

        app_context = AppContext(
            config=config
        )

        #
        # Scheduler
        #

        initialize_scheduler(
            config=config,
            rotate_job=lambda: rotate_job(
                app_context
            ),
            archive_job=lambda: archive_job(
                app_context
            ),
            cleanup_job=lambda: cleanup_job(
                app_context
            ),
        )

        start_scheduler()

        started = True

        logger.info(
            "Application started successfully."
        )

        #
        # Signal Handling
        #

        signal.signal(
            signal.SIGINT,
            signal_handler,
        )

        signal.signal(
            signal.SIGTERM,
            signal_handler,
        )

        #
        # Wait forever
        #

        stop_event.wait()
            
    except LogRotatorError as exc:
        
        if logger is not None:
            logger.error(
                "%s",
                exc,
        )

            logger.info(
                "Application terminated."
        )

        else:

            print(
               f"ERROR: {exc}"
        )

        return
    
        
    
    except Exception:

        if logger is not None:

            logger.exception(
                "Unexpected application error."
            )

        raise

    finally:

        #
        # Scheduler
        #

        try:

            shutdown_scheduler()

        except Exception:

            pass

        #
        # Compression Executor
        #

        try:

            shutdown_compressor()

        except Exception:

            pass

        #
        # Application Lock
        #

        try:

            release_lock(
                lock
            )

        except Exception:

            pass

        #
        # Shutdown
        #

        if started and logger is not None:

            logger.info(
                "%s stopped.",
                APP_NAME,
            )


if __name__ == "__main__":

    main()
