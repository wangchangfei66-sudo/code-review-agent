"""Small utility helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Optional


LANGUAGE_BY_EXTENSION = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript React",
    ".ts": "TypeScript",
    ".tsx": "TypeScript React",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
}


def detect_language(path: Path) -> str:
    """Return a friendly language name from a file extension."""

    return LANGUAGE_BY_EXTENSION.get(path.suffix.lower(), "Unknown")


def safe_read_text(path: Path, max_bytes: int) -> Optional[str]:
    """Read a UTF-8-ish source file safely.

    Returns None when the file is too large or cannot be decoded.
    """

    try:
        if path.stat().st_size > max_bytes:
            return None
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except OSError:
            return None
    except OSError:
        return None


def line_number_for_offset(text: str, offset: int) -> int:
    """Convert a character offset to a 1-based line number."""

    return text.count("\n", 0, offset) + 1
