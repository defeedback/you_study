# Week 1 · Day 6：中间件与统一异常处理

**日期**：2026-06-26
**对应阶段**：2 个月路线 · 第 1 周 Day 6
**主题**：让每个请求有日志、有 trace_id、错误响应统一格式

---

## 0. 一句话总结

> 中间件是"所有请求都要经过的门迎"，统一异常处理是"前台用标准模板回复客户错误"。
> 两者配合：请求进来 → 中间件打点 → 业务逻辑出错 → 异常处理器捕获 → 返回标准 JSON 错误响应。

---

## 1. 为什么 JD 里要考这个

| 问题 | 没有中间件/异常处理 | 有 |
|---|---|---|
| 日志 | 每个路由自己写，漏一个就少一份日志 | 全局统一，所有请求自动记录 |
| 错误响应 | 有的返回 `{"detail": "xxx"}`，有的返回 `{"error": "xxx"}` | 统一格式：`{code, message, trace_id}` |
| 排查问题 | 用户说"刚才报错了"，你不知道是哪次请求 | trace_id 贯穿日志和响应，秒定位 |
| 代码重复 | 20 个路由 × 10 行 try-except | 1 个处理器搞定 |

JD 关键词：**middleware、exception handling、trace_id、observability**。

---

## 2. 中间件原理

### 2.1 生活类比

餐厅门迎：

```text
客人进店 → 门迎打招呼 → 点菜 → 后厨做菜 → 上菜 → 门迎送客 → 客人离店
           ↑                                                          ↑
           └───────────── 这两步就是"中间件" ─────────────────────────┘
```

- 门迎不负责做菜，但每个客人进来和离开都要经过
- 门迎可以记录：几点来了多少人、呆了多久

### 2.2 在 FastAPI 里

```text
请求 → 中间件(前) → 路由处理 → 中间件(后) → 响应
        ↓                          ↓
      记录开始时间              计算耗时、打印日志
```

### 2.3 固定写法

```python
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # 请求进来时
    start_time = time.time()

    # 调用下一个处理器（路由）
    response = await call_next(request)

    # 响应返回时
    duration = time.time() - start_time
    print(f"耗时: {duration:.2f}s")

    return response
```

关键点：
- `@app.middleware("http")` 是固定写法，所有 HTTP 请求都会经过
- `call_next(request)` 调用下一个处理器，**必须传 request 参数**

---

## 3. 统一异常处理原理

### 3.1 问题：每个路由自己处理错误

```python
@router.post("/chat")
def chat(request: ChatRequest):
    try:
        answer = generate_chat_answer(request.message)
    except Exception as e:
        logger.exception("LLM 调用失败")
        raise HTTPException(status_code=502, detail="LLM 调用失败")
    return ChatResponse(answer=answer)
```

问题：
- 20 个接口要写 20 遍 try-except
- 错误响应格式可能不一致
- 没有 trace_id，排查困难

### 3.2 解决：全局异常处理器

```text
路由代码里直接抛异常
        ↓
全局异常处理器捕获
        ↓
统一转成标准 JSON 响应
```

类比：每个部门遇到问题，扔给前台，前台用统一模板回复客户。

---

## 4. 实现步骤

### 4.1 定义业务异常类

```python
# app/core/exceptions.py
class AppException(Exception):
    """业务异常基类"""
    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        self.message = message
        self.status_code = status_code
```

### 4.2 实现日志中间件

```python
# app/core/middleware.py
import time
import uuid
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    # 1. 生成 trace_id
    trace_id = uuid.uuid4().hex[:8]
    request.state.trace_id = trace_id

    # 2. 记录请求开始
    logger.info("[%s] %s %s - 请求开始", trace_id, request.method, request.url.path)
    start_time = time.time()

    # 3. 调用下一个处理器
    response = await call_next(request)

    # 4. 记录请求结束
    duration = (time.time() - start_time) * 1000
    logger.info("[%s] 状态码=%d 耗时=%.2fms", trace_id, response.status_code, duration)

    # 5. 把 trace_id 放到响应头里
    response.headers["X-Trace-Id"] = trace_id

    return response
```

### 4.3 注册中间件和异常处理器

```python
# app/main.py
from app.core.exceptions import AppException
from app.core.middleware import logging_middleware

# 注册中间件
app.middleware("http")(logging_middleware)

# 注册异常处理器
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    trace_id = getattr(request.state, "trace_id", "unknown")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "trace_id": trace_id
        }
    )
```

### 4.4 服务层抛业务异常

```python
# app/services/llm_service.py
from app.core.exceptions import AppException

def generate_chat_answer(message: str) -> str:
    try:
        llm = get_llm()
        chain = CHAT_PROMPT | llm | StrOutputParser()
        return chain.invoke({"user_message": message})
    except Exception as e:
        logger.exception("LLM 调用失败")
        raise AppException(
            code="LLM_ERROR",
            message="LLM 调用失败，请稍后重试",
            status_code=502
        ) from e
```

### 4.5 路由层简化

```python
# app/api/chat.py
@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    logger.info("收到聊天请求: %s", request.message[:80])
    answer = generate_chat_answer(request.message)  # 出问题自动抛 AppException
    return ChatResponse(answer=answer)
```

---

## 5. 完整流程图

```text
请求进来
   ↓
┌────────────────────────┐
│ 中间件                  │
│ - 生成 trace_id         │
│ - 记录开始时间          │
│ - trace_id 存到         │
│   request.state         │
└────────────────────────┘
   ↓
┌────────────────────────┐
│ 路由处理                │
│ - 业务逻辑              │
│ - 出问题抛 AppException │
└────────────────────────┘
   ↓ (如果有异常)
┌────────────────────────┐
│ 全局异常处理器          │
│ - 捕获 AppException     │
│ - 生成标准错误响应      │
│ - 带上 trace_id         │
└────────────────────────┘
   ↓
┌────────────────────────┐
│ 中间件（响应阶段）       │
│ - 计算耗时              │
│ - 打印请求日志          │
│ - 日志里带 trace_id     │
│ - 响应头加 X-Trace-Id   │
└────────────────────────┘
   ↓
响应返回给客户端
```

---

## 6. 测试验证

```bash
# 正常请求
curl http://localhost:8000/chat -X POST -H "Content-Type: application/json" -d '{"message":"你好"}'

# 触发异常（比如 LLM API key 无效）
curl http://localhost:8000/chat -X POST -H "Content-Type: application/json" -d '{"message":"测试错误"}'
```

正常响应：
```json
{"answer": "你好！有什么可以帮助你的吗？"}
```

错误响应：
```json
{
  "code": "LLM_ERROR",
  "message": "LLM 调用失败，请稍后重试",
  "trace_id": "abc12345"
}
```

日志输出：
```text
[abc12345] POST /chat - 请求开始
[abc12345] 状态码=502 耗时=1234.56ms
```

---

## 7. 踩过的坑

| 问题 | 原因 | 解决 |
|---|---|---|
| `call_next()` 报错 | 忘了传 `request` 参数 | `call_next(request)` |
| `logger.infor` 报错 | 拼写错误 | `logger.info` |
| `self.status_code = self.status_code` | 自己赋值给自己 | `self.status_code = status_code` |

---

## 7.1 易错点：中间件执行顺序

多个中间件的执行顺序是**后注册先执行**（像洋葱一样包裹）：

```python
@app.middleware("http")
async def middleware_A(request, call_next):
    print("A 进")
    response = await call_next(request)
    print("A 出")
    return response

@app.middleware("http")
async def middleware_B(request, call_next):
    print("B 进")
    response = await call_next(request)
    print("B 出")
    return response
```

请求流程：
```text
请求 → B 进 → A 进 → 路由 → A 出 → B 出 → 响应
```

---

## 7.2 易错点：为什么用 `request.state`

存储 trace_id 的几种方式对比：

| 方式 | 问题 |
|---|---|
| 全局变量 | 多请求并发时会互相覆盖，trace_id 就乱了 |
| 传参 | 要一路传到底（中间件 → 路由 → service），太麻烦 |
| `request.state` | ✅ 天然绑定到当前请求对象，随请求生灭 |

```python
# 中间件里存
request.state.trace_id = trace_id

# 异常处理器里取
trace_id = getattr(request.state, "trace_id", "unknown")
```

---

## 7.3 易错点：继承异常类的正确写法

错误写法：

```python
class RateLimitError(AppException):
    def __init__(self):
        super().__init__()  # ❌ 没传参数
        self.code = 429      # ❌ 应该传给父类，不是自己赋值
```

正确写法：

```python
class RateLimitError(AppException):
    def __init__(self, message: str = "请求过于频繁"):
        super().__init__(
            code="RATE_LIMIT_ERROR",
            message=message,
            status_code=429
        )
```

---

## 8. 文件结构

```text
app/
├── core/
│   ├── config.py          # 配置
│   ├── logging.py         # 日志配置
│   ├── exceptions.py      # 业务异常类 ← 新增
│   └── middleware.py      # 日志中间件 ← 新增
├── api/
│   └── chat.py            # 路由（简化后）
├── services/
│   └── llm_service.py     # 服务层（抛异常）
└── main.py                # 注册中间件和异常处理器
```

---

## 9. 验收清单

- [x] 理解中间件原理和作用
- [x] 理解统一异常处理原理和作用
- [x] 创建 `AppException` 业务异常类
- [x] 实现日志中间件 + trace_id
- [x] 在 `main.py` 注册中间件和异常处理器
- [x] 改造 `llm_service.py` 抛出业务异常
- [x] 简化 `chat.py` 路由代码
- [x] 测试验证通过

---

## 10. 面试可讲点

> "我实现了统一的请求日志中间件和异常处理机制。
>
> 中间件层面，每个请求进来会生成一个 trace_id，存到 `request.state` 里，记录请求开始和结束的耗时，并把 trace_id 放到响应头 `X-Trace-Id` 里。
>
> 异常处理层面，我定义了 `AppException` 业务异常类，在服务层捕获底层异常后抛出业务异常，由全局异常处理器统一转成标准 JSON 格式 `{code, message, trace_id}`。
>
> 这样做的好处是：路由层不用写 try-except，错误响应格式统一，排查问题可以通过 trace_id 快速定位。
>
> 我踩过一个坑：中间件的 `call_next()` 必须传 `request` 参数，否则会报错。"

---

## 11. 可继续完善

1. **扩展异常类型**：预定义 `LLMError`、`RateLimitError` 等子类
2. **中间件增强**：记录请求体、慢请求告警、请求来源 IP
3. **结构化日志**：JSON 格式，方便 ELK / Grafana Loki 采集
4. **请求体日志**：注意敏感信息过滤

---

## 12. 下一步：Day 7

Week 1 工程化收尾完成。接下来：

- Week 2：RAG 知识库问答
- 引入向量数据库、文档切分、Embedding、检索
