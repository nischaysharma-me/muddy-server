"""Tool and MCP Execution Service."""

import time
from typing import Any, Dict, List, Optional
from app.config import settings
from app.core.exceptions import ToolExecutionError
from app.core.logging import logger
from app.providers.tools import mcp_bridge, registry
from app.services.base_service import BaseService


class ToolService(BaseService):
    """Manages dynamic tool and MCP schema discovery, execution, and audit logging."""

    def __init__(self):
        super().__init__("ToolService")

    def list_all_tools(self) -> List[Dict[str, Any]]:
        """Returns catalog of all registered internal tools and external MCP tools."""
        native_tools = [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "parameters": t.parameters_schema,
                "is_mcp": False,
            }
            for t in registry.list_tools()
        ]
        mcp_tools = [
            {
                "name": t["full_name"],
                "description": t["description"],
                "category": f"mcp_{t['server']}",
                "parameters": t["schema"],
                "is_mcp": True,
            }
            for t in mcp_bridge.list_mcp_tools()
        ]
        return native_tools + mcp_tools

    async def execute_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Executes a tool and logs invocation to SQL audit log."""
        start_time = time.perf_counter()
        is_error = False
        error_msg = None
        result = None

        try:
            result = await registry.execute(name, **arguments)
        except Exception as e:
            is_error = True
            error_msg = str(e)
            raise ToolExecutionError(f"Error executing tool '{name}': {e}") from e
        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            await self._log_tool_audit(
                session_id=session_id,
                tool_name=name,
                is_mcp=False,
                arguments=arguments,
                result=result if not is_error else None,
                is_error=is_error,
                error_message=error_msg,
                duration_ms=duration_ms,
            )

        return {
            "tool": name,
            "result": result,
            "duration_ms": duration_ms,
            "status": "success",
        }

    async def _log_tool_audit(
        self,
        session_id: Optional[str],
        tool_name: str,
        is_mcp: bool,
        arguments: Dict[str, Any],
        result: Optional[Any],
        is_error: bool,
        error_message: Optional[str],
        duration_ms: float,
    ):
        if not settings.ENABLE_SQL_DB:
            return
        try:
            from app.db.session import async_session_factory
            from app.db.models.tool_log import ToolLogModel
            async with async_session_factory() as session:
                async with session.begin():
                    log = ToolLogModel(
                        session_id=session_id,
                        tool_name=tool_name,
                        is_mcp=is_mcp,
                        arguments=arguments,
                        result=result if isinstance(result, dict) else {"output": str(result)},
                        is_error=is_error,
                        error_message=error_message,
                        duration_ms=duration_ms,
                    )
                    session.add(log)
        except Exception as e:
            logger.warning(f"[ToolService] Failed to record tool audit log in SQL: {e}")


tool_service = ToolService()
