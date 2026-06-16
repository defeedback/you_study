# Week 1 · Day 3：Prompt 工程化与模板分层

**日期**：2026-06-15 ~ 2026-06-16
**对应阶段**：2 个月路线 · 第 1 周 Day 3
**主题**：把 Prompt 从 service 层拎出来，建立可版本化的模板体系

---

## 0. 一句话总结

> Service 写 "怎么做"，Prompts 写 "说什么"，Schemas 写 "格式什么"。三件事分开，项目才能长大。

完成后 [llm_service.py](../../dev-knowledge-agent/app/services/llm_service.py) 业务代码只剩 8 行。

---

## 1. 为什么要做 Prompt 工程化

JD 里反复出现的 "Prompt Engineering" 在企业里**不是指会写一句让模型听话**，而是指：

- Prompt 可独立修改、独立 review
- 有版本号，能 A/B 测试和回滚
- 不和业务代码耦合，产品/非技术同学也能审
- 多接口可复用同一套模板

如果 Prompt 散落在 service 里，后续做不了这些事。

---

## 2. Prompt 管理的四个等级

| Level | 形式 | 适用阶段 |
|---|---|---|
| L1 | 写在代码里 `SYSTEM_PROMPT = "..."` | 玩具 Demo |
| L2 | 拎到独立模块 `app/prompts/chat.py` | **当前阶段** |
| L3 | 配置文件 `prompts/chat.yaml` + 版本号 | 多 prompt 项目 |
| L4 | 数据库 / LangSmith / Langfuse | 团队协作、生产环境 |

> Day 3 目标是 L1 → L2，不要过度工程化跳到 L3。

---

## 3. 项目结构变化

### Day 3 之前

```text
app/
  services/
    llm_service.py   ← Prompt 字符串和业务逻辑混在一起
```

### Day 3 之后

```text
app/
  prompts/
    __init__.py
    chat.py          ← 只放 Prompt 模板和版本号
  services/
    llm_service.py   ← 只剩 LCEL 编排
  scripts/
    try_chat.py      ← 手测 Prompt 效果的临时脚本
```

为什么不放在 services 里？

```text
services/   动作（怎么调模型、怎么处理）
prompts/    内容（说什么话）
```

把"动作"和"内容"分离，prompt 才能独立版本化、独立评测、独立 review。

---

## 4. ChatPromptTemplate 三种写法

### 写法 A：tuple 列表（最常用）

```python
ChatPromptTemplate.from_messages([
    ("system", "你是一个助手"),
    ("human", "{user_message}"),
])
```

LangChain 会自动把 `("system", "...")` 识别成 `SystemMessage`，`("human", "...")` 识别成 `HumanMessage`。LangChain 1.x 文档主要写法。

### 写法 B：消息对象列表（显式）

```python
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate

ChatPromptTemplate.from_messages([
    SystemMessage(content="你是一个助手"),
    HumanMessagePromptTemplate.from_template("{user_message}"),
])
```

适合需要混入工具调用历史等复杂消息的场景。

### 写法 C：MessagesPlaceholder（多轮对话必用）

```python
from langchain_core.prompts import MessagesPlaceholder

ChatPromptTemplate.from_messages([
    ("system", "你是一个助手"),
    MessagesPlaceholder("history"),     # 占位"消息列表"
    ("human", "{user_message}"),
])
```

调用时必须传 `history` 字段（可以是空列表 `[]`，但不能不传）：

```python
chain.invoke({
    "user_message": "刚刚我问了什么？",
    "history": [
        ("human", "什么是 RAG？"),
        ("ai", "RAG 是检索增强生成..."),
    ],
})
```

> **第 4 周做会话记忆时一定会用到 MessagesPlaceholder**，今天先认识。本质就是把 history 从硬编码变成"从数据库/Redis 读出来"。

---

## 5. 模板变量的工作机制

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是 {role}，用 {language} 回答。"),
    ("human", "{user_message}"),
])
```

调用流程：

```text
1. invoke 传入 dict
2. 模板按 {key} 替换
3. 替换后的消息列表喂给 llm
4. llm 返回 AIMessage
5. StrOutputParser 提取 .content
```

### 黄金规则

> **prompt 模板里出现的所有 `{xxx}` 和 `MessagesPlaceholder("xxx")`，都必须在 `invoke({...})` 里传齐。少一个就报 KeyError。**

排查工具：

```python
print(prompt.input_variables)
# ['language', 'role', 'user_message']
```

---

## 6. 推荐的 prompts 模块结构

```python
"""聊天接口的 Prompt 模板"""
from langchain_core.prompts import ChatPromptTemplate

# 版本号：每次有意义的修改递增
CHAT_PROMPT_VERSION = "v1.0"

# System 部分：定义角色、能力边界、回答约束
SYSTEM_PROMPT = """\
你是一个面向开发者的技术学习助手。

回答要求：
1. 用中文回答
2. 技术术语保留英文
3. 回答简洁、准确、有结构
4. 不确定的内容明确说明"我不确定"，不要编造
"""

# 模板：组合 system + human
CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{user_message}"),
])
```

### 设计要点

1. **顶部声明版本号**：改 prompt 就改版本号，配合 git log 能溯源每次变更
2. **常量名 + Prompt 后缀**：`CHAT_PROMPT` / `CHAT_SYSTEM_PROMPT`，一眼能区分
3. **System 提示用三引号 + 编号清单**：模型对编号清单的指令遵循度更高
4. **三引号开头用 `"""\`**：去掉首行多余的 `\n`，prompt 字符更可控
5. **明确"不确定就承认"**：减少幻觉，是 RAG 时代最重要的 prompt 原则之一

---

## 7. Prompt 工程的 4 条原则

### 原则 1：System 描述"角色 + 能力 + 约束"

不要：

```text
你是一个 AI 助手。请回答用户问题。
```

要：

```text
你是【角色】。
你能做【能力 1】、【能力 2】。
你不能【边界 1】。
回答时遵循【格式 1】、【格式 2】。
```

### 原则 2：Human 模板里只放变量，不放指令

不推荐：

```text
("human", "请帮我用中文简洁地回答：{user_message}")
```

推荐：

```text
("human", "{user_message}")
```

回答约束应该放在 system，不要散落到 human，否则模型可能把约束当成用户问题的一部分。

### 原则 3：用 structured output 代替"返回 JSON"

不要在 prompt 里写"请返回 JSON 格式"，应该用 LangChain 1.x 的 `with_structured_output`（Day 4 学）。

### 原则 4：Few-shot 示例放 system 末尾或独立 messages

```python
ChatPromptTemplate.from_messages([
    ("system", CHAT_SYSTEM_PROMPT),
    ("human", "什么是 RAG？"),
    ("ai", "RAG 是检索增强生成..."),
    ("human", "{user_message}"),
])
```

模型看到"前面这样回答了 X，那对当前 Y 我也用同样风格"。

---

## 8. Service 层接入 Prompt 模块

最终 [llm_service.py](../../dev-knowledge-agent/app/services/llm_service.py) 只剩：

```python
from langchain_core.output_parsers import StrOutputParser
from app.services.llm_client import get_llm
from app.prompts.chat import CHAT_PROMPT


def generate_chat_answer(message: str) -> str:
    llm = get_llm()
    chain = CHAT_PROMPT | llm | StrOutputParser()
    return chain.invoke({"user_message": message})
```

8 行业务代码。修改 prompt 完全不需要碰 service，这就是分层的力量。

---

## 9. 踩过的坑

### 坑 1：直接把 .py 文件当脚本跑

```powershell
uv run .\app\prompts\chat.py        # ❌ 报 ModuleNotFoundError: No module named 'app'
```

正确做法：用 `-m` 模块语法

```powershell
uv run python -m app.prompts.chat   # ✅
```

> **包内文件用 `-m` 跑，不要用文件路径跑。** 用了 `from app.xxx import` 的文件，永远用 `-m`。

### 坑 2：PYTHONPATH 设错

```powershell
$env:PYTHONPATH = "app"   # ❌ Python 会去找 app/app/services/...
```

`PYTHONPATH` 应该指向**项目根**，让 `app` 这个包能被找到，而不是指向 `app` 自身。最稳妥的做法是不设 `PYTHONPATH`，直接 `-m`。

### 坑 3：chain.invoke 用关键字参数

```python
chain.invoke(user_message="你好")           # ❌
chain.invoke({"user_message": "你好"})      # ✅ 必须传 dict
```

LangChain 的 `Runnable.invoke()` 第一个参数是字典，不是 kwargs。

### 坑 4：MessagesPlaceholder 不传 history

模板里有 `MessagesPlaceholder("history")` 但 invoke 没传，报：

```text
KeyError: "Input to ChatPromptTemplate is missing variables {'history'}."
```

第一次没历史也要传空列表 `history=[]`，不能不传。

### 坑 5：import 后又用同名变量覆盖

```python
from app.prompts.chat import SYSTEM_PROMPT, CHAT_PROMPT   # 导入
SYSTEM_PROMPT = "你是一个面向开发者的技术学习助手..."        # 覆盖了
```

后果：改 prompts/chat.py 里的 SYSTEM_PROMPT 没用，被本地变量盖掉。  
原则：**service 层只 import 它真正用的（CHAT_PROMPT），不要 import 内部细节（SYSTEM_PROMPT）。**

### 坑 6：定义了 logger 却用 logging

```python
logger = logging.getLogger(__name__)
...
logging.info("xxx")    # ❌ 用了全局 logging
logger.info("xxx")     # ✅ 用模块 logger
```

后果：日志里 logger name 显示成 root 而不是 app.api.chat，排查问题时定位不准。

---

## 10. 验收清单

- [x] 新建 `app/prompts/__init__.py` 和 `app/prompts/chat.py`
- [x] Prompt 拎出 service，加版本号 `CHAT_PROMPT_VERSION`
- [x] Service 层用 `from app.prompts.chat import CHAT_PROMPT`
- [x] Service 业务代码精简到 ~8 行
- [x] 用 `scripts/try_chat.py` 验证 3 种模板写法
- [x] 理解 `prompt.input_variables` 和 `MessagesPlaceholder` 的作用
- [x] 启动服务后 `/chat` 接口仍然可用

---

## 11. 面试可讲点

> "我在项目里把 Prompt 抽到了独立模块，每个模板带版本号，service 层只通过 LCEL 编排 `prompt | llm | parser`，业务代码 8 行就能完成调用。  
> 这样做的好处是：改 prompt 不需要动 service，未来可以接入 LangSmith 做版本对比和评测。  
> Prompt 模板用 `ChatPromptTemplate.from_messages` + `MessagesPlaceholder`，为下一阶段会话记忆和工具调用预留了扩展位。"

---

## 12. 下一步：Day 4

**主题：Structured Output**

让模型直接返回 Pydantic 对象，替代手写 `json.loads`。  
LangChain 1.x 推荐 `llm.with_structured_output(SomeSchema)`。

预期收获：

- 不再让模型返回纯文本然后自己解析
- 类型安全：返回的就是带类型注解的 Python 对象
- 为 RAG 引用片段、Agent 工具调用打基础
