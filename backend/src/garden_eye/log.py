"""Centralized logging configuration for GardenEye."""

import logging


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create and configure a logger with standardized formatting.

    Args:
        name: Logger name, typically module name
        level: Logging level

    Returns:
        Configured logger instance with standardized formatting
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    console = logging.StreamHandler()
    console.setLevel(level)

    if name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] uvicorn: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    console.setFormatter(formatter)
    logger.handlers = [console]
    logger.propagate = False
    return logger
