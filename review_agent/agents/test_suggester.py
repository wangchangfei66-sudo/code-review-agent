"""Agent that suggests useful tests from the current findings and files."""

from __future__ import annotations

from collections import Counter
from typing import Iterable, List

from review_agent.models import Finding, SourceFile


class TestSuggestionAgent:
    """Creates testing advice for programming assignments."""

    name = "TestSuggestionAgent"

    def run(self, files: Iterable[SourceFile], findings: Iterable[Finding]) -> List[str]:
        file_list = list(files)
        finding_list = list(findings)
        languages = Counter(item.language for item in file_list)
        categories = Counter(item.category for item in finding_list)
        suggestions: List[str] = []

        if languages.get("Python", 0):
            suggestions.append("为每个公开函数补充 pytest 单元测试，覆盖正常输入、空输入和异常输入。")
            suggestions.append("为文件读写、网络请求等副作用逻辑增加 mock 测试，避免测试依赖真实环境。")
        if languages.get("JavaScript", 0) or languages.get("TypeScript", 0):
            suggestions.append("使用 Vitest/Jest 覆盖核心函数，并检查异步函数的成功与失败路径。")
        if categories.get("security", 0):
            suggestions.append("新增安全回归测试，确保不会把密钥、token 或密码写入日志、报告和仓库。")
        if categories.get("error-handling", 0):
            suggestions.append("构造失败输入，测试异常是否被正确抛出、记录或转换成用户可理解的错误。")
        if categories.get("complexity", 0) or categories.get("design", 0):
            suggestions.append("拆分复杂函数后，为每个小函数写针对性测试，防止重构改变原有行为。")
        if not suggestions:
            suggestions.append("至少准备一组 happy path、一组边界值、一组非法输入测试，证明代码不是只在样例上可运行。")

        return suggestions
