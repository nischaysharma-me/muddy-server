"""JSON Formatter & Validator Plugin Handler."""

import json
from typing import Any, Dict
from app.tools.plugins.base import BaseToolPlugin


class JsonFormatterTool(BaseToolPlugin):
    """Formats, validates, and pretty-prints raw JSON strings."""

    async def execute(self, raw_json: str, indent: int = 2) -> Dict[str, Any]:
        try:
            parsed = json.loads(raw_json)
            formatted = json.dumps(parsed, indent=indent)
            return {
                "valid": True,
                "formatted_json": formatted,
                "keys_count": len(parsed) if isinstance(parsed, dict) else len(parsed) if isinstance(parsed, list) else 1,
            }
        except json.JSONDecodeError as err:
            return {
                "valid": False,
                "error": f"JSON Decode Error: {err.msg} at line {err.lineno}, column {err.colno}",
                "formatted_json": raw_json,
            }
