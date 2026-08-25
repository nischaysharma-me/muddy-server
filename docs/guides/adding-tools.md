# Guide: Adding Agent Tools & MCP Servers 🔌

How to register custom Python functions as agent tools and connect external Model Context Protocol (MCP) servers.

---

## 1. Registering Native Python Tools
Use `@registry.register()` with type annotations:

```python
from app.providers.tools import registry

@registry.register(name="currency_converter", description="Converts USD to EUR", category="finance")
async def currency_converter(amount: float, target_currency: str = "EUR") -> dict:
    converted = amount * 0.92
    return {"amount": amount, "target": target_currency, "result": converted}
```

---

## 2. Registering External MCP Servers
Connect stdio or SSE Model Context Protocol servers:

```python
from app.providers.tools import mcp_bridge

# Register MCP Server
mcp_bridge.register_server(
    server_name="github_mcp",
    transport="sse",
    config={"url": "http://localhost:8080/sse"},
)

# Register MCP Tool
mcp_bridge.register_mcp_tool(
    server_name="github_mcp",
    tool_name="list_repositories",
    description="Lists user repositories on GitHub",
    schema={"properties": {"username": {"type": "string"}}},
    handler=my_github_handler,
)
```
