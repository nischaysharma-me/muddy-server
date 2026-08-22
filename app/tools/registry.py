"""Agent Tool Registry and Execution Manager."""

import inspect
from typing import Any, Callable, Dict, List, Optional
from langchain_core.tools import StructuredTool, BaseTool
from pydantic import BaseModel, create_model
from app.core.exceptions import ToolExecutionError
from app.core.logging import logger


class ToolDefinition(BaseModel):
    """Metadata describing a registered agent tool."""

    name: str
    description: str
    parameters_schema: Dict[str, Any]
    category: str = "general"


class ToolRegistry:
    """Central registry for managing agent tools and schemas."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._metadata: Dict[str, ToolDefinition] = {}

    def register(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: str = "general",
    ):
        """Decorator to register a Python function as an agent tool."""

        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            tool_desc = description or (func.__doc__ or "No description provided.").strip()

            # Inspect signature to generate schema
            sig = inspect.signature(func)
            fields = {}
            for param_name, param in sig.parameters.items():
                if param_name in ("self", "cls"):
                    continue
                param_type = param.annotation if param.annotation != inspect.Parameter.empty else Any
                param_default = param.default if param.default != inspect.Parameter.empty else ...
                fields[param_name] = (param_type, param_default)

            ParamModel = create_model(f"{tool_name}_params", **fields)
            schema = ParamModel.model_json_schema()

            self._tools[tool_name] = func
            self._metadata[tool_name] = ToolDefinition(
                name=tool_name,
                description=tool_desc,
                parameters_schema=schema,
                category=category,
            )
            logger.debug(f"[ToolRegistry] Registered tool: '{tool_name}' ({category})")
            return func

        return decorator

    def get_tool(self, name: str) -> Optional[Callable]:
        """Retrieve the callable for a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        """List metadata for all registered tools."""
        return list(self._metadata.values())

    def get_metadata(self, name: str) -> Optional[ToolDefinition]:
        """Get metadata for a specific tool."""
        return self._metadata.get(name)

    async def execute(self, name: str, **kwargs) -> Any:
        """Executes a registered tool asynchronously."""
        func = self.get_tool(name)
        if not func:
            raise ToolExecutionError(f"Tool '{name}' not found in registry.")

        try:
            if inspect.iscoroutinefunction(func):
                result = await func(**kwargs)
            else:
                result = func(**kwargs)
            return result
        except Exception as e:
            logger.error(f"[ToolRegistry] Error executing tool '{name}': {e}")
            raise ToolExecutionError(f"Tool '{name}' execution failed: {str(e)}") from e

    def to_langchain_tools(self, names: Optional[List[str]] = None) -> List[BaseTool]:
        """Convert registered tools into LangChain BaseTool instances."""
        tools_to_convert = names if names else list(self._tools.keys())
        lc_tools: List[BaseTool] = []

        for t_name in tools_to_convert:
            if t_name not in self._tools:
                continue

            func = self._tools[t_name]
            meta = self._metadata[t_name]

            if inspect.iscoroutinefunction(func):
                tool = StructuredTool.from_function(
                    coroutine=func,
                    name=meta.name,
                    description=meta.description,
                )
            else:
                tool = StructuredTool.from_function(
                    func=func,
                    name=meta.name,
                    description=meta.description,
                )
            lc_tools.append(tool)

        return lc_tools


# Global Tool Registry Singleton
registry = ToolRegistry()
