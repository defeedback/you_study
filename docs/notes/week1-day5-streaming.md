# Week 1 · Day 5：流式响应（Streaming / SSE）

**日期**：2026-06-18 ~ 2026-06-24
**对应阶段**：2 个月路线 · 第 1 周 Day 5
**主题**：让 `/chat` 从"憋 5 秒一次性吐答案"变成"第 200ms 就有字往外蹦"

> 📓 **配套问答笔记**：[qa/week1-day5-streaming.md](qa/week1-day5-streaming.md)
> 记录了我学习过程中的真实疑问、当时的卡点、犯过的错。

---

## 0. 一句话总结

> `chain.stream()` 返回迭代器，`yield from` 透传给 FastAPI 的 `StreamingResponse`，最终以 `data: xxx\n\n` 的 SSE 格式逐 token 推给前端。
> 响应头加 `X-Accel-Buffering: no` 防止 Nginx 缓冲变成假流式。

---

## 1. 为什么 JD 里要考流式

打开 ChatGPT，回答是**一个字一个字**蹦出来的；如果它憋十几秒一次性甩给你一整段，你早就关页面了。

| 场景 | 没流式 | 有流式 |
|---|---|---|
| 1000 字回答 | 用户瞪屏幕 8 秒看到完整答案 | 第 200ms 就有第一个字 |
| 后端体感 | 一个请求占住 worker 8 秒 | 同样 8 秒，但前端 perceived latency 砍到 1/30 |
| 成本/取消 | 用户走了，token 还在烧 | 用户断连立即停 |

JD 关键词：**SSE、StreamingResponse、async generator、token-level streaming**。

---

## 2. 整体框架（三层）

```text
┌──────────┐    SSE   ┌────────────────┐   LCEL.stream   ┌─────┐
│  浏览器  │ <─────── │  /chat/stream  │ <────────────── │ LLM │
└──────────┘  text/   │ StreamingResp. │  yield 小段 str └─────┘
              event-  └────────────────┘
              stream
```

三个关键概念：

| 名词 | 角色 | 一句话 |
|---|---|---|
| `chain.stream(...)` | LangChain LCEL API | 不再返回 `str`，返回**迭代器**，每次给一小段 |
| `StreamingResponse` | FastAPI 响应类 | 把 Python 生成器挂到 HTTP body，不缓冲 |
| SSE (Server-Sent Events) | HTTP 子协议 | `data: xxx\n\n` 格式，浏览器原生 `EventSource` 支持 |

> 💡 **vs WebSocket**：SSE 单向（服务器→客户端），HTTP 协议，简单；WebSocket 双向，需要握手协议。聊天回答场景 SSE 完全够用。

---

## 3. LCEL `.stream()` vs `.invoke()`

### 对比表

| 维度 | `.invoke()` | `.stream()` |
|---|---|---|
| 返回类型 | 完整结果（`str` 或 Pydantic 对象） | **迭代器**，每次 yield 一个 chunk |
| 调用方处理 | 直接拿结果 | 用 `for chunk in chain.stream(...)` 逐段处理 |
| 底层 | 一次 API 调用，等模型返回全部 token | 仍是**一次** API 调用，但模型每生成一段就推过来 |
| 适用场景 | 批处理、后台任务 | 实时对话、ChatGPT 式体验 |

### chain 末尾为什么要保留 `StrOutputParser`

```python
chain = CHAT_PROMPT | llm | StrOutputParser()
yield from chain.stream({"user_message": message})
```

- **没 StrOutputParser**：每次 yield 一个 `AIMessageChunk` 对象，调用方拿到的是消息块，还得 `.content` 提取
- **加了 StrOutputParser**：每次 yield 是已经提取好的 `str`，直接拼接 / 转发

---

## 4. `yield from` vs `yield`（高频 bug）

### 错误写法

```python
def stream_chat_answer(message: str) -> Iterator[str]:
    chain = CHAT_PROMPT | llm | StrOutputParser()
    yield chain.stream({"user_message": message})  # ❌ 只 yield 一次
```

后果：调用方收到一个 `<generator>` 对象，然后就结束了，**不会逐段输出**。

### 正确写法

```python
def stream_chat_answer(message: str) -> Iterator[str]:
    chain = CHAT_PROMPT | llm | StrOutputParser()
    yield from chain.stream({"user_message": message})  # ✅ 逐项透传
```

### 一句话区分

| 写法 | 含义 | 调用方收到 |
|---|---|---|
| `yield x` | 把 `x` 这一个东西吐出去 | `x`（**一次**） |
| `yield from iterable` | 把可迭代对象**逐项透传** | iterable 里的每一项（**N 次**） |

> 🤔 我第一次就写成 `yield chain.stream(...)` → [Q1](qa/week1-day5-streaming.md#q1-yield-和-yield-from-的区别)

---

## 5. SSE 协议格式

SSE（Server-Sent Events）是 HTTP 的一个子协议，用于服务器向客户端单向推送事件流。

### 基本格式

```text
data: 第一行内容\n
data: 第二行内容\n
\n
```

规则：
- 每行内容前缀 `data: `
- 一条 event **以空行（`\n\n`）结束**
- 内容如果**自身带换行**（比如 markdown、代码块），每个换行后都要重新加 `data: ` 前缀

### 结束哨兵

OpenAI 协议惯例，流结束时发送：

```text
data: [DONE]\n\n
```

前端收到 `[DONE]` 就知道流结束，可以关闭连接、收尾 UI。

### Python 实现

```python
def _sse_format(text: str) -> str:
    """把一段文本包成一条 SSE event。"""
    safe = text.replace("\r\n", "\n").replace("\r", "\n")  # 统一换行符
    lines = safe.split("\n")
    payload = "\n".join(f"data: {line}" for line in lines)
    return payload + "\n\n"
```

---

## 6. FastAPI `StreamingResponse`

### 基本用法

```python
from fastapi.responses import StreamingResponse

@router.post("/stream")
def chat_stream(request: ChatRequest):
    def event_generator():
        for chunk in stream_chat_answer(request.message):
            if chunk:
                yield _sse_format(chunk)
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
```

### 关键细节

| 细节 | 说明 |
|---|---|
| **不能用 `response_model`** | 流式是原始字节流，没有"一个 JSON 对象"可校验 |
| **异常放在 generator 内部** | `StreamingResponse` 已经发了 200 OK，之后抛异常改不了状态码，只能在流里 yield error event |
| **`if chunk:` 过滤空串** | `chain.stream` 偶尔 yield 空字符串，发空 SSE event 是噪声 |

### 响应头的作用

```python
headers={
    "Cache-Control": "no-cache",      # 别缓存事件流
    "X-Accel-Buffering": "no",        # 告诉 Nginx 别 buffer
}
```

不加 `X-Accel-Buffering: no` 的话：
- 本地 dev 一切正常
- 一上 Nginx 反代就变成"假流式"——服务器在流，但 Nginx 攒一波再发，用户体验跟非流式一样

> 🤔 PowerShell curl 引号问题折腾了我半天 → [Q2](qa/week1-day5-streaming.md#q2-powershell-里-curl-的引号陷阱)

---

## 7. 完整代码实现

### service 层

```python
# app/services/llm_service.py
from typing import Iterator
from langchain_core.output_parsers import StrOutputParser
from app.services.llm_client import get_llm
from app.prompts.chat import CHAT_PROMPT

def stream_chat_answer(message: str) -> Iterator[str]:
    llm = get_llm()
    chain = CHAT_PROMPT | llm | StrOutputParser()
    yield from chain.stream({"user_message": message})
```

### 路由层

```python
# app/api/chat.py
from fastapi.responses import StreamingResponse
from app.services.llm_service import stream_chat_answer

def _sse_format(text: str) -> str:
    safe = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = safe.split("\n")
    payload = "\n".join(f"data: {line}" for line in lines)
    return payload + "\n\n"

@router.post("/stream", summary="流式聊天接口 (SSE)")
def chat_stream(request: ChatRequest):
    logger.info("收到流式聊天请求: %s", request.message[:80])

    def event_generator():
        try:
            for chunk in stream_chat_answer(request.message):
                if chunk:
                    yield _sse_format(chunk)
            yield "data: [DONE]\n\n"
        except Exception:
            logger.exception("LLM 流式调用失败")
            yield _sse_format("[ERROR] LLM 调用失败")
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

---

## 8. 验收清单

- [x] service 层新增 `stream_chat_answer`，使用 `chain.stream()` + `yield from`
- [x] 路由层新增 `/chat/stream`，使用 `StreamingResponse`
- [x] SSE 格式正确：每行 `data: xxx`，结束 `data: [DONE]`
- [x] 响应头包含 `Content-Type: text/event-stream`、`Cache-Control: no-cache`、`X-Accel-Buffering: no`
- [x] curl 测试通过，能看到逐段输出
- [x] 写笔记 + 配套 Q&A 文档

---

## 9. 面试可讲点

> "我用 LangChain LCEL 的 `chain.stream()` 实现了流式响应，每次 yield 一个 token 级别的 chunk。
>
> 底层是 FastAPI 的 `StreamingResponse`，把 Python 生成器挂到 HTTP body 上，配合 `text/event-stream` 的 SSE 协议，前端用 `EventSource` 或 `fetch` + `ReadableStream` 就能逐字渲染。
>
> 我踩过一个坑：`yield generator` 和 `yield from generator` 不一样，前者只 yield 一次（迭代器对象本身），后者才是逐项透传。
>
> 响应头我加了 `X-Accel-Buffering: no`，防止 Nginx 反代时缓冲变成假流式。这个在生产环境必须注意，本地 dev 看不出问题。"

---

## 10. 下一步：Day 6

**主题：日志 + 异常处理 + 中间件**

流式响应已经完成，Week 1 的核心功能（FastAPI 骨架 + LLM API + Prompt + Structured Output + Streaming）都跑通了。

接下来做工程化收尾：

- 结构化日志（JSON 格式，方便 ELK / Grafana Loki 采集）
- 统一异常处理（`HTTPException` 子类化、错误码规范）
- 请求日志中间件（记录每个请求的耗时、状态码、trace_id）
- 为 Week 2 的 RAG 铺路
