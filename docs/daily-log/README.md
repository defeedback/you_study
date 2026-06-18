# 每日学习日志（daily-log）

按日期记录学习流水，跨电脑同步学习上下文。

## 用途

- 跨设备 / 跨会话延续上下文：换台电脑 `git pull` 后，看最新一份就知道上次到哪
- 与 [notes/](../notes/) 的区别：notes 按**主题**精炼沉淀（面向回顾、面试），daily-log 按**时间**记流水（面向接续）
- 与 memory（`~/.claude/projects/.../memory/`）的区别：memory 是 Claude 跨会话的长期记忆但**只在本机**；daily-log 入仓库走 git，是真正的跨设备

## 文件命名

`YYYY-MM-DD.md`，例如 `2026-06-18.md`。

## 模板

```md
# YYYY-MM-DD · Week X · Day Y

**学习主题**：xxx
**对应路线阶段**：第 X 周 Day Y

## 今天做了什么

-

## 今天学到的关键点

-

## 卡在哪 / 没解决的问题

-

## 代码改动

- `path/to/file.py`：xxx

## 明天接着做

-
```

## 工作流

- 学习开始时跟 Claude 说"开始第 X 天"，Claude 会读这个目录最新一份对齐进度
- 学习结束（或说"收尾"）时，Claude 起草当天日志，你审阅后 `git commit && push`
