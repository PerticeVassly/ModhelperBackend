import logging.config
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "app.log"),
            "formatter": "standard",
        },
    },
    "loggers": {
        "database": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "api": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "service": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "llm": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "admin_manager": {
            "level": "INFO",
            "handlers": ["file"],
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)