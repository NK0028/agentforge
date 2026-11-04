import os
import logging
from typing import List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class WorkspaceService:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.sandbox_path = os.path.abspath(os.path.join(settings.WORKSPACE_DIR, project_id))
        os.makedirs(self.sandbox_path, exist_ok=True)

    def write_file(self, relative_path: str, content: str) -> str:
        """
        Safely writes file content inside project sandbox.
        Prevents path traversal outside sandbox_path.
        """
        # Clean leading slashes
        clean_rel_path = relative_path.lstrip("/\\")
        target_path = os.path.abspath(os.path.join(self.sandbox_path, clean_rel_path))

        # Security check: Ensure target_path starts with sandbox_path
        if not target_path.startswith(self.sandbox_path):
            raise ValueError(f"Path traversal security violation: {relative_path}")

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Successfully wrote file: {clean_rel_path}")
        return clean_rel_path

    def list_files(self) -> List[Dict[str, Any]]:
        """
        Recursively lists all files in the project workspace sandbox.
        """
        files = []
        if not os.path.exists(self.sandbox_path):
            return files

        for root, _, filenames in os.walk(self.sandbox_path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, self.sandbox_path)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    files.append({"path": rel_path, "content": content})
                except Exception as e:
                    logger.error(f"Error reading {rel_path}: {e}")
        return files
