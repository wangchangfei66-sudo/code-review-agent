"""Agent that summarizes review metrics."""

from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable

from review_agent.models import Finding, SourceFile


class SummaryAgent:
    """Produces compact metrics and an executive summary."""

    name = "SummaryAgent"

    def metrics(self, files: Iterable[SourceFile], findings: Iterable[Finding]) -> Dict[str, int]:
        file_list = list(files)
        finding_list = list(findings)
        total_lines = sum(item.lines for item in file_list)
        by_severity = Counter(item.severity.value for item in finding_list)
        return {
            "files_reviewed": len(file_list),
            "lines_reviewed": total_lines,
            "findings_total": len(finding_list),
            "findings_high": by_severity.get("high", 0),
            "findings_medium": by_severity.get("medium", 0),
            "findings_low": by_severity.get("low", 0),
            "findings_info": by_severity.get("info", 0),
        }

    def summary(self, metrics: Dict[str, int]) -> str:
        if metrics["findings_total"] == 0:
            return "未发现明显问题。建议继续补充自动化测试和 README 使用说明。"
        risk = "低"
        if metrics["findings_high"]:
            risk = "高"
        elif metrics["findings_medium"]:
            risk = "中"
        return (
            f"本次共评审 {metrics['files_reviewed']} 个文件、{metrics['lines_reviewed']} 行代码，"
            f"发现 {metrics['findings_total']} 个问题。综合风险等级：{risk}。"
        )
