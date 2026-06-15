# 第 1 周 Day 1-2：FastAPI + LangChain 1.x 项目骨架

> 学习日期：2026-06-11 至 2026-06-12
> 项目：[dev-knowledge-agent](../../dev-knowledge-agent/)
> 对应学习路线：[第 1 周 项目骨架 + LLM API + Prompt](../learning-plans/ai-agent-2-month-roadmap.md)

## 本次目标

搭建一个工程化的 FastAPI 后端骨架，集成 LangChain 1.x 调用大模型，跑通最小 `/chat` 接口。

## 已完成内容

### 1. 项目结构

```text
dev-knowledge-agent/
  .env                    真实密钥（不提交）
  .env.example            配置模板
  pyproject.toml          uv 管理的依赖
  app/
    main.py               FastAPI 入口
    api/
      chat.py             /chat 路由
    core/
      config.py           BaseSettings 配置
      logging.py          日志初始化
    schemas/
      chat.py             ChatRequest / ChatResponse
    services/
      llm_client.py       LLM 客户端单例
      llm_service.py      聊天业务逻辑
```

### 2. 依赖安装

```bash
uv add fastapi uvicorn python-dotenv pydantic-settings langchain langchain-openai
```

锁定版本：

- langchain 1.3.7
- langchain-core 1.4.6
- langchain-openai 1.3.0
- fastapi 0.136.3
- pydantic-settings 2.14.1

### 3. 跑通最小聊天接口

启动：

```bash
uv run uvicorn app.main:app --reload
```

访问：

- <http://127.0.0.1:8000/docs> Swagger
- <http://127.0.0.1:8000/redoc> ReDoc
- POST /chat 调用大模型成功返回

## 关键知识点

### 1. 工程化分层

| 层 | 职责 | 不该做 |
|---|---|---|
| `main.py` | 创建 app、注册路由、初始化日志 | 写业务逻辑 |
| `api/` | 接收请求、校验、调 service、返回响应 | 直接调 LangChain |
| `schemas/` | Pydantic 模型，定义请求 / 响应格式 | 写业务逻辑 |
| `services/` | 真正的业务逻辑（LLM 调用、RAG、Agent） | 处理 HTTP |
| `core/` | 配置、日志、全局基础设施 | 处理具体业务 |

### 2. 配置集中管理

使用 `pydantic-settings.BaseSettings` 自动从 `.env` 读取配置，比到处 `os.getenv` 强：

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    llm_temperature: float = 0.7

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

要点：

- 没有默认值的字段 = 启动时必须存在，缺失立即报错
- `@lru_cache` 让配置全局只读一次
- `.env` 不能提交，`.env.example` 提交作为模板

### 3. LLM 客户端单例

```python
from functools import lru_cache
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from app.core.config import get_settings

@lru_cache
def get_llm() -> BaseChatModel:
    settings = get_settings()
    return init_chat_model(
        model=settings.llm_model,
        model_provider="openai",
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=settings.llm_temperature,
    )
```

- 不要每次请求都新建 `ChatOpenAI`
- 返回类型用 `BaseChatModel` 抽象基类，方便后续换模型

### 4. LCEL 写法（LangChain 1.x 推荐）

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{user_message}"),
])
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"user_message": message})
```

- LangChain 1.x 已废弃 `LLMChain`，统一用 LCEL
- `StrOutputParser` 把 `AIMessage` 直接转成字符串，省去 `.content`

### 5. Swagger / ReDoc 注释

接口装饰器：

```python
@router.post(
    "",
    response_model=ChatResponse,
    summary="普通聊天接口",
    description="接收用户问题，调用大模型生成回答。",
)
```

Pydantic 字段：

```python
message: str = Field(
    description="用户输入的问题",
    examples=["请解释一下什么是 RAG"],
    min_length=1,
    max_length=2000,
)
```

要点：

- `summary` / `description` / `tags` 控制接口文档
- `Field(description=, examples=)` 控制字段文档
- `examples` 必须是**列表**

### 6. 日志配置

```python
logging.basicConfig(
    level=level,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
```

要点：

- LangChain 底层用 httpx，不静音会刷屏
- 各模块用 `logging.getLogger(__name__)`，按模块名归类日志

## 踩过的坑

### Bug 1：类型注解写错

```python
llm_temperature = float = 0.7   # ❌
llm_temperature: float = 0.7    # ✅
```

`=` 是赋值，`:` 才是类型注解。前者会让 pydantic-settings 不认这个字段。

### Bug 2：用 `format_messages` 构造模板

```python
ChatPromptTemplate.format_messages([...])    # ❌ 这是填变量的
ChatPromptTemplate.from_messages([...])      # ✅ 这是建模板的
```

记忆：

- `from_messages` 建模板（盖房子）
- `format_messages` 填变量（搬家具）

### Bug 3：response_model 写错对象

```python
response_model=ChatRequest    # ❌
response_model=ChatResponse   # ✅
```

写错会导致：LLM 已经返回内容，但 FastAPI 用错误的 schema 校验响应，报 `missing field 'message'`。

### Bug 4：绕过 get_settings 缓存

```python
settings = Settings()        # ❌ 每次新建
settings = get_settings()    # ✅ 全局单例
```

### Bug 5：字段名单复数混用

```python
messages: str = Field(...)   # ❌ 单条消息用复数
message: str = Field(...)    # ✅
```

后面做多轮对话时 `messages` 会和 LangChain 的概念冲突。

### Bug 6：examples 类型

```python
examples="字符串"        # ❌
examples=["字符串"]      # ✅ 必须是列表
```

## 仍然不理解 / 待深入的点

- LCEL 内部的 Runnable 体系是怎么实现 `|` 运算符的？
- `init_chat_model` 和 `ChatOpenAI` 的差异在哪些场景下会显现？
- middleware 在 LangChain 1.x 的 Agent 流程中具体怎么用？（第 4-5 周再看）
- 流式响应（SSE / streaming）怎么和 FastAPI 集成？（暂缓）

## 下一步（Day 3-4）

- [ ] Prompt 模板规范化：把 system prompt 拎到独立模块，便于后续做版本管理
- [ ] 给 `/chat` 接口加请求日志（user_id / latency / token_usage）
- [ ] 引入 structured output：让模型直接返回结构化结果，替代手写 JSON 解析
- [ ] 写第一份接口手测脚本（curl / httpx）
- [ ] Day 7：完成本周复盘，对照 [第 1 周验收标准](../learning-plans/ai-agent-2-month-roadmap.md)

## 面试可讲点

> 在 FastAPI + LangChain 1.x 项目中，我做了清晰的分层：路由层只负责接收请求和校验，业务逻辑放在 service 层，配置用 `BaseSettings` 集中管理并通过 `lru_cache` 实现单例。LLM 客户端通过 `init_chat_model` 创建并缓存，避免每次请求重建 HTTP 连接。Chain 编排使用 LangChain 1.x 推荐的 LCEL 写法（`prompt | llm | StrOutputParser`），不依赖已废弃的 `LLMChain` 和 `AgentExecutor`。
