"""Shared data models used by the agent pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class Severity(str, Enum):
    """Severity levels for a code review finding."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class SourceFile:
    """A source file selected for analysis."""

    path: Path
    relative_path: str
    language: str
    content: str
    lines: int
    size_bytes: int


@dataclass(frozen=True)
class Finding:
    """One actionable code review finding."""

    file: str
    line: Optional[int]
    severity: Severity
    category: str
    message: str
    suggestion: str

    def sort_key(self) -> tuple:
        order = {
            Severity.HIGH: 0,
            Severity.MEDIUM: 1,
            Severity.LOW: 2,
            Severity.INFO: 3,
        }
        return (order.get(self.severity, 99), self.file, self.line or 0, self.category)


@dataclass
class ReviewResult:
    """Complete output from all agents."""

    project_path: Path
    files: List[SourceFile] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)
    summary: str = ""
    metrics: Dict[str, int] = field(default_factory=dict)
    test_suggestions: List[str] = field(default_factory=list)
    llm_notes: str = ""

    @property
    def high_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == Severity.LOW)

    @property
    def info_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == Severity.INFO)
