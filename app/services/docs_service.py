"""Documentation Reader and Tree Indexing Service."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.config import settings
from app.core.exceptions import FeatureDisabledError
from app.services.base_service import BaseService


class DocsService(BaseService):
    """Parses, indexes, and serves markdown documentation files."""

    def __init__(self, docs_dir: Optional[str] = None):
        super().__init__("DocsService")
        # Find docs folder relative to project root
        self.docs_dir = Path(docs_dir) if docs_dir else Path(__file__).resolve().parent.parent.parent / "docs"

    def get_documentation_tree(self) -> List[Dict[str, Any]]:
        """Returns recursive hierarchical tree of all markdown documentation."""
        if not settings.ENABLE_DOCS_ENGINE:
            raise FeatureDisabledError("DOCS_ENGINE")

        if not self.docs_dir.exists():
            return []

        tree = []
        for folder in sorted(self.docs_dir.iterdir()):
            if folder.is_dir() and not folder.name.startswith("."):
                section_item = {
                    "section": folder.name,
                    "title": folder.name.replace("-", " ").title(),
                    "files": [],
                }
                for doc_file in sorted(folder.glob("*.md")):
                    title = self._extract_title(doc_file)
                    section_item["files"].append({
                        "name": doc_file.stem,
                        "filename": doc_file.name,
                        "title": title,
                        "path": f"/api/v1/docs/{folder.name}/{doc_file.stem}",
                    })
                tree.append(section_item)
        return tree

    def get_document(self, section: str, doc_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves raw content and metadata for a specific markdown document."""
        if not settings.ENABLE_DOCS_ENGINE:
            raise FeatureDisabledError("DOCS_ENGINE")

        clean_name = doc_name if doc_name.endswith(".md") else f"{doc_name}.md"
        doc_path = self.docs_dir / section / clean_name

        if not doc_path.exists() or not doc_path.is_file():
            return None

        content = doc_path.read_text(encoding="utf-8")
        title = self._extract_title(doc_path)

        return {
            "section": section,
            "name": doc_name.replace(".md", ""),
            "title": title,
            "content": content,
            "path": str(doc_path),
        }

    def _extract_title(self, file_path: Path) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line_clean = line.strip()
                    if line_clean.startswith("# "):
                        return line_clean[2:].strip()
        except Exception:
            pass
        return file_path.stem.replace("-", " ").title()


docs_service = DocsService()
