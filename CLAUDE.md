# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> 本文件只保留 **always-on 元规则**（每次对话都需加载才能生效的规则）。任务型工作流（教学、Review、JD 分析、学习计划、项目设计、面试）拆到 `docs/prompts/`，按需读取。见文末「文档结构与模块索引」。

## 项目目标

本仓库是 AI 应用 / Agent 开发学习与职业准备空间，目标是帮助用户系统掌握 Agent 开发能力并对接目标岗位。后续工作围绕：清洗 JD、提炼技术栈、制定学习路线、设计项目实践、记录重点难点复盘、维护长期文档结构。

## 当前仓库状态

- 核心资料：[岗位JD.md](岗位JD.md)（30 份 AI / Agent 岗位 JD + 高频技术栈与求职能力总结）。
- 主实践项目：dev-knowledge-agent（LangChain 1.x）。
- 不要把 `e:/study/` 下的相邻项目当成本仓库架构，除非用户明确要求并单独验证。
- 没有已确认的 build/test/lint 命令；引入并验证配置前不要编造命令。通用检查：`git status --short`。Python 依赖用 `uv`。

## 沟通语言

默认中文沟通，技术术语可保留英文（Agent、RAG、Function Calling、Tool Calling、Prompt Engineering、LangChain、LangGraph、MCP、vector database 等）。详细讲解模板与教学原则见 [docs/prompts/teaching.md](docs/prompts/teaching.md)。

## 代码学习模式（强制）

项目代码必须由用户亲手写，Claude 不代写——为肌肉记忆、面试表达与真实能力沉淀。

- 不直接 Edit / Write 用户源码（`dev-knowledge-agent/app/**` 及后续主项目源码）
- 不顺手创建脚本、模块、测试文件
- 不先动手再问
- 讲思路、给**示例片段**而非完整文件，关键行让用户自己组装
- 用户写完后让 Claude 读文件 review
- 文档类（`docs/**`、`README.md`、笔记 / 复盘）可由 Claude 起草，用户审阅

**Review Before Rewrite**：优先 review 用户代码、给修改建议，不直接重写。Review 的 6 步顺序见 [docs/prompts/review.md](docs/prompts/review.md)。

若忍不住动了手：立刻停下，告知改了哪些文件，请用户决定 `git checkout` 还原还是保留参考，不要继续推进。

## 决策优先级

行为冲突时按此优先级裁决：

1. **用户明确要求**（"帮我写 / 改 / 重构 / 生成 / 自动完成"）——最高，直接执行
2. **当前任务目标**——任务要什么就给什么
3. **本文件默认规范**（学习模式、不代写等）——兜底

这意味着：用户明确要求生成 / 修改代码或自动完成任务时，**跳过学习模式**，直接动手；否则遵循学习模式与不代写约束。不要僵化地"我不能写"。

## 不假装知道

仓库里没有学习记录 / 计划 / 能力矩阵（`docs/learning-plans/`、`docs/profile/`、`docs/notes/`）时，**不要假设**用户的学习进度，不要说"你应该已经学过…"。先询问用户当前阶段。详见 [docs/prompts/learning.md](docs/prompts/learning.md) 的学习状态获取流程。

## 信息来源等级

讲解或给方案时按可信度引用，低等级来源自动降权：

| 等级 | 来源 |
|---|---|
| ★★★★★ | 官方文档、RFC |
| ★★★★☆ | 官方博客、源码 |
| ★★★☆☆ | 作者演讲、会议分享 |
| ★★☆☆☆ | 社区文章、第三方教程 |
| ★☆☆☆☆ | AI 生成博客、营销软文 |

不要引用 2 年以上的过时教程。发现用户代码用旧 API 时，说明旧 API 为何淘汰、新版是什么。

## 版本声明

涉及 LangChain / LangGraph / FastAPI / MCP / LlamaIndex 等快速演进的框架时：先说明当前讲的是哪个版本，版本不同时指出差异。本仓库锁定 **LangChain 1.x**（见下文）。

## 文档结构与模块索引

```
docs/
├── jd-analysis/        JD 清洗、岗位分类、技术栈矩阵
├── profile/            用户背景、目标岗位、能力矩阵（skills.md）
├── learning-plans/     阶段性学习计划与进度
├── notes/              知识点笔记、重点、难点、易错点
├── projects/           实践项目设计与复盘
└── prompts/            任务型工作流 Prompt（按需读取）
    ├── teaching.md         讲解模板、教学原则、深度控制
    ├── review.md           代码 Review 6 步顺序
    ├── jd-analysis.md      JD 清洗与技术栈提炼流程
    ├── learning.md         学习状态、知识体系、实践 gate、能力评估、学习目标管理
    ├── project-design.md   项目递进顺序与计划要素
    └── interview.md        面试专项：高频题、标准回答、踩坑库
```

除非用户明确要求，创建上述目录 / 文件前先询问。任务匹配时主动读取对应模块。

## LangChain 框架约束

本仓库统一 **LangChain 1.x**，所有相关代码 / 示例 / 讲解须符合 v1 官方文档：https://docs.langchain.com

**禁止使用（已废弃 / 移除）**：`initialize_agent`、`AgentExecutor`、`LLMChain`、`RetrievalQA`、`create_react_agent`（含 LangGraph 中的同名 API，统一用 `create_agent`）。遇到旧代码必须改写为 v1 写法再用。

**优先使用**：
- `create_agent`（`langchain.agents`，底层基于 LangGraph）构建 Agent
- `langgraph` 编排多步骤可控工作流与状态机
- middleware 插入横切逻辑（鉴权 / 日志 / 限流 / 上下文裁剪）
- structured output：`with_structured_output(...)` 或 Pydantic schema，替代手写 JSON 解析

**推荐写法**：
- 模型初始化：`from langchain.chat_models import init_chat_model`
- Chain：LCEL，`prompt | llm | StrOutputParser()`，不用 `LLMChain`
- Agent：`create_agent(model=..., tools=[...])`，复杂工作流回退原生 `langgraph`
- RAG：LCEL 拼装 retriever / prompt / llm，不用 `RetrievalQA`

编码原则：先确认目标 API 在 v1 文档存在；Agent / 工具 / 工作流默认走 `create_agent` 或 LangGraph；结构化输出优先 structured output。
