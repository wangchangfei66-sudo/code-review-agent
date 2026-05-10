"""Markdown report renderer."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from review_agent.models import Finding, ReviewResult, Severity


SEVERITY_LABELS = {
    Severity.HIGH: "🔴 High",
    Severity.MEDIUM: "🟠 Medium",
    Severity.LOW: "🟡 Low",
    Severity.INFO: "🔵 Info",
}


class MarkdownReporter:
    """Renders a review result to a Markdown report."""

    def render(self, result: ReviewResult) -> str:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lines = [
            "# Code Review Agent 报告",
            "",
            f"> 生成时间：{generated_at}",
            f"> 项目路径：`{result.project_path}`",
            "",
            "## 1. 总览",
            "",
            result.summary,
            "",
            "| 指标 | 数值 |",
            "|---|---:|",
        ]
        for key, value in result.metrics.items():
            lines.append(f"| {key} | {value} |")

        lines.extend([
            "",
            "## 2. 文件概况",
            "",
        ])
        by_language = Counter(item.language for item in result.files)
        if by_language:
            lines.extend(["| 语言 | 文件数 |", "|---|---:|"])
            for language, count in by_language.most_common():
                lines.append(f"| {language} | {count} |")
        else:
            lines.append("未找到可评审的源码文件。")

        lines.extend([
            "",
            "## 3. 发现的问题",
            "",
        ])
        if not result.findings:
            lines.append("未发现明显问题。")
        else:
            for finding in sorted(result.findings, key=lambda item: item.sort_key()):
                lines.extend(self._finding_block(finding))

        lines.extend([
            "",
            "## 4. 测试建议",
            "",
        ])
        for idx, suggestion in enumerate(result.test_suggestions, start=1):
            lines.append(f"{idx}. {suggestion}")

        lines.extend([
            "",
            "## 5. LLM 高阶审阅",
            "",
            result.llm_notes or "未启用 LLM 审阅。",
            "",
            "## 6. 推荐修复顺序",
            "",
            "1. 先修复 High 级别问题，尤其是语法错误、密钥泄露和静默吞异常。",
            "2. 再处理 Medium 级别问题，例如复杂函数、过宽异常捕获和潜在逻辑错误。",
            "3. 最后统一处理 Low/Info 级别的可读性、文档和风格问题。",
        ])
        return "\n".join(lines).rstrip() + "\n"

    def _finding_block(self, finding: Finding) -> list[str]:
        location = finding.file
        if finding.line is not None:
            location += f":{finding.line}"
        return [
            f"### {SEVERITY_LABELS[finding.severity]} · {finding.category}",
            "",
            f"- 位置：`{location}`",
            f"- 问题：{finding.message}",
            f"- 建议：{finding.suggestion}",
            "",
        ]
