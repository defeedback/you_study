# Q&A · Day 4：Structured Output

> 这是配套 [week1-day4-structured-output.md](../week1-day4-structured-output.md) 的问答笔记。
> 记录学习中真实卡过的疑问、当时的理解、最终的答案。

---

## Q1: StrOutputParser 报 ValidationError 是什么意思？

**👀 我当时卡在哪**：跑 `/chat/with_structuring` 接口，控制台一堆 traceback，看到 "Generation text must be string" 完全不知道在说什么。

**🤔 我当时的理解**：以为是模型返回格式不对，想着是不是要在 prompt 里加"请只返回 JSON"。

**✅ 真实原因**：

```text
chain = CHAT_PROMPT | llm | StrOutputParser()
                       ↑          ↑
                  返回 Pydantic   只接受 str
                   对象           
```

`with_structured_output` 之后，LLM 返回的已经是 Pydantic 对象，不是字符串。`StrOutputParser` 期待字符串，拿到对象就抛 ValidationError。

错误信息里 `input_value=ChatResponseWithStructuri...` 已经把答案告诉我了——它在告诉我"我收到了一个对象"——只是当时没看懂。

**💡 一句话记忆**：

> `with_structured_output` 和 `StrOutputParser` 互斥。前者吐对象，后者吃字符串。两个一起用等于"用筷子喝汤"。

> ← 主笔记位置：[整体框架对比](../week1-day4-structured-output.md#2-整体框架)

---

## Q2: 不要 chain 怎么处理 system prompt？

**👀 我当时卡在哪**：Claude 给的最简代码是 `llm.invoke(message)`，我看到没有 `CHAT_PROMPT` 就慌了——那我之前 Day 3 工程化拎出来的 system prompt 不就白搭了？

**🤔 我当时的理解**：以为"structured output 模式 = 不需要 prompt 模板"。

**✅ 真实情况**：那是为了让我**最快跑通**给的简化版。生产里 100% 还是要 system prompt——否则角色约束、不要编造、回答风格全丢。

正确的拼法：

```python
# 普通 chain
chain = CHAT_PROMPT | llm | StrOutputParser()

# structured chain
chain = CHAT_PROMPT | llm        # ← 只是去掉 parser，prompt 还在
```

system prompt **没消失**，只是少了 `StrOutputParser` 这一节。`llm.invoke(message)` 那种简化写法只适合临时调试，不能进 service 层。

**💡 一句话记忆**：

> structured output 改的是"输出端"，不是"输入端"。prompt 该怎么用还怎么用。

> ← 主笔记位置：[Prompt 没消失，只是 chain 拼法变了](../week1-day4-structured-output.md#5-prompt-没消失只是-chain-拼法变了)

---

## Q3: Literal 怎么导入？

**👀 我当时卡在哪**：在 schemas 里写 `confidence: Literal["高", "中", "低"]`，IDE 标红 `Literal` 未定义，不知道从哪导入。

**🤔 我当时的理解**：以为 `Literal` 是 LangChain 或 Pydantic 提供的，到处找。

**✅ 真实答案**：`Literal` 是 Python 标准库 `typing` 里的，不用装包：

```python
from typing import Literal
```

它和我熟悉的 `Optional`、`Union` 是一家人。

顺便补一张同类工具表：

| 工具 | 用途 | 导入 |
|---|---|---|
| `Literal["A", "B"]` | 锁死字符串枚举 | `from typing import Literal` |
| `Enum` | 完整枚举类 | `from enum import Enum` |
| `Optional[str]` | 等同 `str \| None` | `from typing import Optional` |

LangChain / FastAPI 项目优先用 `Literal`——schema 转换最丝滑。

**💡 一句话记忆**：

> 类型工具找不到家时，先试 `from typing import 它`。十有八九在标准库。

> ← 主笔记位置：[Literal 的三层作用](../week1-day4-structured-output.md#4-literal-的三层作用)

---

## Q4: 我的代码工程上还有什么问题？

**👀 我当时卡在哪**：跑通了，自我感觉良好，问 Claude "你看看我的代码呢"——心里其实是想被夸两句。

**🤔 我当时的理解**：以为"跑通 = 完成"。

**✅ 真实答案**：跑通只是 60 分。Claude 给我指出了**分层依赖反向**的问题：

```python
# llm_client.py（基础设施层）
from app.schemas.chat import ChatResponseWithStructuring  # ❌ 反过来依赖业务
```

正确的依赖方向应该是：

```text
api      ──>  services（业务）   ──>  llm_client（基础设施）
                  ↓
              schemas（数据结构）
```

业务依赖基础设施 ✅，基础设施反过来依赖业务 ❌。

修复办法：让 `get_llm_with_structuring(schema)` 接受 schema 参数，把"用哪个 schema"的决定权还给业务层。

**💡 一句话记忆**：

> 跑通 ≠ 工程化。代码能用之后再问一遍："谁依赖谁？方向对吗？"

> ← 主笔记位置：[分层重构](../week1-day4-structured-output.md#6-分层重构基础设施层-vs-业务层)

---

## 我犯过的错

把今天踩过的具体错误集中列出来，下次写新代码前扫一眼。

| # | 错误 | 教训 |
|---|---|---|
| 1 | structured LLM 后面套 `StrOutputParser` | structured output 已经替你解析了，再加 parser 多此一举 |
| 2 | 路由里两个函数都叫 `chat` | Python 后定义的覆盖前面的，FastAPI 不会报错但行为错乱 |
| 3 | `Field("模型回答内容")` | Field 第一个位置参数是 default，写说明必须用关键字 `description=` |
| 4 | `return ChatResponseWithStructuring(result)` | result 已经是该类型实例，二次包裹会抛字段缺失 |
| 5 | `response_model=ChatResponse` 但实际返回 `ChatResponseWithStructuring` | 类型不一致，FastAPI 校验失败 |
| 6 | `llm_client` 反向 import `schemas` | 基础设施依赖业务，违反分层原则 |
| 7 | `get_llm_with_structuring` 重新 `init_chat_model` | 没复用 `get_llm()` 单例，产生两份 HTTP 连接池 |
| 8 | `confidence: str` 没加约束 | 模型可能返回 "high"、"中等" 等花式答案 |

**犯错频率最高的根因**：

- 4 个错跟"类型/范围"有关（1、3、4、5、8）→ **下次写 schema 先想清楚每个字段的边界**
- 2 个错跟"分层"有关（6、7）→ **写完 import 先问：依赖方向对吗？**
- 1 个错跟"命名"有关（2）→ **同一个文件多个路由函数，名字不能重**

---

## 一周后回看

> 留空，等到 2026-06-25 左右回来填：
>
> - 现在哪些问题已经变成"理所当然"了？
> - 哪些当时记的"一句话记忆"现在已经不需要了？
> - 哪些是当时没记但现在觉得很重要的？

---

## 给未来的我

如果再遇到 ValidationError 类的报错，**先看 `input_value` 是什么类型，再看期待什么类型**。报错信息已经把答案告诉你了，只是 traceback 太长容易吓到。
