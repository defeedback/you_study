# Week 2 · Day 3：Chunking 文本切块

**日期**：2026-06-29  
**对应阶段**：2 个月路线 · 第 2 周 Day 3  
**主题**：把 `RawDocument` 切成多个 `DocumentChunk`，并保留来源 metadata

---

## 0. 一句话总结

> Chunking 就是把一篇长文档切成多个语义相对完整的小片段，让后续 Embedding 和检索更精准。

今天完成的是 RAG 建库阶段的第二步：

```text
RawDocument
  ↓
Chunking
  ↓
DocumentChunk（多个）
```

---

## 1. 为什么需要 Chunking

如果用户只问一个具体问题：

```text
FastAPI 中间件有什么作用？
```

却把整篇 3000 字文档拿去做 Embedding 和检索，会带来问题：

1. 文档太长，向量语义被“平均化”，不够聚焦
2. 检索精度下降
3. 拼 Prompt 时无关内容（噪音）变多
4. token 成本更高

所以建库阶段要先把文档切成更小的片段。

---

## 2. chunk 大小的权衡

### 2.1 chunk 太大

例如 `chunk_size = 3000`：

- 一个 chunk 里混合多个主题
- 检索时虽然相关，但噪音多
- 回答容易发散

### 2.2 chunk 太小

例如 `chunk_size = 50`：

- 语义不完整
- 可能切出“中间件可以在请求进入路由前”这种半句话
- 模型缺乏上下文，理解困难

### 2.3 初版推荐值

```python
chunk_size = 500
chunk_overlap = 50
```

这不是绝对最优，但适合最小 RAG Demo。后续可以通过评测再调整。

---

## 3. 数据结构：DocumentChunk

```python
class DocumentChunk(BaseModel):
    content: str
    metadata: dict[str, str]
```

它和 `RawDocument` 字段相同，但语义不同：

| 类型 | 含义 |
|---|---|
| `RawDocument` | 一整篇原始文档 |
| `DocumentChunk` | 从原始文档切出来的一个片段 |

---

## 4. 分层调整：schema 与 service 分离

今天把数据模型从 service 移到了 schema 层：

```python
from app.schemas.chunk import DocumentChunk, RawDocument
```

好处：

- `schemas/` 放数据结构（数据是什么）
- `services/` 放业务逻辑（怎么处理数据）
- 分层清晰，符合项目已有的 FastAPI 分层风格

注意点：

> 一旦把 `RawDocument` 移到 `schemas/chunk.py`，`document_loader.py` 也必须从同一个位置导入 `RawDocument`，否则会出现两个不同的 `RawDocument` 类，类型对不上。

原则：

```text
同一个数据模型，全项目只能有一个定义来源。
```

---

## 5. metadata 继承 + 新增 chunk_index

原始文档 metadata：

```python
{
    "source": "fastapi_notes.md",
    "file_path": "knowledge_base/raw/fastapi_notes.md",
}
```

切块后每个 chunk 的 metadata：

```python
{
    "source": "fastapi_notes.md",
    "file_path": "knowledge_base/raw/fastapi_notes.md",
    "chunk_index": "0",
}
```

由于 `metadata` 类型是 `dict[str, str]`，`chunk_index` 要存成字符串：

```python
"chunk_index": str(index)
```

不要写成整数 `"chunk_index": index`，否则类型不一致。

---

## 6. 字典解包 `**`

```python
metadata = {
    **document.metadata,
    "chunk_index": str(index),
}
```

`**document.metadata` 会把原 metadata 的所有键值“摊开”放进新字典，再追加 `chunk_index`。

等价于：

```python
metadata = {
    "source": "fastapi_notes.md",
    "file_path": "knowledge_base/raw/fastapi_notes.md",
    "chunk_index": "0",
}
```

作用：

> 保留原文档来源信息，同时给每个 chunk 加上自己的编号。

---

## 7. 核心切块函数 split_text

```python
def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks
```

切分逻辑（`chunk_size=500, chunk_overlap=50`）：

```text
chunk 0：0-500
chunk 1：450-950
chunk 2：900-1400
```

每次窗口前进 `chunk_size - chunk_overlap = 450`，相邻 chunk 重叠 50 个字符。

---

## 8. 防御：overlap 不能 >= size（死循环）

如果 `chunk_overlap >= chunk_size`：

```python
start += chunk_size - chunk_overlap   # += 0 或负数
```

会导致 `start` 不前进，`while` 死循环。

所以必须校验，并且：

> 校验要放在函数最前面，参数不合法立刻报错，不要先初始化变量再判断。

```python
if chunk_overlap >= chunk_size:
    raise ValueError("chunk_overlap must be smaller than chunk_size")
```

原则：**先校验，再干活。**

---

## 9. 批量切分 chunk_documents

```python
def chunk_documents(
    documents: list[RawDocument],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[DocumentChunk]:
    all_chunks: list[DocumentChunk] = []

    for document in documents:
        chunks = chunk_document(
            document,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        all_chunks.extend(chunks)

    return all_chunks
```

---

## 10. append vs extend（重要）

### append

```python
all_chunks.append(chunks)   # chunks 是 [c1, c2]
```

结果：

```python
[[c1, c2]]   # 列表里套列表
```

### extend

```python
all_chunks.extend(chunks)
```

结果：

```python
[c1, c2]   # 把子列表摊平放进去
```

合并多篇文档的 chunk 时要用 `extend`。

---

## 11. 今日踩坑：`<+` 运算符

错误写法：

```python
if chunk_size <+ chunk_overlap:
    raise ValueError(...)
```

`<+` 不是一个运算符。Python 会解析成：

```python
chunk_size < (+chunk_overlap)
```

也就是 `+` 被当成正号，等价于：

```python
chunk_size < chunk_overlap
```

两个问题：

1. **判断方向反了**：本意是 overlap 不能大于等于 size
2. **漏掉等于的情况**：`chunk_size == chunk_overlap` 时仍会死循环

正确写法：

```python
if chunk_overlap >= chunk_size:
    raise ValueError("chunk_overlap must be smaller than chunk_size")
```

教训：

> `<=`、`>=` 这种组合运算符不要手滑写成 `<+`、`=>`，Python 不会报语法错误，但语义完全不同，更难查。

---

## 12. 验证结果

测试命令（用更小的参数让短文档也能切出多个 chunk）：

```bash
uv run python -c "from pathlib import Path; from app.services.document_loader import load_documents_from_directory; from app.services.chunk_service import chunk_documents; docs = load_documents_from_directory(Path('knowledge_base/raw')); chunks = chunk_documents(docs, chunk_size=100, chunk_overlap=20); print(len(chunks)); print(chunks[0].metadata); print(chunks[0].content)"
```

实际输出：

```text
117
{'source': 'fastapi_notes.md', 'file_path': 'knowledge_base\\raw\\fastapi_notes.md', 'chunk_index': '0'}
FastAPI 是一个用于构建 API 的现代、快速（高性能）的 Python Web 框架...
```

说明：

- 切块成功，共 117 个 chunk（测试参数 `chunk_size=100`）
- metadata 三个字段齐全
- `chunk_index` 是字符串，类型正确
- content 是完整正常文本

---

## 13. 待办观察点（暂不处理）

`file_path` 当前是 Windows 反斜杠路径：

```text
knowledge_base\raw\fastapi_notes.md
```

如果以后要把该路径返回给前端或写入 JSON 给其他系统，反斜杠可能需要统一成正斜杠（`as_posix()` 或 `replace("\\", "/")`）。当前阶段不影响，先记录。

---

## 14. Day 3 验收清单

- [x] 在 `schemas/chunk.py` 定义 `DocumentChunk`（以及统一 `RawDocument`）
- [x] 实现 `split_text`，支持 chunk_size / chunk_overlap
- [x] 校验 overlap 不能 >= size，防止死循环
- [x] 实现 `chunk_document`，metadata 继承 + chunk_index
- [x] 实现 `chunk_documents`，用 extend 合并
- [x] 修复 `<+` 运算符错误
- [x] 测试切块输出正确

---

## 15. 当前 chunk 策略的局限（面试加分点）

当前用的是“固定字符长度切分”，优点是简单、好理解、能跑通。

但它的局限是：

- 不感知句子边界
- 不感知 Markdown 标题、段落、代码块结构
- 不按 token 计数（不同模型 token 切分不同）

更成熟的切分策略：

- 按段落 / 句子切
- 按 Markdown 标题层级切（结构感知）
- 按 token 切（贴合模型上下文窗口）
- 递归字符切分（RecursiveCharacterTextSplitter）

当前阶段先用最简单方案跑通链路，后续在 Week 3 评测时再决定是否升级。

---

## 16. 面试可讲点

> 在 RAG 建库阶段，我实现了基础的文档切块模块。系统会把每篇原始文档切成多个 `DocumentChunk`，每个 chunk 保留正文和 metadata。metadata 继承原始文档的 source、file_path，并额外增加 chunk_index，方便后续检索结果定位来源。
>
> 初版采用固定字符长度切分，并加入 chunk_overlap，避免句子或上下文关系被切断。同时对 chunk_overlap 做了校验，防止 overlap 大于等于 chunk_size 导致死循环。
>
> 我把数据模型放在 schema 层、切块逻辑放在 service 层，保持分层清晰。后续可以把切分策略升级为基于 Markdown 标题或 token 的更精细方案。

---

## 17. 当前 RAG 建库进度

```text
✅ Day 2：文档读取 → RawDocument
✅ Day 3：切块     → DocumentChunk
⬜ Day 4：Embedding → 向量
⬜ Day 5：向量库   → 检索
⬜ Day 6：拼 Prompt → LLM 回答
```

---

## 18. 下一步：Week 2 Day 4

Day 4 主题：

> 接入火山引擎 Embedding，把 chunk 文本转成向量。

计划：

```text
DocumentChunk.content
  ↓
EmbeddingService（调火山引擎 Ark API）
  ↓
list[list[float]] 向量
```

要点预告：

- 用 `httpx` 直接调火山引擎 Embedding 接口
- API Key 从 `.env` 读取（pydantic-settings）
- 关注返回结构里 embedding 数组的解析
- 注意批量请求和单条请求的差异
