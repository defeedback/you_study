'''
Author: DefeedBack
Date: 2026-06-11 18:04:25
LastEditors: DefeedBack
LastEditTime: 2026-06-18 09:58:24
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
from pydantic import BaseModel,Field
from typing import Literal

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

class ChatResponseWithStructuring(BaseModel):
    """聊天接口结构化输出"""
    answer: str = Field(description="模型回答内容")
    confidence: Literal["高","中","低"] = Field(description="回答置信度,取值为中高低")
    follow_up_questions: list[str] = Field(
        default_factory=list,
        description="推荐1-3个追问"
    )