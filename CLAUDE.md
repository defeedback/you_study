# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目目标

本仓库是 AI 应用 / Agent 开发学习与职业准备空间，目标是帮助用户系统掌握 AI 应用开发中的 Agent 开发能力。后续工作应围绕以下主线展开：

- 清洗和整理岗位 JD
- 从 JD 中提炼技术栈与能力要求
- 了解用户当前编程能力和学习背景
- 制定阶段性学习路线
- 设计项目实践
- 记录学习过程中的重点、难点和复盘
- 建立可长期维护的文档结构

## 当前仓库状态

- 当前核心资料是 [岗位JD.md](岗位JD.md)。
- 该文件包含 30 份 AI / Agent 相关岗位 JD，以及高频技术栈和求职能力总结。
- 当前仓库没有发现已确认的包管理文件、应用源码目录、构建脚本、测试配置或 lint 配置。
- 不要把 `e:/study/` 下的相邻项目当成本仓库架构，除非用户明确要求并经过单独验证。

## 沟通语言与讲解风格

默认使用中文与用户沟通。技术术语可以保留英文，例如 Agent、RAG、Function Calling、Tool Calling、Prompt Engineering、LangChain、LlamaIndex、LangGraph、MCP、vector database 等。

讲解技术内容时，优先采用以下结构：

1. 说明这个能力为什么会出现在 JD 中。
2. 先给整体认知框架。
3. 再拆解关键概念。
4. 给一个最小实践任务或项目练习。
5. 用户需要时，整理重点、难点和易错点到笔记文档。

## JD 清洗与技术栈提炼流程

整理 [岗位JD.md](岗位JD.md) 时遵循以下规则：

- 保留 30 份岗位信息的原始含义，不要随意删除原始信息。
- 统一字段格式，例如：岗位名称、薪资、地点、核心标签、岗位职责、任职要求、加分项。
- 清理标题层级不一致、重复表述、目录锚点错误、格式不统一等问题。
- 可按岗位方向归类，例如：
  - AI Agent 应用开发
  - RAG / 知识库 / 工作流工程
  - 后端工程与 API 集成
  - 模型训练 / 微调 / 算法工程
  - AI 产品、运营与业务落地
- 提炼技术栈矩阵，覆盖：
  - 编程语言
  - 后端与 API 工程
  - LLM API 与模型供应商
  - Agent 框架与编排
  - RAG、Embedding、Rerank、向量数据库
  - 数据库、缓存、消息队列
  - 部署、可观测性与 LLMOps
  - 产品、沟通、业务理解等软技能

## 用户画像与学习计划流程

未来制定学习路线或解释新主题前，应尽可能了解用户情况。用户画像可关注：

- 当前编程能力
- Python / JavaScript / TypeScript / 后端开发经验
- AI / 机器学习 / LLM 基础
- 是否做过 RAG、Agent、API 集成或部署项目
- 目标岗位方向
- 每周可投入学习时间
- 偏好的学习方式和项目兴趣

当用户要求讲解新知识或安排学习任务时，先检查是否已有学习计划或进度文档。如果已有，应先读取并对齐当前阶段；如果没有，应先帮助用户建立阶段性学习计划，再展开长篇课程式讲解。

## 推荐文档结构

以下是推荐结构，不代表这些目录已经存在。除非用户明确要求，否则创建这些目录或文件前应先询问用户。

- `docs/jd-analysis/`：存放 JD 清洗、岗位分类、技术栈矩阵。
- `docs/profile/`：存放用户背景、目标岗位、约束条件、学习偏好。
- `docs/learning-plans/`：存放阶段性学习计划与进度记录。
- `docs/notes/`：存放知识点笔记、重点、难点、易错点。
- `docs/projects/`：存放实践项目设计、实现记录和复盘。

## 项目实践学习建议

设计学习项目时，应尽量贴合 JD 能力要求。建议项目递进顺序：

1. LLM API 调用与 Prompt Engineering 小工具。
2. RAG 知识库问答项目。
3. 带工具调用和记忆能力的 Agent 项目。
4. 多步骤工作流 / LangGraph 风格 Agent 项目。
5. 端到端 AI Agent 应用，包含后端 API、持久化、评估和部署。

每个项目计划应包含：项目目标、覆盖的 JD 能力、技术栈、模块拆分、MVP 范围、进阶范围、验收标准。

## 常用命令

当前仓库没有已确认的 build、test、lint、run 命令。不要编造命令；只有在引入并验证对应配置文件后，才补充具体运行、测试或构建命令。

已验证的通用仓库检查命令：

```bash
git status --short
```

如果后续加入 Python 代码，应遵循用户全局偏好，使用 `uv` 管理 Python 依赖和执行命令。

## LangChain 框架约束

本仓库统一使用 **LangChain 1.x**。所有 LangChain 相关代码、示例、讲解必须符合 v1 官方文档：https://docs.langchain.com

### 禁止使用（已废弃或已移除）

- `initialize_agent`
- `AgentExecutor`
- `LLMChain`
- `RetrievalQA`
- `create_react_agent`（LangChain 旧版 API；LangGraph 中的 `create_react_agent` 也不要使用，统一用 `create_agent`）

如果在示例、教程或旧代码中遇到上述 API，必须改写为 v1 写法后再使用，不能直接照搬。

### 优先使用

- `create_agent`：来自 `langchain.agents`，构建 Agent 的统一入口，底层基于 LangGraph
- `langgraph`：用于编排多步骤、可控的 Agent 工作流和状态机
- middleware：用于在 Agent 调用前后插入横切逻辑（鉴权、日志、限流、上下文裁剪等）
- structured output：通过 `with_structured_output(...)` 或 Pydantic schema 让模型直接返回结构化结果，替代手写 JSON 解析

### 推荐写法

- 模型初始化：优先 `from langchain.chat_models import init_chat_model`，统一切换 provider 和模型名
- Chain 编排：使用 LCEL，例如 `prompt | llm | StrOutputParser()`，不再使用 `LLMChain`
- Agent 编排：使用 `create_agent(model=..., tools=[...])`，复杂工作流回退到原生 `langgraph`
- RAG 编排：用 LCEL 拼装 retriever、prompt、llm，不使用 `RetrievalQA`

### 编码原则

- 写代码或讲解时，先确认目标 API 是否在 v1 文档中存在，避免引用已删除模块
- 涉及 Agent / 工具调用 / 工作流时，默认走 `create_agent` 或 LangGraph 路线
- 涉及结构化输出时，优先 structured output，而不是让模型自行返回 JSON 字符串再人工 `json.loads`
