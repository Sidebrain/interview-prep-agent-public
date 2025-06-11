import json
import logging
import logging.config
from typing import Any


class JsonFormatter(logging.Formatter):
    """Base JSON formatter that handles complex objects and provides clean output"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "logger": record.name,
            "level": record.levelname,
            "file": record.filename,
            "line": record.lineno,
            "message": record.msg,
        }

        # Add context if available
        if hasattr(record, "context"):
            log_data["context"] = self._sanitize_value(record.context)

        # Add extra data if available
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra

        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(log_data, indent=2, default=str)

    def _sanitize_value(self, value: Any) -> Any:
        """Sanitize values for JSON serialization"""
        if isinstance(value, dict):
            return {
                k: self._sanitize_value(v) for k, v in value.items()
            }
        if isinstance(value, (list, tuple)):
            return [self._sanitize_value(v) for v in value]
        if hasattr(value, "model_dump"):  # Pydantic v2 model
            return value.model_dump()
        if hasattr(
            value, "dict"
        ):  # Pydantic v1 model (backwards compatibility)
            return value.dict()
        try:
            json.dumps(value)
            return value
        except Exception:
            return str(value)


class ColoredConsoleFormatter(JsonFormatter):
    """Adds color to console output"""

    COLORS = {
        "DEBUG": "\x1b[38;20m",  # grey
        "INFO": "\x1b[32;20m",  # green
        "WARNING": "\x1b[33;20m",  # yellow
        "ERROR": "\x1b[31;20m",  # red
        "CRITICAL": "\x1b[31;1m",  # bold red
    }
    RESET = "\x1b[0m"

    def format(self, record: logging.LogRecord) -> str:
        formatted_json = super().format(record)
        color = self.COLORS.get(record.levelname, self.COLORS["DEBUG"])
        return f"{color}{formatted_json}{self.RESET}"


class JsonArrayFileHandler(logging.FileHandler):
    """A file handler that maintains a JSON array format with clear spacing for readability"""

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        encoding: str | None = None,
        delay: bool = False,
    ) -> None:
        super().__init__(filename, mode, encoding, delay)
        # Initialize file with array opening bracket if empty
        if mode == "w" or (mode == "a" and self.stream.tell() == 0):
            self.stream.write("[\n")
        elif mode == "a":
            # If appending and file not empty, add comma after last entry
            self.stream.seek(
                self.stream.tell() - 2, 0
            )  # Move before final bracket
            self.stream.write(",\n\n")  # Add extra newline for spacing

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record with proper JSON array formatting and spacing"""
        msg = self.format(record)
        self.stream.write(msg)
        self.stream.write(",\n\n")  # Add extra newline for spacing
        self.flush()

    def close(self) -> None:
        """Ensure proper JSON array closing on shutdown"""
        if not self.stream.closed:
            self.stream.seek(
                self.stream.tell() - 3, 0
            )  # Move before last comma and newlines
            self.stream.write("\n]\n")  # Add final newline
        super().close()


def setup_logging(debug: bool = False) -> None:
    """Configure application logging with console and file outputs"""
    # Create formatters
    console_formatter = ColoredConsoleFormatter()
    file_formatter = JsonFormatter()

    # Create and configure handlers
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)

    file_handler = JsonArrayFileHandler("logs/app.log", mode="a")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    root_logger.addHandler(console_handler)

    # Configure app logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.DEBUG if debug else logging.INFO)
    app_logger.propagate = False
    app_logger.addHandler(console_handler)
    app_logger.addHandler(file_handler)

    # Configure third-party loggers
    for logger_name in ["urllib3", "asyncio", "websockets", "httpx"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
