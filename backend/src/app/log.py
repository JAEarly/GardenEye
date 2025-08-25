import logging


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
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
