import json
import logging
import sys
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "logger": record.name,
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%SZ"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)
        for key, value in record.__dict__.items():
            if key not in ("name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module",
                           "exc_info", "exc_text", "stack_info", "lineno", "funcName", "created", "msecs",
                           "relativeCreated", "thread", "threadName", "processName", "process"):
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def _configure_root() -> None:
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.setLevel(logging.INFO)
    root.addHandler(handler)


def get_logger(name: str = "podcast_engine") -> logging.Logger:
    _configure_root()
    return logging.getLogger(name)
