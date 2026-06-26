# AI Agent 学习仓库

> 2 个月系统掌握 AI Agent 应用开发，从 LLM API 到 RAG 知识库再到完整 Agent 项目。

## 项目简介

本仓库是 AI 应用 / Agent 开发学习与职业准备空间，目标是帮助系统掌握 AI 应用开发中的 Agent 开发能力。

## 核心项目

### dev-knowledge-agent

面向技术学习和代码仓库探索的智能体知识库 Agent API。

**技术栈**：
- FastAPI
- LangChain 1.x
- OpenAI API（兼容 DeepSeek）

**已实现功能**：
- LLM 聊天接口（普通 / 结构化输出 / 流式）
- Prompt 外置管理
- 日志中间件 + trace_id
- 统一异常处理

## 学习进度

### Week 1：工程化基础 ✅

| Day | 主题 | 状态 |
|---|---|---|
| Day 1 | FastAPI 骨架搭建 | ✅ |
| Day 2 | LLM API 接入 | ✅ |
| Day 3 | Prompt 外置 | ✅ |
| Day 4 | Structured Output | ✅ |
| Day 5 | 流式响应 SSE | ✅ |
| Day 6 | 中间件 + 异常处理 | ✅ |

### Week 2：RAG 知识库

进行中...

## 目录结构

```text
.
├── dev-knowledge-agent/    # 主项目
│   ├── app/
│   │   ├── api/           # 路由层
│   │   ├── core/          # 核心配置、中间件、异常
│   │   ├── prompts/       # Prompt 模板
│   │   ├── schemas/       # 数据模型
│   │   └── services/      # 业务逻辑
│   └── pyproject.toml
├── docs/
│   └── notes/             # 学习笔记
├── 岗位JD.md              # 岗位 JD 汇总
└── CLAUDE.md              # 项目协作规范
```

## 快速开始

```bash
# 进入项目目录
cd dev-knowledge-agent

# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY

# 启动服务
uv run uvicorn app.main:app --reload
```

## 文档

学习笔记位于 `docs/notes/`：

- [Day 3 - Prompt 外置](docs/notes/week1-day3-prompt-modularization.md)
- [Day 4 - Structured Output](docs/notes/week1-day4-structured-output.md)
- [Day 5 - 流式响应](docs/notes/week1-day5-streaming-response.md)
- [Day 6 - 中间件与异常处理](docs/notes/week1-day6-middleware-exception.md)

## 相关资源

- [LangChain 1.x 文档](https://docs.langchain.com)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
