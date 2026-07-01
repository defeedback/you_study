# Week 2 · Day 2：文档读取与清洗

**日期**：2026-06-29  
**对应阶段**：2 个月路线 · 第 2 周 Day 2  
**主题**：把本地 Markdown / TXT 文档读取成统一的 `RawDocument` 结构

---

## 0. 一句话总结

> RAG 的第一步不是向量库，而是先把原始文档稳定、干净、带来源信息地读进系统。

今天完成的是 RAG 建库阶段的第一步：

```text
原始 .md / .txt 文件
  ↓
读取文件
  ↓
基础清洗
  ↓
转换成 RawDocument(content + metadata)
```

---

## 1. 为什么文档读取和清洗很重要

RAG 后面的效果高度依赖输入文档质量。

如果文档读取阶段就有问题，例如：

- 文本为空
- 中文乱码
- 空行混乱
- 来源信息丢失
- 不支持的文件类型被错误读取

那么后续即使 Embedding、向量库和 Prompt 写得很好，问答效果也会受到影响。

所以 RAG 的第一块砖是：

> 把原始文档变成结构稳定的内部数据对象。

---

## 2. Day 2 的目标

支持读取目录：

```text
knowledge_base/raw/
```

其中先只支持两类文件：

```text
.md
.txt
```

读取后统一转换成：

```python
RawDocument(
    content="文档正文",
    metadata={
        "source": "fastapi_notes.md",
        "file_path": "knowledge_base/raw/fastapi_notes.md",
    },
)
```

---

## 3. `content` 和 `metadata` 的作用

| 字段 | 作用 |
|---|---|
| `content` | 文档正文，后续用于 chunking、Embedding 和 RAG 上下文 |
| `metadata` | 文档来源信息，后续用于引用来源、排查问题和结果展示 |

不要只返回 `list[str]`。

原因是：

```text
后续 RAG 回答需要告诉用户答案来自哪个文件、哪个片段。
```

如果 Day 2 不保留 metadata，后面做引用来源时会很麻烦。

---

## 4. 推荐数据结构：RawDocument

使用 Pydantic 定义一个简单模型：

```python
from pydantic import BaseModel


class RawDocument(BaseModel):
    content: str
    metadata: dict[str, str]
```

含义：

```text
RawDocument = 一篇被读取进来的原始文档。
```

后续 Day 3 切块后，一篇 `RawDocument` 会变成多个 `DocumentChunk`。

---

## 5. 支持的文件类型

可以定义：

```python
SUPPORTED_SUFFIXES = {".md", ".txt"}
```

读取目录时只处理这两类文件。

这样可以避免误读：

- `.png`
- `.pdf`
- `.docx`
- `.pyc`
- 其他临时文件

Day 2 不处理 PDF，因为 PDF 会引入额外复杂度：

- 页眉页脚
- 分页
- 表格错乱
- 换行异常
- 解析库选择

当前阶段先聚焦最小 RAG 链路。

---

## 6. 文本清洗规则

Day 2 只做基础清洗，不做激进清洗。

建议规则：

1. 统一换行符
2. 去掉首尾空白
3. 合并过多空行

示例：

```python
def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.strip()

    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    return text
```

---

## 7. 为什么不要过度清洗 Markdown

Markdown 中的标题、列表和代码块本身有语义。

例如：

```md
# FastAPI 笔记

- 路由
- 中间件
- 统一异常处理
```

不要清洗成：

```text
FastAPI 笔记 路由 中间件 统一异常处理
```

因为这会破坏文档结构。

RAG 初期清洗原则：

> 只清理明显噪音，不破坏原始语义结构。

---

## 8. 读取单个文件

核心逻辑：

```python
from pathlib import Path


def load_text_file(file_path: Path) -> RawDocument:
    text = file_path.read_text(encoding="utf-8")
    cleaned_text = clean_text(text)

    return RawDocument(
        content=cleaned_text,
        metadata={
            "source": file_path.name,
            "file_path": str(file_path),
        },
    )
```

关键点：

| 代码 | 作用 |
|---|---|
| `read_text(encoding="utf-8")` | 避免中文乱码 |
| `clean_text(text)` | 做基础清洗 |
| `file_path.name` | 获取文件名，例如 `fastapi_notes.md` |
| `str(file_path)` | 把 Path 对象转成字符串路径 |

---

## 9. 批量读取目录

核心逻辑：

```python
def load_documents_from_directory(directory: Path) -> list[RawDocument]:
    documents: list[RawDocument] = []

    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue

        document = load_text_file(file_path)
        documents.append(document)

    return documents
```

---

## 10. `rglob("*")` 的作用

```python
directory.rglob("*")
```

表示递归扫描目录下所有路径。

例如：

```text
knowledge_base/raw/
  fastapi_notes.md
  langchain_notes.md
  subdir/
    rag_notes.txt
```

也可以扫描到 `subdir/rag_notes.txt`。

---

## 11. 为什么要判断 `is_file()`

因为 `rglob("*")` 扫到的不一定都是文件，也可能是目录。

所以需要：

```python
if not file_path.is_file():
    continue
```

意思是：

```text
如果不是文件，就跳过。
```

---

## 12. 为什么要判断后缀

```python
if file_path.suffix.lower() not in SUPPORTED_SUFFIXES:
    continue
```

作用：

```text
只读取 .md 和 .txt，跳过其他类型。
```

`.lower()` 是为了兼容：

```text
README.MD
note.TXT
```

---

## 13. 今日踩坑：Pydantic BaseModel 初始化

今天遇到报错：

```text
TypeError: BaseModel.__init__() takes 1 positional argument but 2 were given
```

问题代码：

```python
return RawDocument(
    cleaned_text,
    metadata={
        "source": file_path.name,
        "file_path": file_path,
    },
)
```

错误原因：

> Pydantic 的 `BaseModel` 初始化时，字段应该使用关键字参数，不能把 `cleaned_text` 当作位置参数传入。

正确写法：

```python
return RawDocument(
    content=cleaned_text,
    metadata={
        "source": file_path.name,
        "file_path": str(file_path),
    },
)
```

重点：

```python
content=cleaned_text
```

而不是：

```python
RawDocument(cleaned_text, ...)
```

---

## 14. 今日踩坑：metadata 类型

模型定义：

```python
metadata: dict[str, str]
```

说明 metadata 的 key 和 value 都应该是字符串。

所以这里不要直接放 `Path` 对象：

```python
"file_path": file_path
```

应该写成：

```python
"file_path": str(file_path)
```

---

## 15. 今日踩坑：空行清洗不要太狠

不推荐：

```python
while "\n\n\n" in text:
    text = text.replace("\n\n\n", "\n")
```

因为它会把多个空行压成单个换行，可能破坏 Markdown 段落。

推荐：

```python
while "\n\n\n" in text:
    text = text.replace("\n\n\n", "\n\n")
```

含义：

```text
多个连续空行 → 最多保留一个空行。
```

这样能保留段落间隔。

---

## 16. 最小测试命令

可以在项目目录下执行：

```bash
uv run python -c "from pathlib import Path; from app.services.document_loader import load_documents_from_directory; docs = load_documents_from_directory(Path('knowledge_base/raw')); print(len(docs)); print(docs[0].metadata); print(docs[0].content[:100])"
```

期望输出类似：

```text
3
{'source': 'fastapi_notes.md', 'file_path': 'knowledge_base/raw/fastapi_notes.md'}
# FastAPI 笔记
FastAPI 是一个 Python Web 框架...
```

也可以进一步检查：

```python
for doc in docs:
    print(doc.metadata["source"])
    print(len(doc.content))
```

确认：

1. 每篇文档都被读取；
2. 文档内容长度不是 0；
3. metadata 里有来源信息。

---

## 17. Day 2 验收清单

- [x] 创建 `knowledge_base/raw/` 测试文档目录
- [x] 准备 Markdown / TXT 测试文档
- [x] 创建 `app/services/document_loader.py`
- [x] 定义 `RawDocument`
- [x] 实现 `clean_text`
- [x] 实现 `load_text_file`
- [x] 实现 `load_documents_from_directory`
- [x] 修复 Pydantic BaseModel 初始化错误
- [x] 能成功打印读取结果

---

## 18. 面试可讲点

> 在 RAG 建库阶段，我先实现了文档加载模块，支持读取本地 Markdown 和 TXT 文件。每篇文档会被转换成统一的 `RawDocument` 结构，包含正文 `content` 和来源 `metadata`。
>
> `metadata` 会保留文件名和文件路径，方便后续在 RAG 回答中返回引用来源。文本清洗阶段我只做了基础处理，比如统一换行符、去除首尾空白和合并多余空行，避免过度清洗破坏 Markdown 结构。
>
> 我还踩过一个 Pydantic 的坑：`BaseModel` 初始化字段时要用关键字参数，比如 `content=cleaned_text`，不能直接传位置参数。

---

## 19. 下一步：Week 2 Day 3

Day 3 主题：

> Chunking 文本切块。

下一步会把：

```text
RawDocument
```

切成：

```text
DocumentChunk
```

也就是：

```text
一篇长文档 → 多个小片段
```

每个 chunk 也要保留 metadata，例如：

```python
{
    "source": "fastapi_notes.md",
    "file_path": "knowledge_base/raw/fastapi_notes.md",
    "chunk_index": "0",
}
```

这样后续向量检索时，才能知道每个片段来自哪篇文档。
