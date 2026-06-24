# Week 1 · Day 5 Q&A：流式响应学习过程中的真实问题

**日期**：2026-06-18 ~ 2026-06-24
**主题**：记录学习流式响应时的疑问、卡点和踩过的坑

---

## Q1：`yield` 和 `yield from` 的区别

### 问题描述

在写 `stream_chat_answer` 时，我一开始写成：

```python
def stream_chat_answer(message: str) -> Iterator[str]:
    chain = CHAT_PROMPT | llm | StrOutputParser()
    yield chain.stream({"user_message": message})  # 我写的
```

结果调用方收到的不是逐段文本，而是一个 `<generator>` 对象。

### 原因

`yield x` 只会 yield **一次**，把 `x` 这个东西吐出去。
`chain.stream(...)` 返回的是一个**迭代器对象**，用 `yield` 吐出去，调用方拿到的就是那个迭代器本身，不会自动展开。

### 正确写法

```python
def stream_chat_answer(message: str) -> Iterator[str]:
    chain = CHAT_PROMPT | llm | StrOutputParser()
    yield from chain.stream({"user_message": message})  # 正确
```

`yield from iterable` 会把可迭代对象**逐项透传**给外层调用者，等价于：

```python
for item in iterable:
    yield item
```

但更简洁，且能正确转发 `.send()` / `.throw()` / `.close()`。

### 记忆点

```python
yield x        # 吐一个东西出去（一次）
yield from x   # 把 x 里的每个东西逐个吐出去（N 次）
```

---

## Q2：PowerShell 里 curl 的引号陷阱

### 问题描述

在 PowerShell 里用 curl 测试流式接口：

```powershell
curl.exe -N -X POST 'http://127.0.0.1:8000/chat/stream' -H 'Content-Type: application/json' -d '{"message": "用50字解释什么是RAG"}'
```

结果报错：

```json
{"detail":[{"type":"json_invalid","loc":["body",1],"msg":"JSON decode error"...}]}
```

### 原因

PowerShell 对引号的处理跟 Linux bash 不一样：
- 单引号 `'...'` 在 PowerShell 里是**字面量**，不会解析里面的内容
- curl.exe 收到的是**带单引号的字符串**，而不是 JSON 对象

### 解决方案

在 PowerShell 里，用 `--%` 告诉 PowerShell "后面的内容别动，原样传给 curl.exe"：

```powershell
curl.exe --% -N -X POST "http://127.0.0.1:8000/chat/stream" -H "Content-Type: application/json" -d "{\"message\": \"用50字解释什么是RAG\"}"
```

或者用 Git Bash（如果装了 Git），引号处理跟 Linux 一样：

```bash
curl -N -X POST 'http://127.0.0.1:8000/chat/stream' -H 'Content-Type: application/json' -d '{"message": "用50字解释什么是RAG"}'
```

---

## Q3：为什么流式路由不能加 `response_model`

### 问题描述

其他两个路由都写了 `response_model=ChatResponse`，但流式路由没写。为什么不加？

### 原因

`response_model` 用于：
1. FastAPI 校验响应数据
2. 在 Swagger 上展示响应结构
3. 自动序列化成 JSON

但流式响应是**原始字节流**，不是"一个 JSON 对象"。内容是：

```text
data: R
data: AG
data: （
...
data: [DONE]
```

没有固定的 schema 可校验，所以不能加 `response_model`。

Swagger 上会展示成 `text/event-stream`，调用方看到的是原始 SSE 流。

---

## Q4：`if chunk:` 判断是干嘛的

### 问题描述

路由层代码里有一行：

```python
for chunk in stream_chat_answer(request.message):
    if chunk:
        yield _sse_format(chunk)
```

为什么要判断 `if chunk:`？

### 原因

`chain.stream()` 偶尔会 yield **空字符串**（`""`）。

发空 SSE event 是无意义噪声：

```text
data:

```

过滤掉可以减少不必要的网络传输和前端处理。

---

## Q5：异常为什么放在 generator 内部

### 问题描述

```python
def event_generator():
    try:
        for chunk in stream_chat_answer(...):
            ...
    except Exception:
        logger.exception("...")
        yield _sse_format("[ERROR] LLM 调用失败")
        yield "data: [DONE]\n\n"
```

为什么不直接在 `chat_stream` 函数里 try/except？

### 原因

```python
@router.post("/stream")
def chat_stream(request: ChatRequest):
    ...
    return StreamingResponse(event_generator(), ...)
```

当 `return StreamingResponse(...)` 执行时，FastAPI 已经发了 **200 OK** 响应头。

如果之后 `event_generator` 抛异常：
- HTTP 状态码已经回不去 502 了
- 只能在流里发一条 `[ERROR]` event，让前端处理

所以异常必须在 generator 内部捕获，yield error event + DONE，然后优雅结束。

---

## Q6：为什么 chain 末尾要保留 `StrOutputParser`

### 问题描述

普通 chain 和流式 chain 都写了 `| StrOutputParser()`，这个 parser 在流式场景里起什么作用？

### 没有 StrOutputParser 时

```python
chain = CHAT_PROMPT | llm  # 没有 parser
for chunk in chain.stream({"user_message": "..."}):
    print(type(chunk))  # <class 'langchain_core.messages.ai.AIMessageChunk'>
```

每次 yield 的是 `AIMessageChunk` 对象，调用方需要 `.content` 提取字符串。

### 加了 StrOutputParser 后

```python
chain = CHAT_PROMPT | llm | StrOutputParser()
for chunk in chain.stream({"user_message": "..."}):
    print(type(chunk))  # <class 'str'>
```

每次 yield 的直接是 `str`，省掉调用方提取的步骤。

---

## 我犯过的错

1. **写成 `yield chain.stream(...)` 而不是 `yield from chain.stream(...)`**
   - 后果：只 yield 一次，吐出迭代器对象本身，不是逐段文本
   - 修复：改成 `yield from`

2. **路由路径写成 `"/chat/stream"`**
   - 后果：跟 `prefix="/chat"` 拼成 `/chat/chat/stream`
   - 修复：改成 `"/stream"`

3. **参数类型写成 `ChatResponse` 而不是 `ChatRequest`**
   - 后果：`request.message` AttributeError
   - 修复：改成 `ChatRequest`

4. **`StreamingResponse` 缩进错位，跑进了 `event_generator` 内部**
   - 后果：`chat_stream` 没有返回值，FastAPI 拿到 `None`
   - 修复：整段往左退 4 个空格，和 `def event_generator():` 同级

5. **PowerShell curl 引号问题**
   - 后果：JSON 解析错误
   - 修复：用 `curl.exe --% ...` 或 Git Bash
