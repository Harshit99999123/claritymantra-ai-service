import contextvars
import logging
from logging.config import dictConfig

request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx_var.get()
        return True


def configure_logging(log_level: str) -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "request_id": {
                    "()": "core.logging.RequestIdFilter",
                }
            },
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | request_id=%(request_id)s | %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "filters": ["request_id"],
                }
            },
            "root": {
                "handlers": ["console"],
                "level": log_level.upper(),
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
