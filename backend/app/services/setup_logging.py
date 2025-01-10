import json
import logging
import logging.config

from pydantic import BaseModel


class JsonFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\x1b[38;20m",  # grey
        "INFO": "\x1b[32;20m",  # green
        "WARNING": "\x1b[33;20m",  # yellow
        "ERROR": "\x1b[31;20m",  # red
        "CRITICAL": "\x1b[31;1m",  # bold red
    }
    RESET = "\x1b[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["DEBUG"])
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

        # Add color to console output, but not to file output
        if getattr(
            record, "colored", True
        ):  # Default to colored output
            return f"{color}{json.dumps(log_data, indent=2, default=str)}{self.RESET}"
        return json.dumps(log_data, indent=2, default=str)


def setup_logging(debug: bool = False) -> None:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JsonFormatter,
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG" if debug else "INFO",
                "formatter": "json",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "level": "DEBUG",
                "formatter": "json",
                "class": "logging.FileHandler",
                "filename": "logs/app.log",
                "mode": "a",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],  # updated handler name
                "level": "WARNING",
                "propagate": True,
            },
            "app": {
                "handlers": ["console", "file"],  # both handlers
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
