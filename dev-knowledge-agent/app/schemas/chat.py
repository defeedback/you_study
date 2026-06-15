'''
Author: DefeedBack
Date: 2026-06-11 18:04:25
LastEditors: DefeedBack
LastEditTime: 2026-06-12 16:20:23
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
from pydantic import BaseModel,Field

class ChatRequest(BaseModel):
    message: str = Field(
        description="用户输入的问题",
        examples=["解释一下什么是rag"],
        min_length=1,
        max_length=2000
    )

class ChatResponse(BaseModel):
    answer: str = Field(
        description="大模型的回答",
        examples=["RAG是检索增强生成"]
    )