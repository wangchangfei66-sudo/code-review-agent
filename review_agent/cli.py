"""Command-line interface for Code Review Agent."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from review_agent.config import ReviewConfig
from review_agent.orchestrator import CodeReviewOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code-review-agent",
        description="Multi-agent code review assistant for programming assignments.",
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Path to a project directory or one source file. Default: current directory.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="reports/review_report.md",
        help="Markdown report output path. Default: reports/review_report.md",
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Enable optional OpenAI-powered high-level review. Requires OPENAI_API_KEY.",
    )
    parser.add_argument(
        "--model",
        default="gpt-4.1-mini",
        help="Model name used when --use-llm is enabled.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=200,
        help="Maximum number of files to review. Default: 200.",
    )
    parser.add_argument(
        "--ext",
        nargs="*",
        default=None,
        help="File extensions to include, e.g. --ext .py .js .ts",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = ReviewConfig.create(
        project_path=Path(args.project_path),
        output_path=Path(args.output),
        use_llm=args.use_llm,
        model=args.model,
        include_extensions=args.ext,
        max_files=args.max_files,
    )
    orchestrator = CodeReviewOrchestrator(config)

    try:
        result = orchestrator.run_and_write_report()
    except Exception as exc:
        print(f"❌ Review failed: {exc}", file=sys.stderr)
        return 1

    print("✅ Code review completed")
    print(f"Reviewed files: {result.metrics['files_reviewed']}")
    print(f"Findings: {result.metrics['findings_total']}")
    print(f"Report: {config.output_path}")
    if result.high_count:
        print("⚠️  High severity findings detected. Please fix them first.")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
