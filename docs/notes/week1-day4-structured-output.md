# Week 1 · Day 4：Structured Output 与分层重构

**日期**：2026-06-17 ~ 2026-06-18
**对应阶段**：2 个月路线 · 第 1 周 Day 4
**主题**：让模型直接返回 Pydantic 对象，并完成一次正确的依赖方向重构

> 📓 **配套问答笔记**：[qa/week1-day4-structured-output.md](qa/week1-day4-structured-output.md)
> 记录了我学习过程中的真实疑问、当时的卡点、犯过的错。

---

## 0. 一句话总结

> `with_structured_output(schema)` 让模型直接吐 Pydantic 对象，省掉 `json.loads` 和字段校验。
> Schema 由业务层声明，基础设施层（llm_client）保持通用——这是分层依赖的正确方向。

---

## 1. 为什么要做 Structured Output

JD 里"工具调用"、"知识库引用"、"Agent 多步规划"几乎都依赖**结构化输出**。

老办法的痛点：

```text
prompt → "请返回 JSON 格式..."
↓
模型有时返回纯 JSON，有时混入 ```json``` 代码块，有时编个新字段
↓
代码 try/except json.loads，再手动校验字段
↓
失败率 5~15%，生产无法接受
```

LangChain 1.x 的 `with_structured_output` 把这一切替你做完：模型 API 调用、JSON Schema 注入、解析、Pydantic 校验，**一次到位**。

> 🤔 当时我以为"结构化输出 = 在 prompt 里要求模型返回 JSON"，是真的动手才理解 → [Q2](qa/week1-day4-structured-output.md#q2-不要-chain-怎么处理-system-prompt)

---

## 2. 整体框架

普通 chain vs structured chain 的对比：

```text
┌─────────┐     ┌─────┐     ┌──────────────┐    ┌──────────────┐
│ Prompt  │────>│ LLM │────>│StrOutputParser│───>│   str        │   普通
└─────────┘     └─────┘     └──────────────┘    └──────────────┘

┌─────────┐     ┌──────────────────┐                  ┌──────────────┐
│ Prompt  │────>│ LLM (structured) │─────────────────>│Pydantic 对象 │   结构化
└─────────┘     └──────────────────┘                  └──────────────┘
```

关键差异：

| 维度 | 普通 chain | structured chain |
|---|---|---|
| LLM 输出 | `AIMessage` | Pydantic 对象 |
| Parser | `StrOutputParser()` | **不要 parser** |
| 调用方式 | `chain.invoke({...})` | `chain.invoke({...})` |
| 返回类型 | `str` | 你声明的 Pydantic schema |

> 🤔 我把 `StrOutputParser` 和 structured LLM 拼在一起，结果报 ValidationError → [Q1](qa/week1-day4-structured-output.md#q1-strooutputparser-报-validationerror-是什么意思)

---

## 3. with_structured_output 的工作原理

```python
llm = init_chat_model(...)
structured_llm = llm.with_structured_output(ChatResponseWithStructuring)
result = structured_llm.invoke("解释一下 RAG")
# result 直接是 ChatResponseWithStructuring(answer=..., confidence=..., follow_up_questions=...)
```

底层做了 3 件事：

1. **把 Pydantic schema 转成 JSON Schema**
2. **以 tool/function calling 的方式发给模型**（OpenAI 协议下用 `tools` 字段）
3. **解析模型返回的 JSON，填进 Pydantic 实例**

所以模型看到的不是"请返回 JSON"，而是"调用一个名为 ChatResponseWithStructuring 的工具，参数是这些"。这是为什么 structured output 比 prompt + json.loads 稳定得多。

---

## 4. Literal 的三层作用

```python
from typing import Literal

confidence: Literal["高", "中", "低"] = Field(description="回答置信度")
```

| 层 | 作用 | 时机 |
|---|---|---|
| 1 | IDE 类型检查 | 写代码时 Pylance 标红非法值 |
| 2 | Pydantic 运行时校验 | 实例化时抛 ValidationError |
| 3 | LLM 输出约束 | schema 转 JSON Schema 的 `enum` 字段，模型严格按枚举输出 |

**第 3 层最重要**——它决定模型不会返回 "high"、"较高"、"中等" 这种花式答案。

> 🤔 一开始我不知道 `Literal` 怎么导入 → [Q3](qa/week1-day4-structured-output.md#q3-literal-怎么导入)

---

## 5. Prompt 没消失，只是 chain 拼法变了

`with_structured_output` 不能让你跳过 system prompt。否则角色约束、不要编造、回答风格全丢了。

正确的 structured chain 写法：

```python
from app.prompts.chat import CHAT_PROMPT

llm = get_llm_with_structuring(ChatResponseWithStructuring)
chain = CHAT_PROMPT | llm        # ✅ 没有 StrOutputParser
return chain.invoke({"user_message": message})
```

记忆点：

```text
普通 chain:        prompt | llm | StrOutputParser()
structured chain:  prompt | llm
```

> 🤔 我当时以为"不要 chain 就等于不要 prompt" → [Q2](qa/week1-day4-structured-output.md#q2-不要-chain-怎么处理-system-prompt)

---

## 6. 分层重构：基础设施层 vs 业务层

Day 4 不只是用了一个新 API，更重要的是**做了一次正确的依赖方向调整**。

### 错误做法（我最初写的）

```python
# llm_client.py
from app.schemas.chat import ChatResponseWithStructuring   # ❌ 反向依赖

@lru_cache
def get_llm_with_structuring() -> BaseChatModel:
    model = init_chat_model(...)                           # ❌ 重复初始化
    return model.with_structured_output(ChatResponseWithStructuring)  # ❌ 写死业务
```

问题：

1. 通用工具反过来依赖业务 schema
2. 重复初始化 LLM 实例（已经有 `get_llm()` 单例）
3. 每加一个业务都要改 llm_client

### 正确做法

```python
# llm_client.py
def get_llm_with_structuring(schema: Type[BaseModel]) -> Runnable:
    return get_llm().with_structured_output(schema)
```

```python
# llm_service.py
def generate_chat_answer_with_structuring(message: str) -> ChatResponseWithStructuring:
    llm = get_llm_with_structuring(ChatResponseWithStructuring)
    chain = CHAT_PROMPT | llm
    return chain.invoke({"user_message": message})
```

依赖方向：

```text
api      ──>  services  ──>  llm_client (通用)
              ↓
          schemas（数据结构，被各层引用是 OK 的）
```

llm_client 不知道 schema 长什么样，业务层决定用哪个 schema——这就是 **依赖倒置**。

> 🤔 我犯过的所有 bug 清单 → [我犯过的错](qa/week1-day4-structured-output.md#我犯过的错)

---

## 7. 为什么 get_llm_with_structuring 不能用 @lru_cache

```python
def get_llm_with_structuring(schema: Type[BaseModel]) -> Runnable:  # ✅ 没装饰器
```

原因：`Type[BaseModel]` 不一定可哈希，`@lru_cache` 会抛 `TypeError`。

但**不需要担心性能**：

```text
get_llm()                     有 @lru_cache，整个应用只创建一次
.with_structured_output(...)  只是套个 Runnable 壳，几乎零开销
```

每次调用 `get_llm_with_structuring(...)` 等于白嫖了 `get_llm()` 的单例 + 套个轻量壳。

---

## 8. 验收清单

- [x] 新建 `ChatResponseWithStructuring` schema，含 `Literal` 字段
- [x] `get_llm_with_structuring(schema)` 复用 `get_llm()`
- [x] 业务层显式传入 schema，基础设施层不依赖 schemas
- [x] structured chain 不带 `StrOutputParser`
- [x] 新建 `/chat/with_structuring` 路由，函数名不与原 `/chat` 冲突
- [x] response_model 与返回类型一致
- [x] Swagger 测试通过，confidence 稳定输出"高/中/低"
- [x] 写笔记 + 配套 Q&A 文档

---

## 9. 面试可讲点

> "我用 LangChain 1.x 的 `with_structured_output` 实现了结构化输出，模型直接返回 Pydantic 对象，省掉了 `json.loads` 和字段校验。
>
> 字段用 `Literal` 约束枚举值，schema 转 JSON Schema 传给 LLM 时变成 `enum`，模型严格按枚举输出，避免了"高/high/较高"这种花式答案。
>
> 我把 `get_llm_with_structuring(schema)` 设计成接受任意 schema，让基础设施层（llm_client）保持通用，业务层（llm_service）决定具体 schema。这样 RAG 引用片段、Agent 工具调用都能复用同一个基础设施。"

---

## 10. 下一步：Day 5

**主题：Tool Calling（工具调用）**

让模型能调用本地 Python 函数（查时间、读文件、计算等），是 Agent 的"手"。

预期收获：

- 用 `@tool` 装饰器定义工具
- `llm.bind_tools([...])` 让模型知道有哪些工具
- 用 `create_agent` 自动循环"思考 → 调工具 → 再思考"
- 为 Week 2 的 RAG + Agent 完整闭环铺路
