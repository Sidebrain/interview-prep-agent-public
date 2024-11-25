import logging
import logging.config
import json


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "logger": record.name,
            "level": record.levelname,
            "file": record.filename,
            "line": record.lineno,
            "message": record.msg
        }

        # Add extra context if available
        if hasattr(record, "context"):
            log_data["context"] = record.context

        # Handle exceptions
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, indent=2, default=str)


def setup_logging(debug: bool = False):
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s",
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
