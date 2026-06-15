# AI Agent 岗位技术栈矩阵

本文件从 30 份岗位 JD 中提炼高频技术栈，并按学习优先级分为 P0 / P1 / P2。

## 优先级定义

| 优先级 | 含义 |
|---|---|
| P0 | AI Agent 应用开发求职必须优先掌握 |
| P1 | 能显著提升竞争力，适合项目深化 |
| P2 | 进阶或特定岗位需要，后期补充 |

## 技术栈总览

| 技术方向 | 高频技术 / 关键词 | 频率等级 | 代表岗位 | 优先级 | 为什么重要 | 推荐实践项目 |
|---|---|---|---|---|---|---|
| 编程语言 | Python | 极高频 | JD-01、JD-02、JD-05、JD-13、JD-19、JD-26、JD-30 | P0 | Python 是 LLM API、RAG、Agent 框架和数据处理的主力语言 | 用 Python 封装 LLM API 调用、文件解析、工具函数 |
| 编程语言 | Java / Go / TypeScript / Node.js | 高频 | JD-01、JD-06、JD-14、JD-16、JD-22、JD-29、JD-30 | P1 | 很多企业岗位要求后端工程能力，语言不止 Python | 用一种后端语言实现 Agent API 服务 |
| 编程语言 | C / C++ | 中频 | JD-03、JD-07、JD-08、JD-11、JD-17、JD-21、JD-27 | P2 | 偏模型部署、后台性能、游戏和嵌入式场景 | 实现一个 C++ / Python 混合小工具或推理服务 Demo |
| 后端与 API | FastAPI / Flask / Django / Spring Boot / Express / Koa | 高频 | JD-05、JD-13、JD-16、JD-19、JD-22 | P0 | AI 能力需要通过 API 服务接入业务系统 | FastAPI + LLM / RAG 服务 |
| 后端与 API | RESTful API、接口联调、权限控制、异常处理 | 高频 | JD-02、JD-14、JD-17、JD-21、JD-22、JD-27 | P0 | Tool Calling、MCP、业务系统集成都依赖 API 能力 | 为 Agent 接入一个外部 API 工具 |
| 数据库 / 缓存 | MySQL / PostgreSQL / Redis / MongoDB | 高频 | JD-01、JD-05、JD-06、JD-13、JD-15、JD-19、JD-22 | P0 | 存储用户、会话、任务、缓存、业务数据 | 为 Agent 服务加入会话表和 Redis 缓存 |
| 消息与任务 | Kafka / RabbitMQ / 任务调度 / 可重试服务 | 中频 | JD-01、JD-06、JD-16 | P1 | 长任务、异步执行和高可用系统需要消息与任务机制 | 实现一个异步任务队列处理 Agent 执行请求 |
| LLM API | OpenAI、Claude、Gemini、Qwen、DeepSeek、GLM | 高频 | JD-01、JD-02、JD-30 | P0 | 调用主流模型是所有 Agent / RAG 项目的入口 | 支持多个模型供应商的聊天接口 |
| Prompt | Prompt Engineering、指令工程、CoT、Few-shot、ReAct | 极高频 | JD-01、JD-04、JD-10、JD-14、JD-20、JD-24、JD-27、JD-30 | P0 | Prompt 直接影响 Agent 稳定性、可控性和业务效果 | 为一个业务场景设计 Prompt 模板并评估效果 |
| Function / Tool | Function Calling、Tool Calling、工具调用、业务 API 对接 | 极高频 | JD-01、JD-05、JD-14、JD-16、JD-17、JD-21、JD-27、JD-30 | P0 | Agent 区别于普通聊天机器人的关键能力 | 实现天气 / 搜索 / 数据库查询工具调用 Agent |
| Agent 核心 | 任务规划、任务分解、记忆管理、多轮对话、反思优化 | 极高频 | JD-01、JD-05、JD-16、JD-19、JD-20、JD-22、JD-26、JD-30 | P0 | 岗位反复要求能构建真正能执行任务的智能体 | 实现“计划 → 执行 → 观察 → 修正”的 Agent 循环 |
| Agent 框架 | LangChain | 高频 | JD-01、JD-06、JD-15、JD-16、JD-19、JD-24、JD-26、JD-29、JD-30 | P0 | 最常见的大模型应用与 Agent 编排框架之一 | 用 LangChain 串联 Prompt、Retriever、Tool |
| Agent 框架 | LangGraph | 高频 | JD-05、JD-15、JD-16、JD-19、JD-22、JD-26 | P0 | 适合多步骤、状态机、工作流型 Agent | 用 LangGraph 实现多节点任务执行流程 |
| Agent 框架 | LlamaIndex | 高频 | JD-01、JD-19、JD-22、JD-26、JD-29、JD-30 | P1 | 在数据连接、索引和 RAG 场景中常见 | 用 LlamaIndex 构建文档问答系统 |
| Agent 框架 | AutoGen / CrewAI / Dify / Coze / OpenClaw / Spring AI | 中高频 | JD-12、JD-15、JD-16、JD-18、JD-19、JD-24、JD-27 | P1 | 覆盖低代码、多 Agent、企业落地和 AI 编程平台 | 用 Dify / Coze / OpenClaw 复现一个业务 Agent 原型 |
| RAG | 数据清洗、Chunking、Embedding、向量检索、混合检索、Rerank | 极高频 | JD-01、JD-05、JD-06、JD-13、JD-15、JD-19、JD-20、JD-26、JD-29、JD-30 | P0 | RAG 是 AI 应用岗位最核心的落地能力之一 | 搭建带引用来源和评估指标的知识库问答系统 |
| 向量数据库 | Milvus、FAISS、PGVector、Qdrant、Elasticsearch、Pinecone | 高频 | JD-05、JD-11、JD-16、JD-19、JD-26、JD-30 | P1 | 企业知识库和语义检索的核心基础设施 | 对比 FAISS 与 Milvus 的检索效果和部署方式 |
| 多智能体 | Multi-Agent、多 Agent 角色协作、A2A | 中高频 | JD-01、JD-05、JD-14、JD-15、JD-20、JD-24、JD-29、JD-30 | P1 | 复杂业务会拆成多个角色协作，而不是单一 Agent | 设计“规划 Agent + 执行 Agent + 评审 Agent”的协作 Demo |
| MCP / 工具协议 | MCP、A2A、Modal、E2B | 中频 | JD-15、JD-17、JD-18、JD-21、JD-29 | P1 | 新型 Agent 生态强调标准化工具接入和沙箱执行 | 为 Agent 接入一个本地工具服务或沙箱执行环境 |
| 工程部署 | Linux、Docker、docker-compose、K8s、CI/CD | 高频 | JD-06、JD-07、JD-11、JD-15、JD-19、JD-27 | P1 | Demo 到可交付项目必须经过部署和运行环境管理 | 将 RAG / Agent 服务 Docker 化 |
| 观测与 LLMOps | 日志、监控、模型评测、成本控制、Token 消耗、异常处理 | 中高频 | JD-04、JD-26、JD-27、JD-30 | P1 | 企业关注稳定性、效果、成本和可维护性 | 为 Agent 服务记录调用日志、错误和 Token 成本 |
| 模型训练 / 微调 | PyTorch、TensorFlow、CUDA、LoRA / 微调、模型评测 | 中频 | JD-02、JD-03、JD-07、JD-11、JD-15、JD-18 | P2 | 对算法岗或高阶应用优化有帮助，但不是应用开发起点 | 完成一个小模型微调或模型评测实验 |
| 多模态 / AIGC | CLIP、图像识别、文生图、文生视频、文生建模 | 低到中频 | JD-11、JD-27、JD-28 | P2 | 适合游戏、美术、图像业务和多模态岗位 | 做一个图片理解或 AIGC 工作流 Demo |
| AI 编程工具 | Claude Code、Cursor、Trae、Codex、Vibe Coding | 中高频 | JD-06、JD-14、JD-17、JD-21、JD-24、JD-28 | P1 | 岗位越来越重视 AI Native 开发效率和工具熟练度 | 用 AI 编程工具完成一个小功能并记录协作流程 |
| 业务能力 | 需求拆解、业务抽象、跨团队协作、指标意识、文档表达 | 极高频 | JD-04、JD-05、JD-10、JD-14、JD-20、JD-23、JD-24、JD-28 | P0 | Agent 项目不是纯技术，需要把业务流程转成可执行系统 | 为一个业务场景写“需求 → Agent 方案 → 验收指标”文档 |

## P0 必学清单

1. Python 基础与 API 调用
2. LLM API 调用与流式响应
3. Prompt Engineering：角色、任务、约束、示例、输出格式
4. Function Calling / Tool Calling
5. RAG 全链路：解析、分块、Embedding、检索、重排、评估
6. LangChain / LangGraph 基础
7. Agent 核心循环：任务规划、工具调用、记忆、多轮对话
8. FastAPI 或同类 Web API 开发
9. MySQL / Redis 基础使用
10. 业务需求拆解与项目文档表达

## P1 强竞争力清单

1. LlamaIndex / Dify / AutoGen / CrewAI / OpenClaw 等框架对比
2. Milvus / FAISS / PGVector / Qdrant 至少掌握一种
3. Multi-Agent 协作
4. MCP / A2A / 工具协议
5. Docker / Linux / 基础部署
6. 日志、监控、评测、Token 成本控制
7. AI 编程工具工作流

## P2 进阶补充清单

1. PyTorch / TensorFlow / 模型微调
2. CUDA / C++ 推理优化
3. 多模态与 AIGC
4. 云原生 K8s 深入
5. 高并发大规模系统架构

## 对学习路线的启发

如果目标是 AI Agent 应用开发，建议不要一开始陷入模型训练，而是先按以下顺序学习：

1. Python + Web API + 数据库基础
2. LLM API + Prompt
3. Function Calling / Tool Calling
4. RAG 知识库
5. LangChain / LangGraph Agent
6. Docker、日志、评测、部署
7. Multi-Agent、MCP、LLMOps 等进阶能力
