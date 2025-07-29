import logging
import os
from logging.config import dictConfig


def setup_logger() -> None:
    level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    config = {
        "version": 1,
        "disable_existing_loggers": True,
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "formatters": {
            "default": {"format": "%(asctime)s :: %(levelname)s :: %(message)s"},
        },
        "loggers": {
            "": {"handlers": ["default"], "level": level},
            "uvicorn.error": {"level": "INFO"},
        },
    }

    dictConfig(config)
    logging.debug("Logger configured")


setup_logger()


def get_logger():
    return logging.root
