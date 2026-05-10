from pathlib import Path

from review_agent.agents.scanner import RepositoryScannerAgent
from review_agent.config import ReviewConfig


def test_scanner_collects_python_file(tmp_path: Path):
    source = tmp_path / "main.py"
    source.write_text("print('hello')\n", encoding="utf-8")
    ignored = tmp_path / "node_modules"
    ignored.mkdir()
    (ignored / "x.py").write_text("print('ignore')\n", encoding="utf-8")

    config = ReviewConfig.create(tmp_path, output_path=tmp_path / "report.md")
    files = RepositoryScannerAgent(config).run()

    assert len(files) == 1
    assert files[0].relative_path == "main.py"
    assert files[0].language == "Python"
