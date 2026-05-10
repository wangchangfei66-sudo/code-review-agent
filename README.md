# Code Review Agent：编程作业 / 代码评审多 Agent 系统

这是一个可以直接上传到 GitHub 的完整 Python 项目。它面向学生编程作业、课程项目和个人练习，提供自动化代码扫描、静态评审、测试建议和 Markdown 报告生成。

项目默认可以离线运行，不强制依赖 OpenAI API。设置 `OPENAI_API_KEY` 并添加 `--use-llm` 后，可以启用可选的 LLM 高阶审阅 Agent。

## 项目亮点

- **多 Agent 协作流程**：扫描 Agent、静态分析 Agent、测试建议 Agent、总结 Agent、可选 LLM Review Agent。
- **适合学校项目展示**：能清楚说明“解决了什么痛点、Agent 怎么协作、最终产出什么结果”。
- **可量化成果**：自动生成代码质量报告，能统计文件数、行数、问题数、严重程度分布。
- **无需复杂环境**：核心功能只用 Python 标准库即可运行。
- **GitHub 友好**：包含 `pyproject.toml`、测试用例、GitHub Actions、示例项目、MIT License。

## 解决的核心痛点

在编程作业或课程项目中，学生常常需要手动检查：

1. 是否有语法错误、危险函数、硬编码密钥；
2. 是否有过长函数、过宽异常捕获、静默吞异常；
3. 是否遗留 `print`、`console.log`、`TODO/FIXME`；
4. 是否需要补充边界值、异常路径、回归测试。

这个 Agent 把这些重复工作自动化，并输出结构化 Markdown 报告，方便提交、复盘或作为课程项目成果展示。

## 核心逻辑流

```text
项目目录 / 单个代码文件
        │
        ▼
RepositoryScannerAgent
扫描源码文件，过滤 node_modules、.git、venv 等无关目录
        │
        ▼
StaticAnalysisAgent
执行 Python / JavaScript / TypeScript 等规则检查
        │
        ▼
TestSuggestionAgent
根据问题类型生成测试建议
        │
        ▼
SummaryAgent
汇总文件数、行数、问题数、风险等级
        │
        ▼
LLMReviewAgent（可选）
基于 OPENAI_API_KEY 生成高阶代码审阅建议
        │
        ▼
MarkdownReporter
输出 review_report.md
```

## 快速开始

### 1. 克隆或下载项目

```bash
git clone https://github.com/your-name/code-review-agent.git
cd code-review-agent
```

如果你是直接下载 zip，解压后进入项目目录即可。

### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
# Windows: .venv\Scripts\activate
```

### 3. 安装项目

```bash
pip install -e .
```

开发模式安装测试依赖：

```bash
pip install -e .[dev]
```

### 4. 运行示例

```bash
code-review-agent examples/buggy_student_project -o reports/example_report.md
```

你也可以直接用 Python 模块运行：

```bash
python -m review_agent.cli examples/buggy_student_project -o reports/example_report.md
```

生成后查看：

```bash
cat reports/example_report.md
```

## 扫描自己的作业项目

```bash
code-review-agent /path/to/your/homework -o reports/homework_review.md
```

只扫描 Python 文件：

```bash
code-review-agent /path/to/your/homework --ext .py -o reports/python_review.md
```

设置最多扫描文件数：

```bash
code-review-agent /path/to/your/homework --max-files 80
```

## 启用可选 LLM 审阅

核心扫描不需要 API key。若你希望让 LLM 生成更高阶的设计建议，可以这样做：

```bash
pip install -e .[llm]
export OPENAI_API_KEY="你的 API key"
code-review-agent examples/buggy_student_project --use-llm -o reports/llm_report.md
```

Windows PowerShell：

```powershell
$env:OPENAI_API_KEY="你的 API key"
code-review-agent examples/buggy_student_project --use-llm -o reports/llm_report.md
```

可以通过 `--model` 指定模型：

```bash
code-review-agent . --use-llm --model gpt-4.1-mini
```

## 项目结构

```text
code-review-agent/
├── review_agent/
│   ├── agents/
│   │   ├── scanner.py           # 仓库扫描 Agent
│   │   ├── static_analysis.py   # 静态规则分析 Agent
│   │   ├── test_suggester.py    # 测试建议 Agent
│   │   ├── summary.py           # 汇总 Agent
│   │   └── llm_review.py        # 可选 LLM Review Agent
│   ├── reporters/
│   │   └── markdown.py          # Markdown 报告生成
│   ├── cli.py                   # 命令行入口
│   ├── config.py                # 配置
│   ├── models.py                # 数据模型
│   ├── orchestrator.py          # 多 Agent 编排
│   └── utils.py                 # 工具函数
├── examples/
│   └── buggy_student_project/   # 故意带问题的示例项目
├── tests/                       # 单元测试
├── .github/workflows/           # GitHub Actions
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

## 当前内置检查规则

### 通用规则

- 疑似硬编码 API key、token、password；
- 行尾空格；
- 单行代码过长；
- `TODO` / `FIXME`；
- 调试输出：`print(...)`、`console.log(...)`。

### Python 规则

- 语法错误；
- `eval` / `exec` 动态执行；
- 公开函数缺少 docstring；
- 函数过长；
- 函数参数过多；
- 捕获过宽异常；
- `except: pass` 或静默吞异常；
- 过度使用 `typing.Any`。

### JavaScript / TypeScript 规则

- 使用 `var`；
- 使用 `==` 而不是 `===`；
- 使用 `any`；
- 遗留 `console.log`。

## 运行测试

```bash
pip install -e .[dev]
pytest
ruff check .
```

## 示例成果描述

可以把下面这段放到学校系统、项目申请、课程报告或 GitHub README 里：

> 我构建了一个面向编程作业和课程项目的 Code Review Agent，用来解决代码调试耗时、错误定位困难和代码规范不统一的问题。系统采用多 Agent 协作流程：RepositoryScannerAgent 负责扫描项目目录并过滤无关文件；StaticAnalysisAgent 负责检查语法错误、硬编码密钥、异常处理、复杂函数和调试输出；TestSuggestionAgent 根据发现的问题自动生成测试建议；SummaryAgent 汇总风险等级和问题分布；LLMReviewAgent 可在设置 API key 后生成更高阶的重构建议。实际使用中，它可以在几十秒内完成一次课程项目的初步评审，自动输出 Markdown 报告，帮助我优先修复高风险问题，并补充边界值和异常路径测试。

## 后续可扩展方向

- 接入真实 lint 工具，例如 Ruff、ESLint、mypy；
- 支持 Git diff，只评审本次改动；
- 增加 Web UI；
- 生成 PR Review 评论；
- 加入 RAG，读取课程规范或教师评分 rubrics 后定制评审标准；
- 对单元测试覆盖率进行自动分析。

## License

MIT
