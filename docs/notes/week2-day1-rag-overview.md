# Week 2 · Day 1：RAG 全链路 + 向量库 / Embedding 选型

**日期**：2026-06-28
**对应阶段**：2 个月路线 · 第 2 周 Day 1
**主题**：吃透 RAG 链路，定下向量库和 Embedding 方案

---

## 0. 一句话总结

> RAG = 检索 + 生成。离线把文档「切碎 → 向量化 → 存库」，在线把问题「向量化 → 去库里捞最像的几段 → 连同问题喂给 LLM 回答」。
> 今天不写代码，只做两件事：吃透全链路 + 定下 Embedding 方案。

---

## 1. 为什么 JD 里 RAG 是必考

大模型有两个硬伤：

- **知识截止时间**：训练数据有截止日，之后的事它不知道。
- **幻觉**：一本正经胡说，尤其在没有依据时。

企业真正要的是：用**自家文档**（产品手册、内部 wiki、代码仓库）回答问题，且**答错能追责**。RAG 就是目前业界最通用的解法——用外部知识补上模型不知道的，并且每句话能溯源到原文档。

JD 关键词：`RAG / Embedding / 向量数据库 / chunking / 引用来源 / 幻觉控制`。

---

## 2. RAG 整体认知框架

```text
┌─────────────────────────────────────────────────────────────┐
│  离线阶段（建库，只做一次 / 文档更新时重做）                  │
│                                                             │
│  原始文档 → ①解析 → ②分块(chunking) → ③Embedding → ④入向量库 │
│   .md/.txt   纯文本    语义连续的小段        向量           FAISS │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ 同一个 Embedding 模型
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  在线阶段（每次提问）                                        │
│                                                             │
│  用户问题 → ⑤Embedding → ⑥向量检索(top-k) → ⑦拼 Prompt       │
│              同模型      FAISS 找最相似 k 段   把片段塞进上下文 │
│                                                             │
│          → ⑧LLM 生成 → ⑨返回答案 + 引用来源                  │
└─────────────────────────────────────────────────────────────┘
```

**一句话记忆**：离线建库，在线检索增强生成。

---

## 3. 9 步关键概念拆解

| 步骤 | 干什么 | 关键参数 / 选型 | 面试常问 |
|---|---|---|---|
| ① 解析 | .md/.txt → 纯文本 | 保留标题层级 | 代码 / PDF 怎么解析？ |
| ② 分块 chunking | 长文档切成小段 | chunk_size、overlap | 太大太小各有什么问题？ |
| ③ Embedding | 文本 → 向量 | **选哪个模型** | 和关键词搜索区别？ |
| ④ 入库 | 向量 + 原文存进 FAISS | index 类型 | 为什么用向量库不用列表？ |
| ⑤ 问题向量化 | 用**同一个** Embedding 模型 | 必须和 ③ 一致 | 换模型会怎样？ |
| ⑥ 检索 | 余弦相似度找 top-k | k 取多少 | top-k 太大太小？ |
| ⑦ 拼 Prompt | 检索片段塞进 prompt | Prompt 模板 | 检索不到怎么办？ |
| ⑧ 生成 | LLM 基于片段回答 | 温度、模型 | 怎么防幻觉？ |
| ⑨ 引用 | 返回片段来源 | metadata 存文件名/位置 | 怎么做引用溯源？ |

Week 2 的 Day 2-6 就是把这 9 步一天实现一两个。

---

## 4. 向量库选型：FAISS（已定）

`pyproject.toml` 已装 `faiss-cpu>=1.14.3`，向量库就用 FAISS。

为什么是 FAISS 而不是 Chroma / PGVector / Milvus：

| 方案 | 适合场景 | 我们为什么不选 |
|---|---|---|
| **FAISS** ✅ | 单机、纯向量索引、轻量 | 学习项目够用，零额外服务 |
| Chroma | 单机，自带持久化和 metadata 过滤 | 多一个依赖，FAISS 已够 |
| PGVector | 已有 PostgreSQL，想要 SQL 联动 | 还没引入 PG |
| Milvus / Qdrant | 生产级分布式 | 太重，学习项目用不上 |

面试可讲：「选 FAISS 是因为单机、轻量、纯索引够用；如果要做 metadata 过滤或多用户，会换 Chroma；要上生产规模才考虑 Milvus。」

---

## 5. Embedding 选型：火山引擎（豆包）API（已定）

### 5.1 为什么不能跟着 LLM 用 DeepSeek

DeepSeek 没有提供 embedding 接口，所以 embedding 必须另选 provider。

### 5.2 候选对比

| 方案 | 优点 | 代价 |
|---|---|---|
| 本地 bge-small-zh | 免费、离线、可讲「为什么本地」 | 首次下载模型、建库慢、吃 CPU |
| OpenAI embedding | 质量稳定、生态好 | 国内需代理、计费 |
| **火山引擎（豆包）** ✅ | 国内直连、兼容 OpenAI 协议、复用 langchain-openai、有免费额度 | 多一个 API key |

### 5.3 选火山引擎的关键理由

1. **兼容 OpenAI 协议** → 直接用 `langchain_openai.OpenAIEmbeddings`，配 `base_url` 即可，**不用装新依赖**。
2. **国内直连** → 不用代理，和 DeepSeek 一样的开发体验。
3. **能复用现有配置模式** → 和 LLM 一样走 pydantic-settings + .env。

### 5.4 LangChain 1.x 接入写法（Day 4 会用到，先存个预览）

> 注意：是 `OpenAIEmbeddings`，不是已废弃的 `Embeddings` 旧写法。火山引擎 ARK 的 base_url 是 `https://ark.cn-beijing.volces.com/api/v3`。

```python
# 预览，Day 4 真正实现时再写到 app/services/embedding_client.py
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings

def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,        # 如 doubao-embedding-text-240715
        api_key=settings.EMBEDDING_API_KEY,
        base_url=settings.EMBEDDING_BASE_URL,  # https://ark.cn-beijing.volces.com/api/v3
    )
```

要点：

- `OpenAIEmbeddings` 来自 `langchain_openai`，已装。
- **离线建库（③）和在线查库（⑤）必须用同一个 model**，所以它要做成单例（参考 `llm_client.py` 的 `@lru_cache` 写法）。
- 模型名用火山引擎控制台里 embedding 模型的 ID。

### 5.5 .env.example 需要新增的字段（配置文件，自己改）

在 `.env.example` 里追加（和现有 `LLM_*` 并列）：

```bash
# Embedding（火山引擎豆包）
EMBEDDING_API_KEY=your-ark-api-key
EMBEDDING_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
EMBEDDING_MODEL=doubao-embedding-text-240715
```

对应的 `app/core/config.py` 也要加三个字段（`EMBEDDING_API_KEY: str` 等），Day 4 接入时一起做。

---

## 6. 本周（Week 2）路线回顾

| 天数 | 任务 | 对应 9 步里的 |
|---|---|---|
| Day 1 ✅ | 理解 RAG 全链路，确定向量库 + Embedding 方案 | 全局 |
| Day 2 | 实现文档读取和清洗 | ① |
| Day 3 | 实现 Chunking | ② |
| Day 4 | 接入 Embedding 并写入向量库 | ③ ④ |
| Day 5 | 实现相似度检索 | ⑤ ⑥ |
| Day 6 | 检索结果拼 Prompt 回答问题 | ⑦ ⑧ ⑨ |
| Day 7 | 复盘：记录 RAG 链路和关键参数 | — |

---

## 7. 验收清单

- [x] 能画出 RAG 离线 / 在线两阶段流程图
- [x] 能说出 9 个步骤各自的作用
- [x] 确定向量库：FAISS
- [x] 确定 Embedding：火山引擎豆包 API（OpenAI 兼容）
- [x] 知道离线/在线必须用同一个 Embedding 模型
- [ ] `.env.example` 追加 `EMBEDDING_*` 三个字段（自己做）

---

## 8. 面试可讲点

> "我的 RAG 链路分离线和在线两阶段。离线把文档解析、分块、向量化后存入 FAISS；在线把用户问题用同一个 Embedding 模型向量化，检索 top-k 片段，拼进 Prompt 让 LLM 基于片段回答，并返回引用来源。
>
> 选型上，向量库用 FAISS，因为单机轻量、纯索引够学习项目使用；Embedding 用火山引擎豆包 API，因为它兼容 OpenAI 协议、国内直连、能直接复用 langchain-openai 不用加依赖。
>
> 一个关键约束：离线建库和在线查库必须用同一个 Embedding 模型，否则向量空间不一致，检索结果会失效。"

---

## 9. 下一步：Day 2

**文档读取和清洗**（对应 ① 解析）。

- 在 `app/services/` 下新建文档处理模块
- 支持读取本地 `.md` / `.txt`
- 清洗：去掉多余空行、保留标题层级（标题后面 chunking 时有用）
- 暂不做向量化，只输出干净的纯文本

> 提醒：按 CLAUDE.md 代码学习模式，Day 2 的代码由你亲手写。我给思路和示例片段，你写完贴出来或让我读文件 review。
