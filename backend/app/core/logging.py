import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict

# Sensitive fields to never log
REDACTED_KEYS = {"password", "passwordhash", "secret", "token", "authorization", "cookie", "session_id"}

class StructuredJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include request_id if available
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id

        # Include extra payload safely
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            clean_extra = {}
            for k, v in record.extra_data.items():
                if k.lower() in REDACTED_KEYS:
                    clean_extra[k] = "[REDACTED]"
                else:
                    clean_extra[k] = v
            log_obj["data"] = clean_extra

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)

def get_logger(name: str = "krishiguard") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = get_logger("krishiguard.app")
