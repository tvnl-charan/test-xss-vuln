"""Application logging configuration (main-branch utility)."""

import logging

DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging with a sensible default format."""
    logging.basicConfig(level=level, format=DEFAULT_FORMAT)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger using the application configuration."""
    return logging.getLogger(name)