# Guide: Tool Marketplace & Custom Plugins 🏪

Muddy Server includes a modular **Tool Marketplace & Plugin Architecture** designed to let developers create, scaffold, upload, and dynamically register custom tools **without touching or modifying core application files**.

---

## 🏗️ Architectural Overview

```
app/tools/plugins/
├── currency_converter/              # Self-contained plugin folder
│   ├── manifest.json                # Standard plugin metadata & JSON schema
│   ├── handler.py                   # Subclasses BaseToolPlugin
│   ├── test_tool.py                 # Isolated pytest test suite
│   └── README.md                    # Tool documentation & examples
│
└── <your_custom_tool>/
    ├── manifest.json
    ├── handler.py
    └── README.md
```

Any tool placed inside `app/tools/plugins/` with `enabled: true` is **automatically discovered on startup or hot-loaded dynamically at runtime**, converted into a standard LangChain `StructuredTool`, and made available to all ReAct conversational agents.

---

## 🚀 1. Scaffolding a New Tool (Instant Boilerplate)

You can generate a complete starter boilerplate with one API call:

### API Request: `POST /api/v1/tools/marketplace/scaffold`
```json
{
  "tool_id": "crypto_price_checker",
  "name": "Crypto Price Checker",
  "category": "finance",
  "author": "Nischay Sharma",
  "description": "Fetches current cryptocurrency prices in USD.",
  "tags": ["crypto", "bitcoin", "ethereum", "finance"],
  "parameters": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "Crypto symbol, e.g. BTC, ETH, SOL"
      }
    },
    "required": ["symbol"]
  }
}
```

This creates the complete starter directory `app/tools/plugins/crypto_price_checker/` on disk with starter code!

---

## 💻 2. Writing the Tool Handler

Open `app/tools/plugins/crypto_price_checker/handler.py` and subclass `BaseToolPlugin`:

```python
from typing import Any, Dict
from app.tools.plugins.base import BaseToolPlugin

class CryptoPriceCheckerTool(BaseToolPlugin):
    """Fetches real-time cryptocurrency prices in USD."""

    async def execute(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper().strip()
        
        # Example mock rates or fetch from real API
        mock_prices = {"BTC": 98500.0, "ETH": 2750.0, "SOL": 195.0}
        price = mock_prices.get(sym, 100.0)

        return {
            "symbol": sym,
            "price_usd": price,
            "currency": "USD",
            "status": "success",
        }
```

---

## 🌐 3. Uploading & Registering via API

You can upload and register any custom tool bundle directly over HTTP:

### `POST /api/v1/tools/marketplace/upload`
```json
{
  "tool_id": "text_reverser",
  "manifest": {
    "name": "Text Reverser",
    "category": "utilities",
    "description": "Reverses the order of characters in a string.",
    "parameters": {
      "type": "object",
      "properties": {
        "text": { "type": "string", "description": "String to reverse" }
      },
      "required": ["text"]
    }
  },
  "handler_code": "from app.tools.plugins.base import BaseToolPlugin\n\nclass TextReverserTool(BaseToolPlugin):\n    async def execute(self, text: str):\n        return {'reversed': text[::-1]}\n"
}
```

The tool is **immediately activated and hot-registered into live agents** without requiring a server reboot!

---

## ⚙️ 4. Managing Tool Lifecycle

| Action | Method | Path | Description |
| :--- | :---: | :--- | :--- |
| **Browse Marketplace** | `GET` | `/api/v1/tools/marketplace` | List all discovered tools with filters |
| **View Tool Details** | `GET` | `/api/v1/tools/marketplace/{id}` | View schema, handler code & README |
| **Install / Enable** | `POST` | `/api/v1/tools/marketplace/{id}/install` | Enables tool for live agents |
| **Uninstall / Disable** | `POST` | `/api/v1/tools/marketplace/{id}/uninstall` | Unregisters tool dynamically |
| **Delete Tool** | `DELETE`| `/api/v1/tools/marketplace/{id}` | Permanently removes tool folder |

---

## 🤖 5. Using Marketplace Tools in Agents

Once installed, agents will automatically use your custom tool when relevant:

```bash
curl -X POST "http://localhost:8000/api/v1/agents/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Convert 500 USD to EUR and reverse the text hello world",
    "provider": "openrouter",
    "model": "gemini-3.7-flash",
    "tools": ["currency_converter", "text_reverser"]
  }'
```
