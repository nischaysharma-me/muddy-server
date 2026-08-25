# API Reference: Tools & Model Context Protocol (MCP) 🔌

Endpoints for listing registered tools and dynamically executing them.

---

### `GET /api/v1/tools`
Returns catalog of all registered tools and connected external MCP server tools.
- **Response**:
  ```json
  [
    {
      "name": "calculator",
      "description": "Evaluates a mathematical expression safely.",
      "category": "math",
      "parameters": { ... },
      "is_mcp": false
    },
    {
      "name": "mcp_github_create_issue",
      "description": "[MCP:github] Creates a new GitHub issue.",
      "category": "mcp_github",
      "parameters": { ... },
      "is_mcp": true
    }
  ]
  ```

---

### `POST /api/v1/tools/{tool_name}/execute`
Directly executes an agent tool with JSON parameters and logs execution to `tool_audit_logs`.
