import logging
import os
import sys

LOGGER_NAME = "ia_op"
logger = logging.getLogger(LOGGER_NAME)
logger.propagate = False


def setup_logger(log_level: int, log_file: str | None) -> None:
    """
    Configure the project logger without affecting other loggers.

    Args:
    - log_level (int): Value from 0 to 4.
    - log_file (str | None): "stderr", "stdout", or a file path.

    Returns:
    - logging.Logger: Configured project logger.

    Raises:
    - ValueError: If log_level is out of range.
    """
    if not 0 <= log_level <= 4:
        raise ValueError("--log-level must be between 0 and 4")

    levels = [
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ]

    logger.setLevel(levels[log_level])

    # Clear old handlers to avoid duplicates if setup is called again
    logger.handlers.clear()

    if log_file == "stderr":
        handler = logging.StreamHandler(sys.stderr)
    elif log_file == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    elif log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    else:
        handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s | %(filename)s:%(lineno)d: %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
