import json
import logging
import logging.config

from pydantic import BaseModel


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "logger": record.name,
            "level": record.levelname,
            "file": record.filename,
            "line": record.lineno,
            "message": record.msg,
        }

        # Add extra context if available
        if hasattr(record, "context"):
            try:
                if isinstance(record.context, dict):
                    sanitized_context = {}
                    for key, value in record.context.items():
                        if isinstance(value, BaseModel):
                            sanitized_context[key] = value.model_dump(
                                by_alias=True
                            )
                        else:
                            try:
                                json.dumps(value)
                                sanitized_context[key] = value
                            except Exception:
                                sanitized_context[key] = str(value)
                    log_data["context"] = sanitized_context
                else:
                    log_data["context"] = str(record.context)
            except Exception:
                log_data["context"] = str(record.context)

        # Add extra
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra

        # Handle exceptions
        if record.exc_info:
            log_data["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(log_data, indent=2, default=str)


def setup_logging(debug: bool = False) -> None:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "()": JsonFormatter,
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
