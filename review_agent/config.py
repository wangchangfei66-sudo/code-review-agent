"""Project configuration for the code review agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Set


DEFAULT_INCLUDE_EXTENSIONS: Set[str] = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".sql",
    ".html",
    ".css",
}

DEFAULT_EXCLUDED_DIRS: Set[str] = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    "target",
    ".venv",
    "venv",
    "env",
    ".idea",
    ".vscode",
    "coverage",
    "htmlcov",
}


@dataclass(frozen=True)
class ReviewConfig:
    """Configuration that controls file scanning and review behavior."""

    project_path: Path
    max_file_size_bytes: int = 120_000
    max_files: int = 200
    include_extensions: Set[str] = field(default_factory=lambda: set(DEFAULT_INCLUDE_EXTENSIONS))
    excluded_dirs: Set[str] = field(default_factory=lambda: set(DEFAULT_EXCLUDED_DIRS))
    use_llm: bool = False
    model: str = "gpt-4.1-mini"
    output_path: Path = Path("review_report.md")

    @classmethod
    def create(
        cls,
        project_path: str | Path,
        output_path: str | Path = "review_report.md",
        use_llm: bool = False,
        model: str = "gpt-4.1-mini",
        include_extensions: Iterable[str] | None = None,
        max_files: int = 200,
    ) -> "ReviewConfig":
        return cls(
            project_path=Path(project_path).expanduser().resolve(),
            output_path=Path(output_path).expanduser().resolve(),
            use_llm=use_llm,
            model=model,
            include_extensions=set(include_extensions or DEFAULT_INCLUDE_EXTENSIONS),
            max_files=max_files,
        )
