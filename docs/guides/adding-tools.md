# Guide: Adding Agent Tools & Model Context Protocol (MCP) 🔌

This guide explains how to define native Python tools for AI agents and connect external Model Context Protocol (MCP) servers.

---

## 1. Native Python Tool Registration

Muddy Server uses a decorator-based `ToolRegistry` ([`app/providers/tools/registry.py`](file:///Users/davinci/Documents/sscorp/nischaysharma.com/muddy-server/app/providers/tools/registry.py)) with automatic JSON Schema generation from Python type annotations.

### Example: Creating a Financial Conversion Tool
Create or edit your tool in `app/tools/custom.py`:

```python
from typing import Dict, Any
from app.providers.tools import registry

@registry.register(
    name="convert_currency",
    description="Converts an amount from one currency to another using current market rates.",
    category="finance"
)
async def convert_currency(
    amount: float,
    from_currency: str = "USD",
    to_currency: str = "EUR"
) -> Dict[str, Any]:
    """
    Converts amount from from_currency to to_currency.
    """
    rates = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 154.5,
        "INR": 86.5,
    }
    
    from_rate = rates.get(from_currency.upper(), 1.0)
    to_rate = rates.get(to_currency.upper(), 1.0)
    
    amount_in_usd = amount / from_rate
    converted_amount = amount_in_usd * to_rate
    
    return {
        "original_amount": amount,
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "converted_amount": round(converted_amount, 2),
    }
```

Once registered, this tool is:
1. Automatically available to LangGraph ReAct agents on `POST /api/v1/agents/chat`.
2. Discoverable in the tool catalog at `GET /api/v1/tools`.
3. Directly testable via `POST /api/v1/tools/convert_currency/execute`.

---

## 2. Model Context Protocol (MCP) Integration

The **Model Context Protocol (MCP)** allows connecting external standalone tools, database inspectors, and third-party servers over stdio or Server-Sent Events (SSE).

### Registering an MCP Server Bridge:
```python
from app.providers.tools import mcp_bridge

# 1. Register MCP Server Connection
mcp_bridge.register_server(
    server_name="github_mcp",
    transport="sse",
    config={"url": "http://localhost:8080/sse"}
)

# 2. Register Tool Exposed by MCP Server
mcp_bridge.register_mcp_tool(
    server_name="github_mcp",
    tool_name="create_issue",
    description="[MCP:github] Creates a new GitHub issue in target repository.",
    schema={
        "type": "object",
        "properties": {
            "repo": { "type": "string", "description": "owner/repo" },
            "title": { "type": "string", "description": "Issue title" },
            "body": { "type": "string", "description": "Issue markdown body" }
        },
        "required": ["repo", "title"]
    },
    handler=my_custom_mcp_handler
)
```

---

## 3. Tool Execution Auditing & SQL Logging

Every time an agent invokes a tool (whether native Python or MCP), `ToolService.execute_tool()`:
1. Validates inputs against the schema.
2. Measures execution duration in milliseconds.
3. Automatically writes a record to `tool_audit_logs` in SQL, capturing latency, arguments, return values, and error traces.
