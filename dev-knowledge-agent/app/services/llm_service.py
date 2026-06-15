'''
Author: DefeedBack
Date: 2026-06-11 18:06:53
LastEditors: DefeedBack
LastEditTime: 2026-06-15 23:30:22
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.llm_client import get_llm


SYSTEMM_PROMPT = "你是一个面向开发者的技术学习助手。回答要求：1. 使用中文回答 2. 技术术语保留英文 3. 简洁、准确、有结构"

def generate_chat_answer(message: str) -> str:
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system",SYSTEMM_PROMPT),
        ("human","{user_message}"),
    ])

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"user_message":message})


