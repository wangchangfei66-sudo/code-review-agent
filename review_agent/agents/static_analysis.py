"""Static analysis agent with dependency-free checks.

The checks are intentionally explainable and conservative. They do not replace a
real linter, but they are useful for education-focused review reports.
"""

from __future__ import annotations

import ast
import re
from typing import Iterable, List

from review_agent.models import Finding, Severity, SourceFile
from review_agent.utils import line_number_for_offset


SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"(?i)bearer\s+[a-z0-9._\-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]

GENERIC_SMELLS = [
    (re.compile(r"\bprint\s*\("), "debug-output", "调试 print 可能不适合提交作业最终版。", "改用日志，或在最终提交前删除临时输出。"),
    (re.compile(r"\bconsole\.log\s*\("), "debug-output", "console.log 可能是临时调试代码。", "改用日志工具，或在最终提交前删除临时输出。"),
    (re.compile(r"\bTODO\b|\bFIXME\b", re.IGNORECASE), "unfinished-work", "代码中仍有 TODO/FIXME。", "把未完成事项转成 issue，或在报告里说明为什么保留。"),
]


class StaticAnalysisAgent:
    """Runs language-aware and generic static checks."""

    name = "StaticAnalysisAgent"

    def run(self, files: Iterable[SourceFile]) -> List[Finding]:
        findings: List[Finding] = []
        for source in files:
            findings.extend(self._generic_checks(source))
            if source.path.suffix.lower() == ".py":
                findings.extend(self._python_checks(source))
            if source.path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx"}:
                findings.extend(self._javascript_checks(source))
        return sorted(findings, key=lambda item: item.sort_key())

    def _generic_checks(self, source: SourceFile) -> List[Finding]:
        findings: List[Finding] = []
        lines = source.content.splitlines()

        for idx, line in enumerate(lines, start=1):
            if len(line) > 120:
                findings.append(
                    Finding(
                        file=source.relative_path,
                        line=idx,
                        severity=Severity.LOW,
                        category="readability",
                        message="单行代码过长，阅读和评审成本较高。",
                        suggestion="拆分表达式，或把复杂逻辑提取成有名字的中间变量。",
                    )
                )
            if line.rstrip() != line:
                findings.append(
                    Finding(
                        file=source.relative_path,
                        line=idx,
                        severity=Severity.INFO,
                        category="style",
                        message="存在行尾空格。",
                        suggestion="开启编辑器保存时自动去除 trailing whitespace。",
                    )
                )

        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(source.content):
                findings.append(
                    Finding(
                        file=source.relative_path,
                        line=line_number_for_offset(source.content, match.start()),
                        severity=Severity.HIGH,
                        category="security",
                        message="疑似硬编码密钥、令牌或密码。",
                        suggestion="立刻撤销已提交的密钥，并改用环境变量或密钥管理服务。",
                    )
                )

        for pattern, category, message, suggestion in GENERIC_SMELLS:
            for match in pattern.finditer(source.content):
                findings.append(
                    Finding(
                        file=source.relative_path,
                        line=line_number_for_offset(source.content, match.start()),
                        severity=Severity.LOW,
                        category=category,
                        message=message,
                        suggestion=suggestion,
                    )
                )
        return findings

    def _python_checks(self, source: SourceFile) -> List[Finding]:
        findings: List[Finding] = []
        try:
            tree = ast.parse(source.content)
        except SyntaxError as exc:
            return [
                Finding(
                    file=source.relative_path,
                    line=exc.lineno,
                    severity=Severity.HIGH,
                    category="syntax",
                    message=f"Python 语法错误：{exc.msg}",
                    suggestion="先修复语法错误，再运行测试和进一步评审。",
                )
            ]

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                findings.extend(self._check_python_function(source, node))
            elif isinstance(node, ast.Try):
                findings.extend(self._check_python_try(source, node))
            elif isinstance(node, ast.Call):
                findings.extend(self._check_python_call(source, node))
            elif isinstance(node, ast.ImportFrom):
                if node.module == "typing" and any(alias.name == "Any" for alias in node.names):
                    findings.append(
                        Finding(
                            file=source.relative_path,
                            line=getattr(node, "lineno", None),
                            severity=Severity.INFO,
                            category="typing",
                            message="使用了 Any，可能削弱类型检查效果。",
                            suggestion="能明确类型时，优先写具体类型；确实动态时再保留 Any。",
                        )
                    )
        return findings

    def _check_python_function(self, source: SourceFile, node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[Finding]:
        findings: List[Finding] = []
        length = (getattr(node, "end_lineno", node.lineno) or node.lineno) - node.lineno + 1
        arg_count = len(node.args.args) + len(node.args.kwonlyargs)

        if length > 50:
            findings.append(
                Finding(
                    file=source.relative_path,
                    line=node.lineno,
                    severity=Severity.MEDIUM,
                    category="complexity",
                    message=f"函数 `{node.name}` 约 {length} 行，可能承担了过多职责。",
                    suggestion="按“输入处理 / 核心计算 / 输出格式化”拆成更小函数。",
                )
            )
        if arg_count > 6:
            findings.append(
                Finding(
                    file=source.relative_path,
                    line=node.lineno,
                    severity=Severity.MEDIUM,
                    category="design",
                    message=f"函数 `{node.name}` 参数较多，调用方容易传错。",
                    suggestion="考虑使用 dataclass、配置对象或拆分函数职责。",
                )
            )
        if ast.get_docstring(node) is None and not node.name.startswith("_"):
            findings.append(
                Finding(
                    file=source.relative_path,
                    line=node.lineno,
                    severity=Severity.LOW,
                    category="documentation",
                    message=f"公开函数 `{node.name}` 缺少 docstring。",
                    suggestion="补充输入、输出、异常和边界条件说明。",
                )
            )
        return findings

    def _check_python_try(self, source: SourceFile, node: ast.Try) -> List[Finding]:
        findings: List[Finding] = []
        for handler in node.handlers:
            is_broad = handler.type is None or (
                isinstance(handler.type, ast.Name) and handler.type.id in {"Exception", "BaseException"}
            )
            if is_broad:
                findings.append(
                    Finding(
                        file=source.relative_path,
                        line=handler.lineno,
                        severity=Severity.MEDIUM,
                        category="error-handling",
                        message="捕获了过宽的异常，可能隐藏真实 bug。",
                        suggestion="捕获更具体的异常，并记录足够的错误上下文。",
                    )
                )
            if not handler.body or all(isinstance(stmt, ast.Pass) for stmt in handler.body):
                findings.append(
                    Finding(
                        file=source.relative_path,
                        line=handler.lineno,
                        severity=Severity.HIGH,
                        category="error-handling",
                        message="异常被静默吞掉，出错时很难定位。",
                        suggestion="至少记录异常，或把异常转换成有业务含义的错误。",
                    )
                )
        return findings

    def _check_python_call(self, source: SourceFile, node: ast.Call) -> List[Finding]:
        findings: List[Finding] = []
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
            findings.append(
                Finding(
                    file=source.relative_path,
                    line=node.lineno,
                    severity=Severity.HIGH,
                    category="security",
                    message=f"使用 `{node.func.id}` 执行动态代码，风险很高。",
                    suggestion="改用安全解析方式，例如 ast.literal_eval、白名单映射或显式函数调用。",
                )
            )
        return findings

    def _javascript_checks(self, source: SourceFile) -> List[Finding]:
        findings: List[Finding] = []
        checks = [
            (
                re.compile(r"\bvar\s+\w+"),
                Severity.LOW,
                "modern-js",
                "使用了 var，容易产生作用域问题。",
                "优先使用 const；需要重新赋值时使用 let。",
            ),
            (
                re.compile(r"==(?!=)"),
                Severity.MEDIUM,
                "correctness",
                "使用了非严格相等 ==，可能发生隐式类型转换。",
                "改用 === 或显式转换后比较。",
            ),
            (
                re.compile(r"\bany\b"),
                Severity.INFO,
                "typing",
                "TypeScript 中 any 会降低类型保护。",
                "尽量写明确接口或使用 unknown 后做类型收窄。",
            ),
        ]
        for pattern, severity, category, message, suggestion in checks:
            for match in pattern.finditer(source.content):
                findings.append(
                    Finding(
                        file=source.relative_path,
                        line=line_number_for_offset(source.content, match.start()),
                        severity=severity,
                        category=category,
                        message=message,
                        suggestion=suggestion,
                    )
                )
        return findings
