"""Base Models and Interfaces for Tool Marketplace Plugins."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PluginManifest(BaseModel):
    """Specification and metadata describing a Marketplace Tool Plugin."""

    id: str = Field(..., description="Unique slug identifier (e.g. currency_converter)")
    name: str = Field(..., description="Human-readable tool name")
    version: str = Field(default="1.0.0", description="Semantic version string")
    author: str = Field(default="Community Developer", description="Tool creator name or email")
    category: str = Field(default="utilities", description="Tool category (e.g. finance, nlp, web, dev)")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    description: str = Field(..., description="Detailed description of what the tool does")
    enabled: bool = Field(default=True, description="Whether tool is active in the registry")
    parameters: Dict[str, Any] = Field(
        default_factory=lambda: {"type": "object", "properties": {}},
        description="JSON Schema defining expected input arguments",
    )
    env_vars: List[str] = Field(default_factory=list, description="Required environment variables")
    icon: Optional[str] = Field(default="🛠️", description="Emoji or URL icon")


class BaseToolPlugin(ABC):
    """Abstract Base Class that every custom marketplace tool must inherit from."""

    def __init__(self, manifest: Optional[PluginManifest] = None):
        self.manifest = manifest

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Executes the tool logic asynchronously with parsed arguments."""
        raise NotImplementedError

    def validate_args(self, kwargs: Dict[str, Any]) -> bool:
        """Validates incoming arguments against required manifest parameters."""
        if not self.manifest or "required" not in self.manifest.parameters:
            return True
        required_fields = self.manifest.parameters.get("required", [])
        return all(k in kwargs for k in required_fields)
