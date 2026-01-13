import logging
import sys

from pythonjsonlogger import jsonlogger

from app.core.config import settings


def configure_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"levelname": "level", "name": "logger"},
    )
    handler.setFormatter(formatter)

    root.handlers.clear()
    root.addHandler(handler)

    # Quiet noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
