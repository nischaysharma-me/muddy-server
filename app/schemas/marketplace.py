"""Pydantic Schemas for Tool Marketplace & Plugin APIs."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MarketplaceToolItem(BaseModel):
    """Catalog item in Marketplace."""

    id: str
    name: str
    version: str
    author: str
    category: str
    tags: List[str]
    description: str
    enabled: bool
    is_active: bool
    icon: Optional[str] = "🛠️"
    parameters: Dict[str, Any]
    env_vars: List[str] = Field(default_factory=list)


class MarketplaceToolDetailResponse(BaseModel):
    """Detailed view of a marketplace tool."""

    manifest: Dict[str, Any]
    readme: str
    handler_code: str
    is_active: bool


class ToolScaffoldRequest(BaseModel):
    """Payload to scaffold boilerplate for a new tool."""

    tool_id: str = Field(..., description="Unique tool identifier, e.g. 'web_scraper'")
    name: Optional[str] = Field(default=None, description="Human-readable tool name")
    category: str = Field(default="utilities", description="Tool category (finance, developer, nlp, web)")
    description: str = Field(default="Custom tool for Muddy Server", description="What the tool does")
    author: str = Field(default="Developer", description="Author name or organization")
    tags: Optional[List[str]] = Field(default=None, description="Tags for search and classification")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Custom JSON Schema for parameters")


class ToolScaffoldResponse(BaseModel):
    """Response returned upon tool scaffolding."""

    tool_id: str
    path: str
    status: str
    message: str


class ToolUploadRequest(BaseModel):
    """Payload to upload and register a custom tool."""

    tool_id: str = Field(..., description="Unique tool slug")
    manifest: Dict[str, Any] = Field(..., description="Manifest JSON metadata dictionary")
    handler_code: str = Field(..., description="Python source code implementing BaseToolPlugin")
    readme_content: Optional[str] = Field(default=None, description="Optional README markdown content")


class ToolActionResponse(BaseModel):
    """Generic status response for tool actions."""

    tool_id: str
    status: str
    message: str
