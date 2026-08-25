"""Abstract Base Pipeline Step."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from app.pipelines.context import PipelineContext


class BasePipelineStep(ABC):
    """Abstract base class representing a single step within a transactional pipeline."""

    def __init__(self, name: Optional[str] = None, weight: float = 1.0):
        self.name = name or self.__class__.__name__
        self.weight = weight

    @abstractmethod
    async def execute(self, context: PipelineContext) -> Any:
        """Executes the core logic of this pipeline step."""
        raise NotImplementedError

    async def rollback(self, context: PipelineContext) -> None:
        """Compensating action executed in reverse order if a downstream step fails."""
        pass

    async def validate(self, context: PipelineContext) -> bool:
        """Validates prerequisites or intermediate state before executing this step."""
        return True
