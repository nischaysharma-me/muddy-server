"""Boilerplate Generator for Marketplace Tools."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.tools.plugins.base import PluginManifest


def generate_tool_boilerplate(
    tool_id: str,
    name: Optional[str] = None,
    category: str = "utilities",
    description: str = "A custom tool for Muddy Server.",
    author: str = "Developer",
    tags: Optional[List[str]] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """Generates starter code and manifest files for a new marketplace tool."""

    clean_id = tool_id.lower().replace("-", "_").strip()
    tool_name = name or clean_id.replace("_", " ").title()
    tool_class_name = "".join(w.capitalize() for w in clean_id.split("_")) + "Tool"

    default_params = parameters or {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Primary input query or parameter",
            }
        },
        "required": ["query"],
    }

    manifest = PluginManifest(
        id=clean_id,
        name=tool_name,
        version="1.0.0",
        author=author,
        category=category,
        tags=tags or [category, "custom", "tool"],
        description=description,
        enabled=True,
        parameters=default_params,
        icon="⚡",
    )

    manifest_json = manifest.model_dump_json(indent=2)

    handler_py = f'''"""Implementation handler for {tool_name}."""

from typing import Any, Dict
from app.tools.plugins.base import BaseToolPlugin


class {tool_class_name}(BaseToolPlugin):
    """
    {description}
    """

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Executes the custom tool operation.
        """
        query = kwargs.get("query", "")

        # TODO: Implement your custom logic here
        result_message = f"Processed query: {{query}}"

        return {{
            "status": "success",
            "tool": "{clean_id}",
            "result": result_message,
        }}
'''

    test_tool_py = f'''"""Unit test for {tool_name}."""

import pytest
from app.tools.plugins.{clean_id}.handler import {tool_class_name}


@pytest.mark.asyncio
async def test_{clean_id}_execution():
    tool = {tool_class_name}()
    result = await tool.execute(query="Test Input")
    assert result["status"] == "success"
    assert "Test Input" in result["result"]
'''

    readme_md = f"""# {tool_name} 🛠️

{description}

---

## 📦 Metadata
- **Tool ID**: `{clean_id}`
- **Category**: `{category}`
- **Author**: `{author}`
- **Version**: `1.0.0`

---

## 🚀 Parameters Schema

```json
{json.dumps(default_params, indent=2)}
```

---

## 🧪 Testing Locally

```bash
uv run pytest app/tools/plugins/{clean_id}/test_tool.py -v
```
"""

    return {
        "manifest.json": manifest_json,
        "handler.py": handler_py,
        "test_tool.py": test_tool_py,
        "README.md": readme_md,
    }


def scaffold_tool_directory(
    target_dir: Path,
    tool_id: str,
    name: Optional[str] = None,
    category: str = "utilities",
    description: str = "A custom tool for Muddy Server.",
    author: str = "Developer",
    tags: Optional[List[str]] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> Path:
    """Scaffolds the tool files directly onto the local filesystem."""
    tool_folder = target_dir / tool_id.lower().replace("-", "_").strip()
    tool_folder.mkdir(parents=True, exist_ok=True)

    files = generate_tool_boilerplate(
        tool_id=tool_id,
        name=name,
        category=category,
        description=description,
        author=author,
        tags=tags,
        parameters=parameters,
    )

    for filename, content in files.items():
        (tool_folder / filename).write_text(content, encoding="utf-8")

    # Create empty __init__.py for clean module resolution
    (tool_folder / "__init__.py").write_text('"""Tool plugin package."""\n', encoding="utf-8")

    return tool_folder
