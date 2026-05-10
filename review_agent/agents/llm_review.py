"""Optional LLM review agent.

The project works without this file being used. When the user passes --use-llm
and sets OPENAI_API_KEY, this agent asks a model for higher-level design notes.
"""

from __future__ import annotations

import os
from textwrap import shorten
from typing import Iterable

from review_agent.models import Finding, SourceFile


class LLMReviewAgent:
    """Adds an optional AI-powered high-level review summary."""

    name = "LLMReviewAgent"

    def __init__(self, model: str) -> None:
        self.model = model

    def run(self, files: Iterable[SourceFile], findings: Iterable[Finding]) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "未启用 LLM：没有检测到 OPENAI_API_KEY。"

        prompt = self._build_prompt(files, findings)
        try:
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model=self.model,
                input=prompt,
            )
            return getattr(response, "output_text", "") or "LLM 未返回可读文本。"
        except ImportError:
            return "未安装 openai 包。请运行：pip install -e .[llm]"
        except Exception as exc:  # pragma: no cover - network/API errors vary
            return f"LLM 审阅失败：{exc}"

    def _build_prompt(self, files: Iterable[SourceFile], findings: Iterable[Finding]) -> str:
        file_block = []
        for source in list(files)[:8]:
            snippet = shorten(source.content.replace("\n", " "), width=1500, placeholder=" ...")
            file_block.append(f"FILE: {source.relative_path}\nLANGUAGE: {source.language}\nCODE_SNIPPET:\n{snippet}")

        finding_block = "\n".join(
            f"- {item.severity.value.upper()} {item.file}:{item.line or '-'} "
            f"[{item.category}] {item.message} 建议：{item.suggestion}"
            for item in list(findings)[:30]
        )

        return f"""
你是一个面向学生编程作业的代码评审 Agent。请用中文输出：
1. 总体评价；
2. 最需要优先修复的 3 个问题；
3. 可执行的重构建议；
4. 建议补充的测试。

已有静态扫描发现：
{finding_block or "暂无"}

代码片段：
{chr(10).join(file_block)}
""".strip()
