# 2 个月 AI Agent 应用开发学习路线

## 适用对象

本路线基于 [../profile/user-profile.md](../profile/user-profile.md) 制定，适合当前具备以下基础的学习者：

- 主修 Python，能独立完成小项目
- 使用过 Flask / FastAPI
- 会简单 SQL
- 使用过 Linux、Docker、Git
- 调用过大模型 API
- 了解 Prompt Engineering、工具调用、RAG、Embedding、向量数据库
- 尚未做过完整 Agent / RAG 项目
- 每天可投入约 1 小时，希望 2 个月产出求职级项目

## 总目标

用 8 周完成一个可用于简历和面试展示的 AI Agent 项目：

**面向技术学习与代码仓库的智能知识库 Agent**

项目最终应具备：

1. 文档上传与解析
2. 文档分块、Embedding、向量检索
3. RAG 问答与引用来源
4. Prompt 模板与基础评测
5. FastAPI 后端接口
6. 多轮对话与简单会话记忆
7. Function Calling / Tool Calling
8. 代码仓库探索能力雏形
9. 日志、错误处理、Docker 启动
10. README、架构图、简历描述、面试问答材料

## 学习原则

1. **项目驱动，不做纯理论堆积**
   - 每周都要有可运行产出。

2. **优先完成 P0 能力**
   - 对齐 [../jd-analysis/03-tech-stack-matrix.md](../jd-analysis/03-tech-stack-matrix.md) 中的 Python、LLM API、Prompt、Tool Calling、RAG、LangChain / LangGraph、FastAPI、数据库、Docker。

3. **暂缓模型训练方向**
   - 2 个月内不重点学习微调、CUDA、多模态，除非主项目已经完成。

4. **每周沉淀文档**
   - 不只是写代码，还要写清楚技术选型、问题、解决方案和面试表达。

## 每日时间分配建议

每天 1 小时，建议拆成：

- 10 分钟：复盘昨天问题，明确今天目标
- 35 分钟：编码 / 调试 / 实验
- 10 分钟：记录笔记、踩坑、关键结论
- 5 分钟：更新 TODO 和下一步

每周建议 6 天学习 + 1 天复盘：

- 周一到周五：推进功能
- 周六：补文档、整理代码、做小测试
- 周日：复盘、总结、调整下周计划

## 8 周路线总览

| 周次 | 主题 | 核心产出 | 对应 JD 能力 |
|---|---|---|---|
| 第 1 周 | 项目骨架 + LLM API + Prompt | FastAPI LLM Chat API | Python、FastAPI、LLM API、Prompt |
| 第 2 周 | 文档解析 + RAG 最小链路 | 本地知识库问答 Demo | 文档解析、Chunking、Embedding、向量检索 |
| 第 3 周 | RAG 优化 + 引用来源 + 评测 | 可解释的 RAG 问答系统 | RAG、引用、评测、幻觉控制 |
| 第 4 周 | Tool Calling + 会话记忆 | 可调用工具的问答 Agent | Function Calling、工具调用、记忆管理 |
| 第 5 周 | LangGraph / Agent 工作流 | 多步骤 Agent 执行流程 | 任务规划、工作流编排、Agent 状态 |
| 第 6 周 | 代码仓库探索 Agent | 代码仓库问答和文件检索工具 | 代码理解、工具调用、RAG 扩展 |
| 第 7 周 | 工程化 + Docker + 日志评测 | 可部署 Agent 后端服务 | Docker、日志、错误处理、LLMOps 基础 |
| 第 8 周 | 项目包装 + 简历面试 | README、架构图、简历项目、面试问答 | 项目表达、业务落地、面试准备 |

## 第 1 周：项目骨架 + LLM API + Prompt

### 目标

建立主项目骨架，完成一个可运行的 LLM Chat API。

### 学习内容

- FastAPI 项目结构
- 环境变量管理
- LLM API 调用
- Prompt 模板
- 普通响应与流式响应的区别

### 实践任务

1. 创建项目结构：

```text
app/
  main.py
  api/
  services/
  schemas/
  core/
```

2. 实现接口：

```text
POST /chat
```

3. 支持：

- 输入用户问题
- 调用大模型 API
- 返回回答
- 基础错误处理
- 基础日志

### 每日安排

| 天数 | 任务 |
|---|---|
| Day 1 | 设计项目目录和技术栈，创建 FastAPI 最小服务 |
| Day 2 | 封装 LLM API 调用函数 |
| Day 3 | 设计 Prompt 模板结构 |
| Day 4 | 实现 `/chat` 接口 |
| Day 5 | 加入基础日志和异常处理 |
| Day 6 | 写 README 的运行方式 |
| Day 7 | 复盘：总结 LLM API、Prompt、FastAPI 的关键点 |

### 验收标准

- 能启动 FastAPI 服务
- 能通过接口调用 LLM
- README 说明如何配置 API Key 和运行服务

## 第 2 周：文档解析 + RAG 最小链路

### 目标

完成最小可用 RAG：文档 → 分块 → Embedding → 向量检索 → LLM 回答。

### 学习内容

- Markdown / TXT 文档解析
- Chunking 策略
- Embedding
- 向量数据库，建议先用 FAISS 或 Chroma
- 检索结果拼接 Prompt

### 实践任务

1. 支持导入本地 Markdown / TXT 文档。
2. 完成分块和向量化。
3. 实现检索函数。
4. 实现：

```text
POST /rag/query
```

### 每日安排

| 天数 | 任务 |
|---|---|
| Day 1 | 理解 RAG 全链路，确定向量库方案 |
| Day 2 | 实现文档读取和清洗 |
| Day 3 | 实现 Chunking |
| Day 4 | 接入 Embedding 并写入向量库 |
| Day 5 | 实现相似度检索 |
| Day 6 | 将检索结果拼接到 Prompt 中回答问题 |
| Day 7 | 复盘：记录 RAG 链路和关键参数 |

### 验收标准

- 能导入至少 3 篇文档
- 能基于文档内容回答问题
- 能看到检索到的原始片段

## 第 3 周：RAG 优化 + 引用来源 + 评测

### 目标

让 RAG 从“能跑”变成“可解释、可评估”。

### 学习内容

- 引用来源
- chunk size / overlap 对结果的影响
- Top-K 检索
- 简单评测集
- 幻觉分析

### 实践任务

1. 回答中返回引用片段。
2. 设计 10 个测试问题。
3. 记录每个问题的：
   - 检索片段是否相关
   - 回答是否正确
   - 是否出现幻觉
4. 调整 chunk size、Top-K、Prompt。

### 每日安排

| 天数 | 任务 |
|---|---|
| Day 1 | 为文档块增加 metadata 和来源 |
| Day 2 | 回答中返回引用片段 |
| Day 3 | 设计 10 条评测问题 |
| Day 4 | 跑第一轮评测并记录问题 |
| Day 5 | 调整 chunk size / Top-K / Prompt |
| Day 6 | 输出 RAG 评测表 |
| Day 7 | 复盘：总结 RAG 错误类型 |

### 验收标准

- RAG 回答包含引用来源
- 有一份 10 条问题的评测记录
- 能说明至少 3 类 RAG 常见错误

## 第 4 周：Tool Calling + 会话记忆

### 目标

把 RAG 问答升级为具备工具调用和简单记忆的 Agent。

### 学习内容

- Function Calling / Tool Calling
- 工具 schema 设计
- 参数校验
- 工具调用日志
- 短期会话记忆

### 实践任务

实现至少 3 个工具：

1. 文档检索工具
2. 当前时间 / 日期工具
3. 简单代码文件读取或关键词搜索工具

新增能力：

- 多轮对话记录
- 根据用户问题决定是否调用工具
- 返回工具调用过程摘要

### 每日安排

| 天数 | 任务 |
|---|---|
| Day 1 | 学习 Tool Calling 基本机制 |
| Day 2 | 设计工具 schema |
| Day 3 | 实现文档检索工具 |
| Day 4 | 实现时间工具和文件搜索工具 |
| Day 5 | 加入会话记忆 |
| Day 6 | 调试多轮问答和工具调用日志 |
| Day 7 | 复盘：总结工具调用失败原因 |

### 验收标准

- Agent 能调用至少 3 个工具
- 支持简单多轮对话
- 能记录工具调用日志

## 第 5 周：LangGraph / Agent 工作流

### 目标

用框架实现可控的多步骤 Agent，而不是只依赖一次性模型调用。

### 学习内容

- LangGraph 状态机思想
- 节点、边、状态
- 规划节点、工具节点、回答节点
- 结束条件

### 实践任务

用 LangGraph 实现流程：

```text
用户问题 → 判断任务类型 → 检索 / 工具调用 → 生成回答 → 输出引用和工具轨迹
```

### 每日安排

| 天数 | 任务 |
|---|---|
| Day 1 | 学习 LangGraph 基本概念 |
| Day 2 | 定义 AgentState |
| Day 3 | 实现任务判断节点 |
| Day 4 | 实现检索 / 工具节点 |
| Day 5 | 实现回答节点和结束条件 |
| Day 6 | 接入 FastAPI 接口 |
| Day 7 | 复盘：画出 Agent 工作流图 |

### 验收标准

- Agent 流程由多个节点组成
- 能输出执行轨迹
- 有一张工作流图或文字说明

## 第 6 周：代码仓库探索 Agent

### 目标

把项目扩展到用户感兴趣的“代码仓库探索”场景。

### 学习内容

- 代码文件扫描
- 文件类型过滤
- 代码块切分
- 基于代码的检索问答
- 工具调用与代码阅读结合

### 实践任务

实现代码仓库探索能力：

1. 输入一个本地代码仓库路径
2. 扫描 `.py` / `.md` 等文件
3. 建立代码索引
4. 支持问题：
   - 这个项目的入口在哪里？
   - 某个函数在哪个文件？
   - 某个模块大概做什么？
   - 如何运行这个项目？

### 每日安排

| 天数 | 任务 |
|---|---|
| Day 1 | 设计代码仓库索引方案 |
| Day 2 | 实现文件扫描和过滤 |
| Day 3 | 实现代码块切分和 metadata |
| Day 4 | 建立代码向量索引 |
| Day 5 | 实现代码问答 Prompt |
| Day 6 | 接入 Agent 工具调用流程 |
| Day 7 | 复盘：记录代码仓库问答的局限 |

### 验收标准

- 能索引一个小型代码仓库
- 能回答 5 类代码仓库问题
- 能返回文件路径和片段来源

## 第 7 周：工程化 + Docker + 日志评测

### 目标

把项目从 Demo 提升到可展示、可运行、可排查的问题级别。

### 学习内容

- Dockerfile
- docker-compose
- 配置管理
- 日志结构
- 错误处理
- 评测脚本
- API 文档

### 实践任务

1. 添加 Dockerfile。
2. 添加 docker-compose。
3. 整理 `.env.example`。
4. 完善日志。
5. 增加评测脚本或评测表。
6. 整理接口文档。

### 每日安排

| 天数 | 任务 |
|---|---|
| Day 1 | 整理配置和环境变量 |
| Day 2 | 编写 Dockerfile |
| Day 3 | 编写 docker-compose |
| Day 4 | 完善日志和异常处理 |
| Day 5 | 编写 RAG / Agent 评测脚本或表格 |
| Day 6 | 整理 API 文档 |
| Day 7 | 复盘：从面试角度总结工程化亮点 |

### 验收标准

- 项目可以通过 Docker 启动
- 有 `.env.example`
- 有日志和错误处理
- 有评测记录或评测脚本

## 第 8 周：项目包装 + 简历面试

### 目标

把项目包装成能放进简历、能讲清楚、能被面试官追问的作品。

### 学习内容

- README 写作
- 架构图
- 项目亮点提炼
- 技术难点与解决方案
- 面试问答准备

### 实践任务

输出以下材料：

1. 项目 README
2. 架构图或模块图
3. 项目运行截图或接口调用示例
4. 简历项目描述
5. 10-15 个面试问答
6. 项目复盘文档

### 每日安排

| 天数 | 任务 |
|---|---|
| Day 1 | 重写 README：背景、功能、架构、运行方式 |
| Day 2 | 画项目架构图和 Agent 工作流图 |
| Day 3 | 整理项目亮点和技术难点 |
| Day 4 | 写简历项目描述 |
| Day 5 | 准备 10-15 个面试问答 |
| Day 6 | 做完整演示和自测 |
| Day 7 | 总复盘：下一阶段补强方向 |

### 验收标准

- 项目能从零启动并演示
- README 能让别人理解和运行
- 简历描述能突出 JD 关键词
- 能讲清楚 RAG、Tool Calling、Agent 工作流、工程化和评测

## 每周复盘模板

建议每周在 `docs/notes/` 中记录一次复盘：

```md
# 第 X 周复盘

## 本周目标

## 已完成内容

## 遇到的问题

## 解决方案

## 关键知识点

## 仍然不理解的点

## 下周计划
```

## 主项目建议名称

可选项目名：

1. `agentic-knowledge-assistant`
2. `codebase-rag-agent`
3. `dev-knowledge-agent`
4. `smart-knowledge-agent`

推荐使用：

**`dev-knowledge-agent`**

含义：面向技术学习、个人知识库和代码仓库探索的智能 Agent。

## 技术栈建议

### 后端

- Python
- FastAPI
- Pydantic
- Uvicorn

### LLM

- 任一可用大模型 API
- 后续可抽象模型供应商接口

### RAG

- 文档解析：先支持 Markdown / TXT
- Embedding：选择一个稳定可用的 embedding API 或本地模型
- 向量库：优先 FAISS / Chroma，后续可切 PGVector / Milvus

### Agent

- 第 4 周先手写 Tool Calling 逻辑
- 第 5 周再引入 LangGraph

### 存储与工程化

- SQLite 或 PostgreSQL：会话和文档元数据
- Redis：后续用于缓存和限流，可选
- Docker / docker-compose
- Python logging 或 loguru

## 简历项目描述草稿

> 开发了一个面向技术学习与代码仓库探索的智能知识库 Agent，基于 FastAPI 构建后端服务，集成大模型 API、RAG 检索、工具调用和多轮会话能力。系统支持 Markdown / TXT 文档解析、Embedding 向量化、知识库问答、引用来源返回，以及本地代码仓库索引与问答。通过 LangGraph 编排多步骤 Agent 工作流，并加入日志、错误处理、Docker 部署和基础评测表，用于提升问答准确性和项目可维护性。

## 面试高频问题预备

1. 你的 RAG 系统完整链路是什么？
2. 你如何做文档分块？chunk size 怎么选？
3. Embedding 和向量数据库分别解决什么问题？
4. 如何判断 RAG 的回答是否可靠？
5. 你的 Agent 和普通聊天机器人有什么区别？
6. Tool Calling 的 schema 怎么设计？
7. 工具调用失败怎么办？
8. LangGraph 在项目中解决了什么问题？
9. 如何做会话记忆？短期记忆和长期记忆有什么区别？
10. 项目如何部署？为什么用 Docker？
11. 如何记录日志和排查问题？
12. 如果用户问的问题知识库里没有，系统怎么处理？
13. 代码仓库探索 Agent 如何切分代码？
14. 你的项目有哪些不足？下一步怎么优化？
15. 如果要支持企业多用户和权限隔离，你会怎么设计？

## 下一步

执行本路线前，建议先创建主项目目录和第一周任务清单。学习过程中，每周结束后更新复盘文档，并根据实际进度调整下一周范围。
