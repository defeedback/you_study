# Week 2 · Day 1 补充：RAG 9 步面试问答 + 工程化做法

**日期**：2026-06-28
**对应阶段**：2 个月路线 · 第 2 周 Day 1
**主题**：RAG 9 个步骤，每步的面试高频问题 + 工程化落地做法
**关联**：[week2-day1-rag-overview.md](week2-day1-rag-overview.md)、[week2-day1-embedding-selection.md](week2-day1-embedding-selection.md)

---

## 0. 怎么用这篇笔记

9 步表格里的"面试常问"展开成两部分：

- **面试会怎么问**：面试官的真实问法 + 他在考察什么。
- **工程化实际做法**：本项目（FAISS + 豆包 + LangChain 1.x + FastAPI）里具体怎么做。

按顺序记，面试时被问任何一个都能答到点。

---

## ① 解析：代码 / PDF 怎么解析？

### 面试会怎么问

- "你的 RAG 文档解析支持哪些格式？"
- "Markdown 文档怎么保留结构？"
- "PDF 里的表格、图片怎么处理？"
- "代码文件解析和普通文档有什么不同？"

考察点：是否理解**不同格式要不同 loader**，以及结构信息对后续 chunking 的影响。

### 工程化实际做法

| 格式 | 工具 | 关键点 |
|---|---|---|
| .md | LangChain `TextLoader` 或自己读 | **保留标题层级**（`#`/`##`），chunking 时可按标题切 |
| .txt | `TextLoader` | 纯文本，无结构 |
| .pdf | `PyPDFLoader` / `UnstructuredPDFLoader` | 表格会丢，复杂版面用 unstructured |
| 代码 .py | 当文本读 + 按 **函数/类** 切分 | 用 AST 切比按字数切更合理 |

本项目的选择：

- Week 2 先支持 `.md` / `.txt`，用 `TextLoader` 或直接 `path.read_text(encoding="utf-8")`。
- Week 6 代码仓库探索时，代码文件按**语法结构**（函数、类）切分，不是按固定字数。

工程要点：

- 编码统一 UTF-8，Windows 下读文件别忘指定 `encoding="utf-8"`，否则中文乱码。
- 解析后保留 `source`（文件路径）作为 metadata，后面 ⑨ 引用要用。

---

## ② 分块 chunking：chunk 太大太小各有什么问题？

### 面试会怎么问

- "chunk_size 怎么选？你是凭感觉还是有依据？"
- "chunk 太大或太小会怎样？"
- "overlap 是干嘛的？为什么要有？"
- "你是按固定字数切还是按语义切？"

考察点：是否理解 chunk_size 和 overlap 的 trade-off，而不是照搬默认值。

### 工程化实际做法

| chunk_size | 问题 |
|---|---|
| 太大（>2000）| 一个 chunk 含多个主题，检索时噪声多；超出 embedding 上下文会被截断；LLM 上下文被占满 |
| 太小（<200）| 语义不完整，一句话被切成两半，检索到也读不懂 |

| overlap | 作用 |
|---|---|
| 有（如 50-200）| 防止关键句被切到两块的边界上，保证语义连续 |
| 太大 | 重复内容多，浪费存储和上下文 |

**起步默认值**（本项目 Week 2 用）：

```text
chunk_size = 500
overlap    = 50
```

LangChain 1.x 写法（`RecursiveCharacterTextSplitter`，递归按 `["\n\n", "\n", " ", ""]` 切，尽量在段落边界断开）：

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""],
)
chunks = splitter.split_text(text)
```

进阶（Week 3 优化）：

- **按 Markdown 标题切**：`MarkdownHeaderTextSplitter` 先按 `#`/`##` 切，再按字数切。
- **chunk_size 和 embedding 上下文联动**：见 [week2-day1-embedding-selection.md](week2-day1-embedding-selection.md) 3.4，chunk_size 不能超过模型上下文长度。

---

## ③ Embedding：和关键词搜索（BM25）有什么区别？

### 面试会怎么问

- "Embedding 检索和关键词搜索（BM25）有什么区别？"
- "什么场景下关键词搜索反而比向量检索好？"
- "你为什么用向量检索？"

考察点：是否理解**语义匹配 vs 字面匹配**。

### 工程化实际做法

| | 关键词搜索（BM25） | 向量检索（Embedding） |
|---|---|---|
| 匹配方式 | 字面 token 重合 | 语义相似 |
| "如何部署项目" 能否匹配 "怎么启动服务" | ❌ 词不一样 | ✅ 语义相近 |
| 专有名词 / 代码标识符 / 人名 | ✅ 精确匹配强 | ❌ 可能被语义带偏 |
| 依赖 | 倒排索引即可 | embedding 模型 + 向量库 |
| 成本 | 低 | 高（向量化 + 存储） |

本项目选向量检索的理由：技术文档问答大量是**同义改写**（用户口语 vs 文档书面语），语义匹配明显优于字面匹配。

进阶做法（Week 3 可选）：**混合检索（Hybrid Search）**

```text
向量检索 top-k  +  BM25 top-k  →  加权融合  →  最终 top-k
```

LangChain 1.x 用 `EnsembleRetriever` 把 `FAISS retriever` 和 `BM25Retriever` 组合。混合检索能兼顾"语义相近"和"专有名词精确"，是生产 RAG 的常见配置。

---

## ④ 入库：为什么要向量库而不是放列表里？

### 面试会怎么问

- "为什么不直接把向量存个 Python list，每次算余弦？"
- "FAISS 比暴力遍历快在哪？"
- "FAISS / Chroma / Milvus 怎么选？"

考察点：是否理解**向量检索的规模问题**和近似最近邻（ANN）。

### 工程化实际做法

暴力遍历的问题：

- N 个 chunk × 每个向量 1024 维 → 每次查询要算 N 次余弦。
- 文档一多（10 万级），单次查询几百毫秒到秒级，不可用。

向量库的作用：

- **FAISS** 用 ANN 索引（如 `IndexFlatIP` 精确、`IndexIVFFlat` 倒排近似、`HNSW` 图近似），把 O(N) 降到 O(logN) 级别。
- 还负责**持久化**（存盘 / 加载）和**向量 + 原文 + metadata 一起管理**。

FAISS index 类型选择：

| Index | 特点 | 适合 |
|---|---|---|
| `IndexFlatIP` | 精确，暴力但内积快 | 小库（<10万），学习项目用这个 |
| `IndexIVFFlat` | 倒排近似，需训练 | 中等规模 |
| `HNSW` | 图近似，查询快、内存大 | 大规模、低延迟 |

本项目 Week 2 用 `IndexFlatIP`（配合 L2 归一化后等价余弦），简单可靠，量小够用。

LangChain 集成：`FAISS.from_documents(docs, embedding)` 一行建库，`.save_local()` / `.load_local()` 持久化。

FAISS vs 其他：

- **FAISS**：纯向量索引，轻量，单机 ✅ 本项目
- **Chroma**：自带持久化 + metadata 过滤，单机，比 FAISS 多一层封装
- **Milvus / Qdrant**：分布式，生产规模

---

## ⑤ 问题向量化：换模型会怎样？

### 面试会怎么问

- "离线建库和在线查库能用不同 embedding 模型吗？"
- "我中途想换 embedding 模型怎么办？"
- "为什么必须同一个模型？"

考察点：是否理解**向量空间一致性**。

### 工程化实际做法

为什么必须同一个模型：

- 每个模型把文本映射到**自己的向量空间**，维度和语义分布都不同。
- A 模型建库的向量，和 B 模型的问题向量，**根本不在同一个空间**，算余弦相似度毫无意义。

换模型的代价：

```text
换 embedding 模型 = 全库重新向量化 = 重新跑一次离线建库流程
```

这是 embedding 选型要慎重的根本原因（见 [week2-day1-embedding-selection.md](week2-day1-embedding-selection.md)）。

工程上防错的做法：

- embedding 客户端做**单例**（`@lru_cache`），保证全流程只初始化一次、用同一个 model 名。
- 在向量库 metadata 里记录**建库用的 embedding 模型名**，加载时校验，不一致就报错而不是静默用错。

```python
# 伪代码：加载时校验模型一致性
meta = faiss_index_to_meta(index)
if meta["embedding_model"] != settings.EMBEDDING_MODEL:
    raise AppException(code="EMBEDDING_MISMATCH",
                       message="向量库与当前 embedding 模型不一致，请重建")
```

---

## ⑥ 检索：top-k 太大太小？

### 面试会怎么问

- "top-k 怎么定？"
- "top-k 太大或太小会怎样？"
- "怎么知道检索结果好不好？"

考察点：是否理解 top-k 对答案质量的影响。

### 工程化实际做法

| top-k | 问题 |
|---|---|
| 太小（k=1）| 只捞一条，万一不相关就没了退路；多相关片段时漏召回 |
| 太大（k=20）| 噪声多，无关片段塞进 prompt 拖累答案、占满上下文、增加成本 |

**起步默认值**：`k = 3 ~ 5`，技术文档问答够用。

进阶：

- **相似度阈值过滤**：不只看 top-k，还设阈值，相似度低于 0.5 的 chunk 即使进了 top-k 也丢掉——防"库里根本没有相关内容却硬塞"。
- **Rerank**（Week 3）：先用向量检索粗召回 top-20，再用 rerank 模型精排到 top-5，质量显著提升。

LangChain 写法：

```python
retriever = vector_store.as_retriever(search_kwargs={"k": 4})
docs = retriever.invoke("用户问题")
```

---

## ⑦ 拼 Prompt：检索不到怎么办？

### 面试会怎么问

- "如果检索结果和问题不相关，你怎么处理？"
- "知识库里没有的问题，你的系统会怎么回答？"
- "怎么防止模型硬编答案？"

考察点：是否做了**检索结果质量判断**和**兜底策略**——这是区分玩具 RAG 和工程 RAG 的关键。

### 工程化实际做法

玩具做法：不管检索到什么，全塞进 prompt 让 LLM 答 → 容易幻觉。

工程做法（分层）：

1. **相似度阈值判断**：检索最高分低于阈值 → 判定"知识库无相关内容"。
2. **Prompt 明确约束**：告诉模型"只能基于以下片段回答，片段没有就回答不知道"。
3. **兜底响应**：判定无相关内容时，直接返回"知识库中未找到相关内容"，不调 LLM 或让 LLM 明确说不知道。

Prompt 模板（本项目 Week 2 用）：

```text
你是一个技术知识库问答助手。请严格基于下方【参考资料】回答问题。
如果参考资料中没有相关内容，请直接回答"知识库中未找到相关内容"，不要编造。

【参考资料】
{context}

【问题】
{question}
```

工程要点：

- `context` 拼接时给每个片段加**编号和来源**，方便 ⑨ 引用：
  ```text
  [1] (来源：docs/abc.md) 片段内容...
  [2] (来源：docs/def.md) 片段内容...
  ```
- 片段总数 / 总长度做上限，超出就截断或减少 k，防 prompt 爆长。

---

## ⑧ 生成：怎么防幻觉？

### 面试会怎么问

- "你的 RAG 怎么防止幻觉？"
- "模型还是编造了答案怎么办？"
- "温度参数怎么设？"

考察点：是否有多层防幻觉手段，而不是只靠 prompt。

### 工程化实际做法

防幻觉是**多层叠加**的，不是一招：

| 层 | 手段 | 作用 |
|---|---|---|
| 检索层 | 相似度阈值 + top-k 控制 | 不相关的别塞进 prompt |
| Prompt 层 | "只基于片段答，没有就说不知道" | 约束模型行为 |
| 生成层 | **温度调低**（0~0.3） | 降低随机性，减少发散 |
| 后处理层 | 引用溯源 + 答案与片段一致性检查 | 答案要能对应到片段 |
| 评测层 | 评测集 + 幻觉标注（Week 3） | 量化幻觉率，持续改进 |

温度参数：

- 问答场景 `temperature = 0 ~ 0.3`，要稳定事实性。
- 创作场景才用 0.7+。本项目 `/chat` 现在是 0.7，RAG 问答接口建议单独设 0.2。

进一步（Week 3）：

- 让模型输出时**标注引用编号**（如"根据 [1]，..."），便于核对。
- 评测集里专门标"知识库无答案"的问题，看系统会不会硬编。

---

## ⑨ 引用：怎么做引用溯源？

### 面试会怎么问

- "你的回答怎么附引用来源？"
- "用户怎么知道答案从哪来的？"
- "引用是文件级还是片段级？"

考察点：是否做了**可追溯性**——企业 RAG 的硬需求。

### 工程化实际做法

引用的关键在**从一开始就带 metadata**，不是事后补：

1. **解析时**（①）：每个 chunk 带 `source`（文件路径）。
2. **chunking 时**（②）：可加 `chunk_index`、`heading`（所属标题）。
3. **检索后**（⑥）：拿到 top-k chunk，连 metadata 一起返回。
4. **响应里**（⑨）：把来源信息回传给前端。

引用粒度：

| 粒度 | 例子 | 适合 |
|---|---|---|
| 文件级 | "来源：docs/abc.md" | 简单，学习项目起步 |
| 片段级 | "来源：docs/abc.md 第 3 段" | 更精确，推荐 |
| 字符级 | "来源：docs/abc.md L42-58" | 最精确，复杂 |

本项目 Week 2 起步：文件级 + 片段序号。

响应结构（Pydantic，配合 Day 4 学的 structured output）：

```python
class Citation(BaseModel):
    source: str          # 文件路径
    snippet: str         # 片段内容（可截断）
    score: float         # 检索相似度

class RagAnswer(BaseModel):
    answer: str
    citations: list[Citation]
```

工程要点：

- 片段内容截断返回（如前 200 字），别把整块塞响应里。
- 引用编号和 prompt 里的 `[1][2]` 对应，方便用户核对。

---

## 10. 一张图串起来（面试可用）

```text
用户问题
   │
   ├─⑤ Embedding（同一模型）─→ ⑥ FAISS 检索 top-k
   │                              │
   │                              ├─ 相似度阈值过滤（防不相关）
   │                              └─ 带 metadata（source / chunk_index）
   │
   ├─⑦ 拼 Prompt（"只基于片段答，没有就说不知道"）
   │
   ├─⑧ LLM 生成（temperature=0.2）
   │
   └─⑨ 返回 answer + citations[]  ← 引用溯源
```

---

## 11. 高频追问汇总（按面试顺序）

1. **"讲讲你的 RAG 完整链路"** → 用上面的图 + 9 步。
2. **"chunk_size 怎么选"** → ②，500 起步，按文档类型调，和 embedding 上下文联动。
3. **"为什么用向量检索不用 BM25"** → ③，语义匹配；进阶说混合检索。
4. **"为什么用 FAISS"** → ④，单机轻量；量大了换 Chroma/Milvus。
5. **"换 embedding 怎么办"** → ⑤，全库重建，所以选型慎重。
6. **"top-k 怎么定"** → ⑥，3-5 起步 + 阈值过滤。
7. **"检索不到怎么办"** → ⑦，阈值判断 + prompt 约束 + 兜底"不知道"。
8. **"怎么防幻觉"** → ⑧，多层：检索过滤 + prompt + 低温 + 引用 + 评测。
9. **"引用怎么做的"** → ⑨，解析时就带 metadata，片段级引用。

---

## 12. 关联

- 9 步全链路见 [week2-day1-rag-overview.md](week2-day1-rag-overview.md)
- Embedding 选型见 [week2-day1-embedding-selection.md](week2-day1-embedding-selection.md)
- Week 3 RAG 优化（rerank、评测、引用增强）见未来 `docs/notes/week3-*.md`
