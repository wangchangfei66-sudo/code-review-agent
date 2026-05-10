"""Pipeline orchestration for the multi-agent code review system."""

from __future__ import annotations

from review_agent.agents.llm_review import LLMReviewAgent
from review_agent.agents.scanner import RepositoryScannerAgent
from review_agent.agents.static_analysis import StaticAnalysisAgent
from review_agent.agents.summary import SummaryAgent
from review_agent.agents.test_suggester import TestSuggestionAgent
from review_agent.config import ReviewConfig
from review_agent.models import ReviewResult
from review_agent.reporters.markdown import MarkdownReporter


class CodeReviewOrchestrator:
    """Coordinates scanner, analysis, test suggestion, optional LLM, and reporting agents."""

    def __init__(self, config: ReviewConfig) -> None:
        self.config = config
        self.scanner = RepositoryScannerAgent(config)
        self.static_analysis = StaticAnalysisAgent()
        self.test_suggester = TestSuggestionAgent()
        self.summary_agent = SummaryAgent()
        self.reporter = MarkdownReporter()

    def run(self) -> ReviewResult:
        files = self.scanner.run()
        findings = self.static_analysis.run(files)
        metrics = self.summary_agent.metrics(files, findings)
        summary = self.summary_agent.summary(metrics)
        test_suggestions = self.test_suggester.run(files, findings)
        llm_notes = ""
        if self.config.use_llm:
            llm_notes = LLMReviewAgent(model=self.config.model).run(files, findings)

        return ReviewResult(
            project_path=self.config.project_path,
            files=files,
            findings=findings,
            metrics=metrics,
            summary=summary,
            test_suggestions=test_suggestions,
            llm_notes=llm_notes,
        )

    def run_and_write_report(self) -> ReviewResult:
        result = self.run()
        report = self.reporter.render(result)
        self.config.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.config.output_path.write_text(report, encoding="utf-8")
        return result
