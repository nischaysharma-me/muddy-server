# API Reference: Tool Marketplace Endpoints 🏪

Endpoints for discovering, scaffolding, uploading, and managing modular tool plugins.

---

### 1. `GET /api/v1/tools/marketplace`
Browse catalog of discovered marketplace tools with filtering and search.
- **Query Parameters**:
  - `category` (*string, optional*): e.g. `finance`, `developer`, `nlp`, `utilities`
  - `tag` (*string, optional*): e.g. `currency`, `json`, `crypto`
  - `search` (*string, optional*): Free-text search matching name, description, tags.
- **Response** (`200 OK`):
  ```json
  [
    {
      "id": "currency_converter",
      "name": "Currency Converter",
      "version": "1.0.0",
      "author": "Muddy Team",
      "category": "finance",
      "tags": ["currency", "finance", "money"],
      "description": "Converts amounts between global fiat currencies.",
      "enabled": true,
      "is_active": true,
      "icon": "💱",
      "parameters": { ... }
    }
  ]
  ```

---

### 2. `GET /api/v1/tools/marketplace/{tool_id}`
Retrieves full manifest, parameter JSON schema, README documentation, and handler source code.
- **Response** (`200 OK`):
  ```json
  {
    "manifest": { ... },
    "readme": "# Currency Converter...",
    "handler_code": "class CurrencyConverterTool...",
    "is_active": true
  }
  ```

---

### 3. `POST /api/v1/tools/marketplace/scaffold`
Scaffolds a new tool boilerplate folder on disk with starter manifest, handler, test, and README.
- **Request Body**:
  ```json
  {
    "tool_id": "pdf_reader",
    "name": "PDF Reader",
    "category": "utilities",
    "description": "Extracts text from PDF documents.",
    "author": "Developer",
    "tags": ["pdf", "text", "extract"]
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "tool_id": "pdf_reader",
    "path": "/app/tools/plugins/pdf_reader",
    "status": "created",
    "message": "Tool 'pdf_reader' scaffolded successfully and registered."
  }
  ```

---

### 4. `POST /api/v1/tools/marketplace/upload`
Uploads and activates a custom tool bundle dynamically.
- **Request Body**:
  ```json
  {
    "tool_id": "custom_echo",
    "manifest": {
      "name": "Custom Echo",
      "category": "utilities",
      "description": "Echoes back input",
      "parameters": {
        "type": "object",
        "properties": { "text": { "type": "string" } },
        "required": ["text"]
      }
    },
    "handler_code": "from app.tools.plugins.base import BaseToolPlugin\n\nclass CustomEchoTool(BaseToolPlugin):\n    async def execute(self, text: str):\n        return {'echo': text}\n"
  }
  ```

---

### 5. `POST /api/v1/tools/marketplace/{tool_id}/install`
Enables a marketplace tool and registers it into live agents.

---

### 6. `POST /api/v1/tools/marketplace/{tool_id}/uninstall`
Disables a marketplace tool and removes it from live agents.

---

### 7. `DELETE /api/v1/tools/marketplace/{tool_id}`
Permanently deletes a custom tool directory from the server.
