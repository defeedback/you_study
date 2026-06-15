'''
Author: DefeedBack
Date: 2026-06-15 15:33:37
LastEditors: DefeedBack
LastEditTime: 2026-06-15 17:50:30
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''

from langchain_core.prompts import ChatPromptTemplate

# 版本号
CHAT_PROMPT_VERSION = "v1.0"

# 系统提示词
SYSTEM_PROMPT = """
你是一个面向开发者的技术学习助手。

回答要求：
1. 用中文回答
2. 技术术语保留英文
3. 回答简洁、准确、有结构
4. 不确定的内容明确说明"我不确定"，不要编造
"""

CHAT_PEOMPT = ChatPromptTemplate.from_messages([
    ("system",SYSTEM_PROMPT),
    ("human","{user_message}")
])
