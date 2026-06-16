'''
Author: DefeedBack
Date: 2026-06-11 18:06:53
LastEditors: DefeedBack
LastEditTime: 2026-06-16 16:53:15
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
from langchain_core.output_parsers import StrOutputParser
from app.services.llm_client import get_llm
from app.prompts.chat import CHAT_PROMPT

def generate_chat_answer(message: str) -> str:
    llm = get_llm()


    chain = CHAT_PROMPT | llm | StrOutputParser()

    return chain.invoke({"user_message":message})


