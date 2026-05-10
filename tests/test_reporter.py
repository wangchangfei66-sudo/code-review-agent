from pathlib import Path

from review_agent.models import Finding, ReviewResult, Severity
from review_agent.reporters.markdown import MarkdownReporter


def test_markdown_report_contains_findings():
    result = ReviewResult(
        project_path=Path("."),
        findings=[
            Finding(
                file="main.py",
                line=1,
                severity=Severity.HIGH,
                category="security",
                message="bad",
                suggestion="fix it",
            )
        ],
        metrics={"files_reviewed": 1, "lines_reviewed": 1, "findings_total": 1},
        summary="summary text",
        test_suggestions=["add tests"],
    )

    report = MarkdownReporter().render(result)

    assert "Code Review Agent 报告" in report
    assert "main.py:1" in report
    assert "fix it" in report
