"""Base Service with Shared Lifecycle Logic."""

from typing import Optional
from app.core.logging import logger


class BaseService:
    """Base class for all business-logic agnostic compute services."""

    def __init__(self, service_name: Optional[str] = None):
        self.service_name = service_name or self.__class__.__name__
        logger.debug(f"[Service] Initialized service '{self.service_name}'")
