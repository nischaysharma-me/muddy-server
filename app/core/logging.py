"""Structured logging setup using Rich and standard logging."""

import logging
import sys
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from app.config.server import ServerSettings

console = Console()


def setup_logging(debug: bool = True, log_level_override: Optional[str] = None) -> logging.Logger:
    """Configures structured logging with Rich formatting."""
    level = logging.DEBUG if debug else logging.INFO
    if log_level_override:
        level = getattr(logging, log_level_override.upper(), level)

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                tracebacks_show_locals=False,
                markup=True,
                show_time=True,
                show_path=debug,
            )
        ],
    )

    logger_instance = logging.getLogger("muddy_server")
    logger_instance.setLevel(level)
    return logger_instance


logger = setup_logging()
