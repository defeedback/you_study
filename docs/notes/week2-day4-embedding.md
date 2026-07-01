# Week 2 · Day 4：接入火山引擎 Embedding

**日期**:2026-06-30  
**对应阶段**:2 个月路线 · 第 2 周 Day 4  
**主题**:把 chunk 文本调火山引擎 Ark Embedding API 转成向量

---

## 0. 一句话总结

> Embedding 就是把文本变成向量,让程序能算"语义相似度"。今天是 RAG 建库阶段最不可控的一步(调外部 API),跑通后后面都是本地操作。

今天完成的是 RAG 建库阶段的第三步:

```text
DocumentChunk.content(文本)
  ↓
EmbeddingService(调火山引擎 Ark API)
  ↓
list[list[float]](向量)
```

---

## 1. Embedding 在 RAG 里的位置

```text
建库阶段:
文档读取 → 切块 → 【Embedding】 → 存向量库

查询阶段:
用户问题 → 【Embedding】 → 向量检索 → 拼 Prompt → LLM
```

建库和查询都要用 Embedding,所以这一步是 RAG 的核心能力。

---

## 2. 火山引擎 Ark Embedding 接口

### 2.1 接口地址

```text
POST https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal
```

注意:这是**多模态**(multimodal)接口,支持文本、图片、视频。Week 2 只用文本部分。

### 2.2 鉴权

```text
Header: Authorization: Bearer <API_KEY>
```

### 2.3 请求体(文本场景)

```json
{
    "model": "doubao-embedding-vision-251215",
    "encoding_format": "float",
    "input": [
        {"type": "text", "text": "要向量化的文本"}
    ]
}
```

关键点:

- `input` 是**对象数组**,每个对象有 `type` 和 `text`
- 文本场景 `type` 固定 `"text"`
- `encoding_format` 用 `"float"`(也可以不传,默认就是 float)

### 2.4 返回结构(重点!)

```json
{
    "created": 1782797590,
    "data": {
        "embedding": [0.01, -0.03, ...]
    }
}
```

**关键差异**:

```text
data 是对象(object),不是数组!
data.embedding 直接就是向量数组
```

这和 OpenAI 标准格式(`data` 是数组,每项一个 `embedding`)**不一样**。取值路径必须是:

```python
res.json()["data"]["embedding"]
```

而不是:

```python
res.json()["data"][0]["embedding"]   # ❌ 会报错
```

---

## 3. 重要发现:多模态接口不支持批量

### 3.1 测试现象

传两条文本:

```json
"input": [
    {"type": "text", "text": "天很蓝"},
    {"type": "text", "text": "海很深"}
]
```

返回**只有一个向量**,不是两个。

### 3.2 验证

分别发两个单条请求:

```text
"天很蓝" → [-0.020, -0.017, -0.015, ...]
"海很深" → [0.015, -0.008, -0.012, ...]
```

向量不同,说明单条请求正常,但批量时接口只返回一个向量。

### 3.3 结论

火山引擎多模态 embedding 接口**不支持批量**。`embed_texts` 必须**循环单条发请求**。

### 3.4 影响

117 个 chunk 要发 117 次请求,比较慢。Day 5 建库时可以加缓存或并发优化。

---

## 4. 向量维度

实测返回的 `embedding` 数组长度:

```text
维度 = 2048
```

这个数字 **Day 5 建 FAISS 索引时必须用到**,FAISS 索引的维度要和向量维度一致,否则建不出来或检索错乱。

模型还支持 1024 维(通过 `dimensions` 参数指定),Week 2 用默认 2048。

---

## 5. 最终代码

```python
from app.core.config import get_settings
import httpx


class EmbeddingService():
    def __init__(self):
        settings = get_settings()
        self.embedding_model = settings.embedding_model
        self.embedding_base_url = settings.embedding_base_url
        self.api_key = settings.llm_api_key

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            res = httpx.post(
                self.embedding_base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.embedding_model,
                    "encoding_format": "float",
                    "input": [{"type": "text", "text": text}]
                },
                timeout=30
            )
            res.raise_for_status()
            vectors.append(res.json()["data"]["embedding"])

        return vectors
```

---

## 6. 关键代码点

| 代码 | 作用 |
|---|---|
| `httpx.post(url, headers=, json=, timeout=)` | 发 POST 请求,json 参数会自动序列化 |
| `headers={"Authorization": f"Bearer {self.api_key}"}` | 火山引擎 API Key 鉴权 |
| `res.raise_for_status()` | 状态码 4xx/5xx 自动抛异常,省得自己判断 |
| `res.json()["data"]["embedding"]` | 取值路径,注意 `data` 是对象不是数组 |
| 循环单条发 | 多模态接口不支持批量 |

---

## 7. 今日踩坑:httpx response 不能用 `.data.embedding`

错误写法:

```python
res = httpx.post(...)
response.append(res.data.embedding)   # ❌
```

原因:`httpx.Response` 对象**没有 `.data` 属性**,不像有些库支持对象式访问。

正确写法:

```python
data = res.json()                      # 先拿 dict
vectors.append(data["data"]["embedding"])  # 再按键取
```

---

## 8. 今日踩坑:漏逗号导致 SyntaxError

```python
headers={"Authorization": f"Bearer {self.api_key}"}
json={
```

`headers=...` 后面漏了逗号,Python 会报 `SyntaxError`。

正确:

```python
headers={"Authorization": f"Bearer {self.api_key}"},
json={
```

教训:多行参数之间一定要用逗号分隔,`}` 后面别忘了。

---

## 9. 今日踩坑:Python 脚本运行报 `No module named 'app'`

### 9.1 现象

```bash
uv run python scripts/try_embedding.py
# ModuleNotFoundError: No module named 'app'
```

### 9.2 原因

Python 启动方式决定 `sys.path[0]`:

| 启动方式 | `sys.path[0]` | 能找到 `app` 吗 |
|---|---|---|
| `python -c "import app"` | `''`(当前工作目录) | ✅ |
| `python -m scripts.try` | `''`(当前工作目录) | ✅ |
| `python scripts/try.py` | `scripts/`(脚本所在目录) | ❌ |

`python scripts/try.py` 会把 `scripts/` 当搜索根,去找 `app` 找的是 `scripts/app`,找不到。

### 9.3 解决

用 `-m` 方式运行:

```bash
cd e:/study/you_study/dev-knowledge-agent
uv run python -m scripts.try_embedding
```

前提:`scripts/` 下要有 `__init__.py`(空文件)。

### 9.4 长期方案

养成习惯:**不用 `python xxx.py`,永远用 `python -m xxx`**。VSCode 调试用 `launch.json` 的 `"module"` 字段代替 `"program"`。

---

## 10. 今日踩坑:VSCode 调试 launch.json

### 10.1 最小配置

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug try_embedding",
            "type": "debugpy",
            "request": "launch",
            "module": "scripts.try_embedding",
            "cwd": "${workspaceFolder}/dev-knowledge-agent",
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

### 10.2 关键字段

| 字段 | 作用 |
|---|---|
| `module` | 用 `-m` 跑的模块路径,换脚本改这里 |
| `cwd` | 工作目录,必须指向项目根 `dev-knowledge-agent/` |
| `justMyCode: false` | 能进第三方库断点 |

### 10.3 为什么需要 launch.json

VSCode 工作区根是 `you_study/`,但项目根是 `dev-knowledge-agent/`。不指定 `cwd` 会导致 `sys.path` 不对,找不到 `app` 包。

---

## 11. 配置说明

### 11.1 `.env`

```env
EMBEDDING_BASE_URL=https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal
EMBEDDING_MODEL=doubao-embedding-vision-251215
```

### 11.2 `config.py`

```python
embedding_base_url: str
embedding_model: str
```

### 11.3 待改进:key 复用

当前:

```python
self.api_key = settings.llm_api_key
```

复用 LLM 的 key。如果火山 embedding 和对话是同一个 key,没问题;如果以后分开,应该在 `config.py` 加 `embedding_api_key` 字段。

---

## 12. 测试脚本

```python
# scripts/try_embedding.py
from app.services.embedding_service import EmbeddingService


def main():
    s = EmbeddingService()
    vecs = s.embed_texts(["天很蓝", "海很深"])
    print("数量:", len(vecs))
    print("维度:", len(vecs[0]))
    print("前5个值:", vecs[0][:5])


if __name__ == "__main__":
    main()
```

运行:

```bash
cd e:/study/you_study/dev-knowledge-agent
uv run python -m scripts.try_embedding
```

实际输出:

```text
数量: 2
维度: 2048
前5个值: [-0.0203857421875, -0.017578125, -0.015625, 0.018310546875, -0.007232666015625]
```

---

## 13. Day 4 验收清单

- [x] `.env` 加 embedding 配置
- [x] `config.py` 加 embedding 字段
- [x] 写 `embedding_service.py`
- [x] 确认火山引擎返回结构(`data` 是对象)
- [x] 确认不支持批量,改成循环单条发
- [x] 修复取值路径 `data["data"]["embedding"]`
- [x] 修复漏逗号语法错误
- [x] 用 `python -m` 跑通测试
- [x] 确认向量维度 2048

---

## 14. 面试可讲点

> RAG 建库阶段,我实现了 EmbeddingService,调火山引擎 Ark 的多模态 embedding 接口,把文本 chunk 转成 2048 维向量。
>
> 接入过程中我发现火山多模态接口和 OpenAI 标准格式有差异:返回的 `data` 是对象而不是数组,取值路径要写成 `data["data"]["embedding"]`。另外多模态接口不支持批量,传多条文本只返回一个向量,所以我改成循环单条发请求。后续如果 chunk 数量大,可以加并发或缓存优化。
>
> 工程上我把测试脚本放在 `scripts/` 下,用 `python -m scripts.xxx` 方式运行,避免 `sys.path` 找不到 `app` 包的问题,并配了 VSCode launch.json 支持断点调试。

---

## 15. 当前 RAG 建库进度

```text
✅ Day 2:文档读取 → RawDocument
✅ Day 3:切块     → DocumentChunk
✅ Day 4:Embedding → 向量(2048 维)
⬜ Day 5:向量库   → FAISS 检索
⬜ Day 6:拼 Prompt → LLM 回答
```

---

## 16. 下一步:Week 2 Day 5

Day 5 主题:

> FAISS 向量库,把向量存进去并支持相似度检索。

计划:

```text
DocumentChunk + 向量
  ↓
FAISS 索引(维度 2048)
  ↓
存盘 / 加载
  ↓
search(query_vector, top_k=3)
```

要点预告:

- FAISS 索引维度必须是 2048
- 向量和 chunk 要对应存储(FAISS 只存向量,文本要自己存)
- 检索返回的是 chunk 的 index,要能找回原文
- 索引可以存盘,避免每次重启都重新 embedding
