import logging
import logging.config


def setup_logging(debug: bool = False):
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "default": {
                "level": "DEBUG" if debug else "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "level": "DEBUG",
                "formatter": "standard",
                "class": "logging.FileHandler",
                "filename": "logs/app.log",
                "mode": "a",
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": "WARNING",
                "propagate": True,
            },
            "app": {
                "handlers": ["default"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
            "urllib3": {
                "level": "WARNING",
            },
            "asyncio": {
                "level": "WARNING",
            },
            "websockets": {
                "level": "WARNING",
            },
            "httpx": {
                "level": "WARNING",
            },
        },
    }

    logging.config.dictConfig(logging_config)
