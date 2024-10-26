import logging
import os
from logging.handlers import RotatingFileHandler
from app.core.config import settings

LOG_FILE_PATH = os.path.join("logs", "app.log")

# create logs directory if not exists
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

def setup_logger(name: str, level: int = settings.log_level.upper()) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # remove existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # set log format
    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
    )

    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # file handler (rotate every 5MB)
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
