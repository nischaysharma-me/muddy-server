"""Abstract Base Compute Engine Interface."""

from abc import ABC, abstractmethod
from typing import Any, Callable, List


class BaseComputeEngine(ABC):
    """Abstract interface for multiprocessing and distributed compute providers."""

    @abstractmethod
    async def execute(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Executes a single callable asynchronously in a parallel worker."""
        raise NotImplementedError

    @abstractmethod
    async def map(self, func: Callable, items: List[Any]) -> List[Any]:
        """Maps a callable over a collection of items concurrently."""
        raise NotImplementedError

    @property
    @abstractmethod
    def engine_type(self) -> str:
        """Returns the identifier of this compute engine."""
        raise NotImplementedError
