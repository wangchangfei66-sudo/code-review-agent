"""Repository scanning agent."""

from __future__ import annotations

from pathlib import Path
from typing import List

from review_agent.config import ReviewConfig
from review_agent.models import SourceFile
from review_agent.utils import detect_language, safe_read_text


class RepositoryScannerAgent:
    """Finds reviewable source files in a project directory."""

    name = "RepositoryScannerAgent"

    def __init__(self, config: ReviewConfig) -> None:
        self.config = config

    def run(self) -> List[SourceFile]:
        project_path = self.config.project_path
        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        if project_path.is_file():
            paths = [project_path]
            root = project_path.parent
        else:
            paths = sorted(self._iter_source_paths(project_path))
            root = project_path

        files: List[SourceFile] = []
        for path in paths[: self.config.max_files]:
            content = safe_read_text(path, self.config.max_file_size_bytes)
            if content is None:
                continue
            relative_path = str(path.relative_to(root)) if path.is_relative_to(root) else path.name
            files.append(
                SourceFile(
                    path=path,
                    relative_path=relative_path,
                    language=detect_language(path),
                    content=content,
                    lines=len(content.splitlines()),
                    size_bytes=path.stat().st_size,
                )
            )
        return files

    def _iter_source_paths(self, root: Path):
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in self.config.excluded_dirs for part in path.parts):
                continue
            if path.suffix.lower() not in self.config.include_extensions:
                continue
            yield path
