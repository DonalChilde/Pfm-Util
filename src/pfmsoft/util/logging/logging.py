"""
Convenience functions for logging.

"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def rotating_file_handler(
    log_dir: Path, file_name: str, log_level: int, format_string: str | None = None
) -> RotatingFileHandler:
    """
    Convenience function to init a rotating file handler.

    Ensures log directory exists, and enforces .log file suffix.
    If no format string is provided, uses a default format.

    Args:
        log_dir: The log directory.
        file_name: The name of the log file, without suffix.
        log_level: The log level
        format_string: The format string for the log message. Defaults to None.

    Returns:
        RotatingFileHandler: The confgured RotatingFileHandler.
    """

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / Path(file_name)
    log_file.with_suffix(".log")
    handler = RotatingFileHandler(log_file, maxBytes=102400, backupCount=10)
    if format_string is None:
        format_string = (
            "%(asctime)s %(levelname)s:%(funcName)s: "
            "%(message)s [in %(pathname)s:%(lineno)d]"
        )
    handler.setFormatter(logging.Formatter(format_string))
    handler.setLevel(log_level)
    return handler


def rotating_file_logger(
    log_dir: Path,
    log_name: str,
    log_level: int,
):
    """
    Configures a logger with a rotating file handler.

    Convenience method with useful defaults.

    Args:
        log_dir: The log directory.
        log_name: The name of the logger.
        log_level: The log level.

    Returns:
        The logger.
    """
    logger = logging.getLogger(log_name)
    handler = rotating_file_handler(
        log_dir=log_dir, file_name=log_name, log_level=log_level
    )
    logger.addHandler(handler)
    logger.setLevel(log_level)
    logger.info("Rotating file logger initialized with %r", handler)
    return logger


# def configure_file_logger(
#     log_dir: Path, logger_name: str, log_level: int
# ) -> logging.Logger:
#     """Configure a logger with a RotatingFileHandler.

#     Note: Calling this function more than once with the same logger_name
#     will result in duplicated logs.
#     """
#     log_file_name = f"{logger_name}.log"
#     logger_ = logging.getLogger(logger_name)
#     log_dir_path: Path = Path(log_dir)
#     log_dir_path.mkdir(parents=True, exist_ok=True)
#     log_file_path = log_dir_path / Path(log_file_name)
#     handler = log_file_handler(log_file_path, log_level=log_level)
#     logger_.addHandler(handler)
#     logger_.setLevel(log_level)
#     ############################################################
#     # NOTE add file handler to other library modules as needed #
#     ############################################################
#     # async_logger = logging.getLogger("eve_esi_jobs")
#     # async_logger.addHandler(file_handler)
#     # async_logger.setLevel(log_level)
#     logger_.info("Rotating File Logger initializd at %s", log_file_path)
#     return logger_


# def log_file_handler(
#     file_path: Path,
#     log_level: int = logging.WARNING,
#     format_string: Optional[str] = None,
# ):
#     """
#     _summary_

#     _extended_summary_

#     Args:
#         file_path (_type_): _description_
#         log_level (_type_, optional): _description_. Defaults to logging.WARNING.
#         format_string (_type_, optional): _description_. Defaults to None.

#     Returns:
#         _type_: _description_
#     """
#     handler = RotatingFileHandler(file_path, maxBytes=102400, backupCount=10)
#     if format_string is None:
#         format_string = (
#             "%(asctime)s %(levelname)s:%(funcName)s: "
#             "%(message)s [in %(pathname)s:%(lineno)d]"
#         )
#     handler.setFormatter(logging.Formatter(format_string))
#     handler.setLevel(log_level)
#     return handler
