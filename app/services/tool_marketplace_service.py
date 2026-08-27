"""Tool Marketplace and Dynamic Plugin Management Service."""

import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.core.exceptions import ToolExecutionError
from app.core.logging import logger
from app.services.base_service import BaseService
from app.tools.plugins.base import BaseToolPlugin, PluginManifest
from app.tools.plugins.generator import (
    generate_tool_boilerplate,
    scaffold_tool_directory,
)
from app.tools.registry import ToolDefinition, registry


class ToolMarketplaceService(BaseService):
    """Orchestrates plugin discovery, boilerplate scaffolding, dynamic registration, and marketplace catalog."""

    def __init__(self, plugins_dir: Optional[Path] = None):
        super().__init__("ToolMarketplaceService")
        self.plugins_dir = (
            plugins_dir
            if plugins_dir
            else Path(__file__).resolve().parent.parent / "tools" / "plugins"
        )
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self._installed_plugins: Dict[str, BaseToolPlugin] = {}
        self._manifests: Dict[str, PluginManifest] = {}

    def discover_and_register_all(self) -> int:
        """Scans plugins directory, loads manifests, and registers active tools in ToolRegistry."""
        count = 0
        if not self.plugins_dir.exists():
            return count

        for tool_folder in sorted(self.plugins_dir.iterdir()):
            if not tool_folder.is_dir() or tool_folder.name.startswith((".", "_")):
                continue

            manifest_path = tool_folder / "manifest.json"
            handler_path = tool_folder / "handler.py"

            if not manifest_path.exists() or not handler_path.exists():
                continue

            try:
                manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest = PluginManifest(**manifest_data)
                self._manifests[manifest.id] = manifest

                if manifest.enabled:
                    self._load_and_register_plugin(tool_folder, manifest)
                    count += 1
            except Exception as e:
                logger.error(f"[Marketplace] Failed loading plugin '{tool_folder.name}': {e}")

        logger.info(f"🏪 [Marketplace] Discovered and registered {count} marketplace tool plugins.")
        return count

    def _load_and_register_plugin(self, folder: Path, manifest: PluginManifest) -> Optional[BaseToolPlugin]:
        """Dynamically imports the tool handler and registers it in ToolRegistry."""
        handler_path = folder / "handler.py"
        module_name = f"app.tools.plugins.{manifest.id}.handler"

        try:
            spec = importlib.util.spec_from_file_location(module_name, str(handler_path))
            if not spec or not spec.loader:
                raise ImportError(f"Cannot create module spec for {handler_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find class that inherits from BaseToolPlugin
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseToolPlugin)
                    and attr is not BaseToolPlugin
                ):
                    plugin_class = attr
                    break

            if not plugin_class:
                raise ValueError(f"No BaseToolPlugin subclass found in {handler_path}")

            plugin_instance = plugin_class(manifest=manifest)
            self._installed_plugins[manifest.id] = plugin_instance

            # Register in ToolRegistry
            async def _dynamic_wrapper(**kwargs):
                return await plugin_instance.execute(**kwargs)

            # Assign docstring and name
            _dynamic_wrapper.__doc__ = manifest.description
            _dynamic_wrapper.__name__ = manifest.id

            registry._tools[manifest.id] = _dynamic_wrapper
            registry._metadata[manifest.id] = ToolDefinition(
                name=manifest.id,
                description=manifest.description,
                parameters_schema=manifest.parameters,
                category=manifest.category,
            )

            logger.debug(f"✅ [Marketplace] Successfully hot-loaded tool: '{manifest.id}'")
            return plugin_instance
        except Exception as e:
            logger.error(f"[Marketplace] Error registering tool '{manifest.id}': {e}")
            return None

    def list_marketplace_tools(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Returns catalog of all marketplace tools."""
        self.discover_and_register_all()
        results = []

        for tool_id, manifest in self._manifests.items():
            if category and manifest.category.lower() != category.lower():
                continue
            if tag and tag.lower() not in [t.lower() for t in manifest.tags]:
                continue
            if search:
                query = search.lower()
                matches = (
                    query in manifest.name.lower()
                    or query in manifest.description.lower()
                    or any(query in t.lower() for t in manifest.tags)
                )
                if not matches:
                    continue

            is_active = tool_id in registry._tools and manifest.enabled
            results.append({
                "id": manifest.id,
                "name": manifest.name,
                "version": manifest.version,
                "author": manifest.author,
                "category": manifest.category,
                "tags": manifest.tags,
                "description": manifest.description,
                "enabled": manifest.enabled,
                "is_active": is_active,
                "icon": manifest.icon,
                "parameters": manifest.parameters,
                "env_vars": manifest.env_vars,
            })

        return sorted(results, key=lambda x: x["name"])

    def get_tool_detail(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Returns full metadata, README, and code preview for a specific tool."""
        folder = self.plugins_dir / tool_id
        manifest_path = folder / "manifest.json"
        if not manifest_path.exists():
            return None

        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        readme_path = folder / "README.md"
        readme_content = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
        handler_path = folder / "handler.py"
        handler_code = handler_path.read_text(encoding="utf-8") if handler_path.exists() else ""

        return {
            "manifest": manifest_data,
            "readme": readme_content,
            "handler_code": handler_code,
            "is_active": tool_id in registry._tools,
        }

    def scaffold_new_tool(
        self,
        tool_id: str,
        name: Optional[str] = None,
        category: str = "utilities",
        description: str = "Custom marketplace tool for Muddy Server.",
        author: str = "Developer",
        tags: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Creates a complete boilerplate folder for a new tool."""
        clean_id = tool_id.lower().replace("-", "_").strip()
        folder = scaffold_tool_directory(
            target_dir=self.plugins_dir,
            tool_id=clean_id,
            name=name,
            category=category,
            description=description,
            author=author,
            tags=tags,
            parameters=parameters,
        )
        self.discover_and_register_all()
        return {
            "tool_id": clean_id,
            "path": str(folder),
            "status": "created",
            "message": f"Tool '{clean_id}' scaffolded successfully and registered.",
        }

    def install_tool(self, tool_id: str) -> bool:
        """Enables and hot-loads a tool into the live ToolRegistry."""
        folder = self.plugins_dir / tool_id
        manifest_path = folder / "manifest.json"
        if not manifest_path.exists():
            raise ToolExecutionError(f"Marketplace tool '{tool_id}' not found.")

        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_data["enabled"] = True
        manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

        manifest = PluginManifest(**manifest_data)
        self._manifests[tool_id] = manifest
        self._load_and_register_plugin(folder, manifest)
        return True

    def uninstall_tool(self, tool_id: str) -> bool:
        """Disables and removes a tool from the live ToolRegistry."""
        folder = self.plugins_dir / tool_id
        manifest_path = folder / "manifest.json"
        if not manifest_path.exists():
            raise ToolExecutionError(f"Marketplace tool '{tool_id}' not found.")

        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_data["enabled"] = False
        manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

        manifest = PluginManifest(**manifest_data)
        self._manifests[tool_id] = manifest

        # Remove from ToolRegistry
        registry._tools.pop(tool_id, None)
        registry._metadata.pop(tool_id, None)
        self._installed_plugins.pop(tool_id, None)
        return True

    def upload_custom_tool(
        self,
        tool_id: str,
        manifest_dict: Dict[str, Any],
        handler_code: str,
        readme_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Saves, validates, and activates a custom tool bundle."""
        clean_id = tool_id.lower().replace("-", "_").strip()
        manifest_dict["id"] = clean_id
        manifest_dict["enabled"] = True

        manifest = PluginManifest(**manifest_dict)
        folder = self.plugins_dir / clean_id
        folder.mkdir(parents=True, exist_ok=True)

        (folder / "manifest.json").write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        (folder / "handler.py").write_text(handler_code, encoding="utf-8")
        (folder / "__init__.py").write_text('"""Custom uploaded plugin."""\n', encoding="utf-8")

        if readme_content:
            (folder / "README.md").write_text(readme_content, encoding="utf-8")

        self._load_and_register_plugin(folder, manifest)
        self._manifests[clean_id] = manifest

        return {
            "tool_id": clean_id,
            "status": "installed",
            "message": f"Custom tool '{clean_id}' uploaded and activated successfully.",
        }

    def delete_custom_tool(self, tool_id: str) -> bool:
        """Deletes a custom tool from the filesystem and removes from registry."""
        folder = self.plugins_dir / tool_id
        if not folder.exists():
            return False

        self.uninstall_tool(tool_id)
        shutil.rmtree(folder, ignore_errors=True)
        self._manifests.pop(tool_id, None)
        return True


tool_marketplace_service = ToolMarketplaceService()
