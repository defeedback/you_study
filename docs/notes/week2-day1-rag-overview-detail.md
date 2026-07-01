# Week 2 · Day 1：RAG 全链路认知与技术方案

**日期**：2026-06-29  
**对应阶段**：2 个月路线 · 第 2 周 Day 1  
**主题**：理解 RAG 是什么、为什么需要 Embedding、确定 Week 2 技术方案

---

## 0. 一句话总结

> RAG 不是让大模型“记住所有文档”，而是让大模型在回答前先查到相关资料，再基于资料回答。

RAG 的核心流程可以概括为：

```text
先检索，再生成。
```

---

## 1. 为什么 JD 里经常要求 RAG

真实业务里，大模型通常不知道企业内部知识、项目文档、制度规范或私有代码库内容。

例如用户问：

```text
我们公司的报销制度里，差旅住宿标准是多少？
```

如果模型没有接入公司内部文档，它可能会：

1. 瞎编一个看起来合理的答案；
2. 回答不知道；
3. 给一个通用但不适用于当前公司的答案。

RAG 要解决的问题是：

> 把外部知识接入大模型，让模型根据检索到的资料回答问题。

JD 中常见关键词：

- RAG
- 知识库问答
- 向量数据库
- Embedding
- 文档切分
- 语义检索
- Top-K
- 引用来源
- 幻觉控制

面试表达：

> RAG 的核心价值是把外部知识接入大模型，让模型基于检索到的上下文回答问题，从而降低幻觉，并支持企业私有知识问答。

---

## 2. RAG 全链路

RAG 可以分成两条线：

1. 建库阶段
2. 查询阶段

---

## 3. 建库阶段

建库阶段负责把原始文档变成可以被检索的知识库。

```text
原始文档
  ↓
文档读取
  ↓
文本清洗
  ↓
文档切分 Chunking
  ↓
Embedding 向量化
  ↓
写入向量数据库
```

例子：

```text
docs/fastapi_notes.md
  ↓
读取 Markdown 文本
  ↓
清理多余空行
  ↓
切成多个 chunk
  ↓
每个 chunk 调用火山引擎 Embedding API
  ↓
向量 + 原文 + metadata 存进 FAISS
```

建库阶段的重点：

| 步骤 | 作用 |
|---|---|
| 文档读取 | 把 `.md` / `.txt` 文件读成字符串 |
| 文本清洗 | 去掉多余空行、无意义字符 |
| Chunking | 把长文档切成小片段 |
| Embedding | 把文本片段转成向量 |
| 向量库 | 存储向量，并支持相似度检索 |

---

## 4. 查询阶段

查询阶段负责根据用户问题找到相关资料，再让大模型回答。

```text
用户问题
  ↓
问题 Embedding
  ↓
向量库相似度检索
  ↓
取 Top-K 文档片段
  ↓
拼接到 Prompt
  ↓
调用 LLM
  ↓
返回答案
```

例子：

```text
用户问：FastAPI 中间件有什么作用？
  ↓
把问题转成向量
  ↓
在向量库中找到最相关的 3 个 chunk
  ↓
把 chunk 拼进 Prompt
  ↓
要求模型只根据资料回答
  ↓
返回答案
```

---

## 5. 为什么不能直接把整篇文档塞给模型

原因主要有 4 个：

1. 上下文窗口有限
2. token 成本高
3. 文档内容太多，无关噪音多
4. 模型容易被无关内容干扰，导致回答不聚焦

所以 RAG 不是把所有资料都塞给模型，而是：

```text
先找出最相关的资料，再交给模型回答。
```

面试表达：

> 直接把整篇文档塞给模型会带来上下文长度、成本和噪音问题。文档越长，无关信息越多，模型越容易被干扰。RAG 的做法是先检索出和问题最相关的片段，再把这些片段作为上下文交给模型，从而降低成本并提升回答相关性。

---

## 6. Embedding 是什么

Embedding 的作用是：

> 把文本映射到向量空间，让程序可以用数学方式计算文本之间的语义相似度。

例子：

```text
文本 A：如何创建 FastAPI 路由？
文本 B：FastAPI 的 APIRouter 怎么用？
文本 C：今天天气不错
```

人能看出 A 和 B 更相关，但程序不能直接理解语义。

Embedding 后大概变成：

```python
A -> [0.12, -0.08, 0.45, ...]
B -> [0.10, -0.07, 0.43, ...]
C -> [-0.33, 0.51, 0.02, ...]
```

然后可以计算向量距离：

```text
A 和 B 距离近
A 和 C 距离远
```

所以：

> Embedding 是 RAG 的“语义坐标系”。

---

## 7. 关键词搜索 vs 语义搜索

传统关键词搜索看的是：

```text
字面是否匹配
```

Embedding 语义搜索看的是：

```text
语义是否接近
```

例子：

```text
用户问：FastAPI 怎么统一处理错误？
文档写：全局异常处理器可以统一返回错误响应。
```

两句话关键词不完全一样，但语义接近。Embedding 检索更容易把它们匹配起来。

---

## 8. Chunk 是什么

Chunk 是从长文档中切出来的小片段。

为什么要切 chunk？

1. 长文档不适合整体检索
2. 小片段更容易精确匹配问题
3. 可以减少传给模型的上下文长度
4. 可以降低无关内容干扰

例子：

```text
原文 3000 字
  ↓
chunk 1：第 1-500 字
chunk 2：第 451-950 字
chunk 3：第 901-1400 字
```

---

## 9. Chunk overlap 是什么

`chunk_overlap` 是相邻 chunk 之间的重叠部分。

例如：

```python
chunk_size = 500
chunk_overlap = 50
```

对应切分：

```text
chunk 1：0-500
chunk 2：450-950
chunk 3：900-1400
```

为什么需要 overlap？

> 防止固定长度切分时，把句子、段落或上下文关系切断。

例子：

```text
FastAPI 中间件会在请求进入路由前执行。它常用于记录日志、计算耗时和添加 trace_id。
```

如果没有 overlap，可能切成：

```text
chunk 1：FastAPI 中间件会在请求进入路由前执行。
chunk 2：它常用于记录日志、计算耗时和添加 trace_id。
```

第二个 chunk 中的“它”指代不清，单独检索出来时语义会变弱。

有 overlap 后，可以保留上下文连续性。

---

## 10. Top-K 是什么

Top-K 表示检索时返回最相关的 K 个文档片段。

例如：

```python
top_k = 3
```

表示：

```text
从向量库中找出和用户问题最相似的 3 个 chunk。
```

K 太小：

- 可能漏掉关键信息。

K 太大：

- 噪音变多；
- Prompt 变长；
- 模型更容易被无关内容干扰。

Week 2 初始建议：

```python
top_k = 3
```

---

## 11. Week 2 技术方案

当前项目 Week 2 暂定方案：

| 模块 | 选择 |
|---|---|
| Embedding | 火山引擎 Ark API |
| 向量库 | FAISS |
| 文档格式 | Markdown / TXT |
| 初始 top_k | 3 |
| 初始 chunk_size | 500 |
| 初始 chunk_overlap | 50 |

---

## 12. 为什么不必强行使用 OpenAI 风格

RAG 真正需要的 Embedding 能力是：

```python
texts: list[str] -> vectors: list[list[float]]
```

只要能把文本列表转成向量列表，底层用哪个供应商都可以：

- OpenAI Embedding
- 火山引擎 Ark Embedding
- 通义千问 Embedding
- 本地 bge 模型
- Ollama Embedding

本项目计划直接封装火山引擎 Embedding API：

```text
EmbeddingService
  ↓
读取 .env 中的火山引擎 API Key
  ↓
调用 Ark Embedding 接口
  ↓
解析返回的 embedding 数组
  ↓
返回 list[list[float]]
```

这样更有利于理解 Embedding API 的真实工作方式，而不是被框架封装隐藏细节。

---

## 13. 计划中的项目模块

后续 Week 2 可能逐步增加这些模块：

```text
app/
  services/
    embedding_service.py      # 调火山引擎 Embedding API
    document_loader.py        # 读取 md/txt
    chunk_service.py          # 文本切块
    vector_store.py           # FAISS 写入和检索
    rag_service.py            # RAG 总编排

  api/
    rag.py                    # /rag/query 接口

  schemas/
    rag.py                    # RAG 请求/响应模型

knowledge_base/
  raw/                        # 原始文档
  index/                      # FAISS 索引文件
```

模块分工：

| 模块 | 作用 |
|---|---|
| `document_loader.py` | 把文件读成文本 |
| `chunk_service.py` | 把长文本切成 chunk |
| `embedding_service.py` | 把 chunk 转成向量 |
| `vector_store.py` | 存向量、查相似片段 |
| `rag_service.py` | 检索 + 拼 Prompt + 调 LLM |
| `rag.py` | 暴露 API 接口 |

---

## 14. 最小 RAG 伪代码

```python
# 1. 读取文档
text = read_file("knowledge_base/raw/fastapi.md")

# 2. 切块
chunks = split_text(text, chunk_size=500, overlap=50)

# 3. 每个 chunk 转 embedding
vectors = embedding_service.embed_texts(chunks)

# 4. 写入向量库
vector_store.add(vectors, chunks)

# 5. 用户提问
question = "FastAPI 中间件有什么作用？"

# 6. 问题也转 embedding
query_vector = embedding_service.embed_texts([question])[0]

# 7. 相似度检索
matched_chunks = vector_store.search(query_vector, top_k=3)

# 8. 拼 Prompt
context = "\n\n".join(matched_chunks)

prompt = f"""
请只根据以下资料回答问题。

资料：
{context}

问题：
{question}
"""

# 9. 调 LLM 回答
answer = llm.invoke(prompt)
```

---

## 15. 今日问答复盘

### 问题 1：RAG 为什么不能直接把整篇文档塞给模型？

回答：

> 整篇文档塞给模型，会导致上下文很长，token 成本比较高；文档内容过多，不够集中，导致模型回答可能偏题。

补充：

> RAG 通过先检索相关片段，再把片段交给模型回答，可以减少无关噪音，提高回答聚焦度。

---

### 问题 2：Embedding 在 RAG 中解决什么问题？

回答：

> Embedding 解决语义搜索问题。通过 Embedding 后，文本被转化为向量，可以用于向量相似性检索。

补充：

> 它让系统不仅能按关键词匹配，还能按语义相似度匹配。

---

### 问题 3：chunk overlap 是为了解决什么问题？

回答：

> 防止在固定 chunk 长度的时候，把一些句子给拆散。

补充：

> overlap 还能保留上下文连续性，避免后一个 chunk 中出现“它”“这个方法”等指代不清的问题。

---

## 16. 今日验收标准

Day 1 结束后，需要能说清楚：

```text
RAG = 检索增强生成。
建库阶段：文档读取 → 切块 → Embedding → 存向量库。
查询阶段：问题 Embedding → 向量检索 → 拼 Prompt → LLM 回答。
Embedding 用来计算语义相似度。
Chunking 是为了让检索更精确，也避免上下文太长。
Overlap 是为了避免切断句子和上下文。
```

---

## 17. 下一步：Week 2 Day 2

Day 2 主题：

> 文档读取和清洗。

目标是让项目支持读取：

```text
knowledge_base/raw/*.md
knowledge_base/raw/*.txt
```

并统一转换成类似结构：

```python
{
    "content": "文档正文",
    "metadata": {
        "source": "fastapi_notes.md"
    }
}
```

Day 2 暂时不做 Embedding，也不做 FAISS，先把“原始文件 → 干净文本”这一步打牢。
