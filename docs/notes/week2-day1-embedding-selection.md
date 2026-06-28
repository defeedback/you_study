# Week 2 · Day 1 补充：如何选择合适的 Embedding 模型

**日期**：2026-06-28
**对应阶段**：2 个月路线 · 第 2 周 Day 1
**主题**：Embedding 选型方法论 + 本项目选型理由
**关联**：[week1-day4-structured-output.md](../week1-day4-structured-output.md)、[week2-day1-rag-overview.md](week2-day1-rag-overview.md)

---

## 0. 一句话总结

> 选 embedding 不是选"最强"，而是在 5 个维度上做权衡：**语言匹配、质量（C-MTEB）、向量维度（成本）、上下文长度（和 chunk_size 联动）、部署方式（API/本地）**。
> 本项目最终选火山引擎豆包 API——多语言、国内直连、兼容 OpenAI 协议能复用 `langchain_openai`。

---

## 1. 为什么这个问题重要

Embedding 是 RAG 的地基：

- 它决定"语义相似"靠不靠谱——检索准不准，一半以上取决于它。
- 它是**最难换的组件**：换一次要把全库重新向量化，成本和换 LLM 完全不在一个量级。
- 选型理由能直接暴露候选人对「成本 / 质量 / 部署 / 语言」的综合判断力。

所以面试官问"你怎么选 embedding 模型"，要的不是名字，而是**在多约束下做权衡并讲清理由**。

---

## 2. 整体认知：5 个维度的权衡

Embedding 模型本质是 `文本 → 定长向量` 的函数。选型在 5 个维度上找平衡：

```text
        质量（C-MTEB 检索分）
            ↑
            │
   多语言 ←──┼──→ 单语言（中文/英文）
            │
   本地部署 ←┼──→ API 调用
            │
   维度(768/1024/1536/3072) ← 成本 & 存储
            │
   上下文长度(512/8192) ← 单次能编码多长的文本
```

**核心权衡永远是：质量 ↔ 成本 ↔ 部署复杂度**。没有"最好"，只有"对这个场景最合适"。

---

## 3. 五个关键维度

### 3.1 语言匹配

| 你的语料 | 该选 |
|---|---|
| 纯英文 | 英文模型（OpenAI text-embedding-3、bge-en） |
| 纯中文 | 中文模型（bge-large-zh、m3e、豆包中文） |
| 中英混合 / 代码 | **多语言模型**（bge-m3、multilingual-e5、豆包多语言） |

> 本项目是「技术学习 + 代码仓库探索」，文档会中英混排（中文笔记 + 英文代码注释），**多语言能力**是加分项。豆包 embedding 对中英混合表现稳定。

### 3.2 质量基准：MTEB / C-MTEB 榜单

别凭感觉，看榜单：

- **MTEB**（Massive Text Embedding Benchmark）是业界公认标准评测，覆盖检索、分类、聚类等。
- 中文检索看 **C-MTEB** 榜单。
- **不要只看总分，看 Retrieval 子任务分数**——那才是 RAG 关心的。
- 榜单地址：`https://github.com/FlagOpen/FlagEmbedding`（BAAI 维护）。

> 面试可讲："我看 embedding 质量主要参考 C-MTEB 检索子任务分数，而不是综合分，因为 RAG 只关心检索能力。"

### 3.3 向量维度 = 成本和存储

| 维度 | 存储（每百万 chunk） | 检索速度 | 典型模型 |
|---|---|---|---|
| 768 | ~3 GB | 快 | bge-small/large-zh |
| 1024 | ~4 GB | 中 | bge-m3、e5 |
| 1536 | ~6 GB | 慢 | OpenAI text-embedding-3-small |
| 3072 | ~12 GB | 最慢 | OpenAI text-embedding-3-large |

> 维度翻倍 ≠ 质量翻倍，但存储和检索成本实打实翻倍。学习项目用 1024 或 1536 都够，没必要追 3072。

### 3.4 上下文长度

模型一次能编码多长的文本。**短上下文（512）逼你切更小的块**，长上下文（8192）允许更大的块。

- bge-small-zh：512
- 豆包 embedding：通常 4096+
- bge-m3：8192

> 它和 chunk_size 联动——选 512 上下文的模型，却切 1000 字的块，模型会**截断后半段**，检索直接失效。这是 Week 2 Day 3 chunking 的隐藏约束。

### 3.5 部署方式：API 还是本地

| | API（豆包/OpenAI） | 本地（bge/m3e） |
|---|---|---|
| 接入成本 | 低，几行配置 | 中，要装 sentence-transformers + 下载模型 |
| 延迟 | 网络 RTT，但有批量加速 | 首次慢，之后纯本地 |
| 离线可用 | ❌ | ✅ |
| 隐私 | 文本出本机 | ✅ 数据不出 |
| 成本 | 按 token 计费 | 免费，吃 CPU/GPU |

---

## 4. 决策树

```text
你的文档是否敏感 / 需要离线？
├─ 是 → 本地模型（bge-m3 多语言 / bge-large-zh 纯中文）
└─ 否 → 走 API
        │
        国内网络能否直连 OpenAI？
        ├─ 能 → OpenAI text-embedding-3-small（1536 维，质量稳）
        └─ 不能 → 国内 API
                  │
                  是否中英 / 代码混排？
                  ├─ 是 → 豆包多语言 / bge-m3 API
                  └─ 否 → 豆包中文 / 智谱 / 通义
```

---

## 5. 本项目选型对照

按 5 个维度逐条对照，验证火山引擎豆包是否合适：

| 维度 | 本项目情况 | 豆包是否合适 |
|---|---|---|
| 语言 | 中英混排（中文笔记 + 英文代码） | ✅ 多语言支持 |
| 质量 | C-MTEB 检索分中上 | ✅ 够学习项目 |
| 维度 | 1024/2048 可选 | ✅ 成本可控 |
| 上下文 | 4096+ | ✅ 块可以切大点 |
| 部署 | 不要求离线，要国内直连 | ✅ 直连，复用 langchain-openai |

### 5.1 一个潜在风险点（面试官会追问）

> 后期「代码仓库探索 Agent」（Week 6）要把代码向量化时，代码不是自然语言，通用 embedding 对代码语义捕捉一般。到那时候可能要考虑**代码专用 embedding**（如 `voyage-code`），或直接用代码结构化检索替代向量检索。
> 这是 **Week 6 的选型再评估点**，不是现在的事。

### 5.2 接入写法预览（Day 4 真正实现）

```python
# 预览，Day 4 写到 app/services/embedding_client.py
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

- `OpenAIEmbeddings` 来自 `langchain_openai`，已装，不用加依赖。
- **离线建库和在线查库必须用同一个 model**，做成单例（参考 `llm_client.py` 的 `@lru_cache`）。
- 模型名用火山引擎控制台里 embedding 模型的 ID。

---

## 6. 最小实践任务：相似度对比（建议做一次）

建 `app/scripts/compare_embeddings.py`（**自己写**，给思路）：

1. 准备 5 对句子：3 对语义相近、2 对不相近（中英混合，含一句代码注释）。
2. 用豆包 API 把它们都向量化。
3. 算每对之间的**余弦相似度**。
4. 观察：相近的对应 > 0.8？不相近的应 < 0.5？

预期产出：一张表，亲眼看到"语义相近 → 向量也近"成立。比看任何文档都管用，也是面试能说"我做过验证"的底气。

关键 API：

- `OpenAIEmbeddings(...).embed_documents([...])` 批量向量化
- `OpenAIEmbeddings(...).embed_query("...")` 单条
- 相似度：`numpy` 算余弦，或 `sklearn.metrics.pairwise.cosine_similarity`

---

## 7. 易错点

| 错误 | 原因 | 正确做法 |
|---|---|---|
| 离线建库用 A 模型，在线查库用 B 模型 | 换了模型没重新向量化 | 全库必须同一个模型，换模型 = 全库重建 |
| chunk_size > 模型上下文长度 | 模型截断后半段，检索失效 | chunk_size 留在上下文长度内 |
| 只看 MTEB 综合分选模型 | 综合分含聚类/分类，不代表检索能力 | 看 Retrieval 子任务分 |
| 代码用通用 embedding | 代码语义捕捉差 | Week 6 评估代码专用 embedding 或结构化检索 |

---

## 8. 面试可讲点

> "选 embedding 模型我看五个维度：语言匹配、C-MTEB 检索分、向量维度（成本）、上下文长度（和 chunk_size 联动）、部署方式（API/本地）。
>
> 我的项目是中英混排、不要求离线、要国内直连，所以选了火山引擎豆包——它兼容 OpenAI 协议能复用 langchain-openai、多语言、成本可控。
>
> 一个关键约束是离线建库和在线查库必须用同一个模型，否则向量空间不一致，检索会失效。另外我注意到代码场景下通用 embedding 表现一般，留到 Week 6 代码仓库 Agent 时再评估代码专用方案。"

---

## 9. 关联

- 全链路认知见 [week2-day1-rag-overview.md](week2-day1-rag-overview.md)
- Week 6 代码仓库 Agent 的 embedding 再评估，见未来 `docs/notes/week6-*.md`
