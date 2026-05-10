from pathlib import Path

from review_agent.agents.static_analysis import StaticAnalysisAgent
from review_agent.models import Severity, SourceFile


def make_source(content: str) -> SourceFile:
    return SourceFile(
        path=Path("sample.py"),
        relative_path="sample.py",
        language="Python",
        content=content,
        lines=len(content.splitlines()),
        size_bytes=len(content.encode()),
    )


def test_detects_eval_and_secret():
    source = make_source('API_KEY = "sk-demo-123456789"\n\ndef run(x):\n    return eval(x)\n')
    findings = StaticAnalysisAgent().run([source])

    categories = {item.category for item in findings}
    severities = {item.severity for item in findings}

    assert "security" in categories
    assert Severity.HIGH in severities


def test_detects_python_syntax_error():
    source = make_source("def broken(:\n    pass\n")
    findings = StaticAnalysisAgent().run([source])

    assert findings[0].category == "syntax"
    assert findings[0].severity == Severity.HIGH
