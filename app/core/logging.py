"""Structured logging setup using Rich and standard logging."""

import logging
import sys
from rich.console import Console
from rich.logging import RichHandler


console = Console()


def setup_logging(debug: bool = True) -> logging.Logger:
    """Configures structured logging for Muddy Server."""
    log_level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                tracebacks_show_locals=False,
                markup=True,
            )
        ],
    )

    logger = logging.getLogger("muddy_server")
    logger.setLevel(log_level)
    return logger


logger = setup_logging()
