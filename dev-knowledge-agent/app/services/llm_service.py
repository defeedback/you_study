'''
Author: DefeedBack
Date: 2026-06-11 18:06:53
LastEditors: DefeedBack
LastEditTime: 2026-06-18 17:51:19
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
from langchain_core.output_parsers import StrOutputParser
from typing import Iterator
from app.services.llm_client import get_llm,get_llm_with_structuring
from app.prompts.chat import CHAT_PROMPT
from app.schemas.chat import ChatResponseWithStructuring

def generate_chat_answer(message: str) -> str:
    llm = get_llm()


    chain = CHAT_PROMPT | llm | StrOutputParser()

    return chain.invoke({"user_message":message})

def generate_chat_answer_with_structuring(message: str) -> ChatResponseWithStructuring:
    llm = get_llm_with_structuring(ChatResponseWithStructuring)


    # chain = CHAT_PROMPT | llm | StrOutputParser()  #   返回的是 structured LLM不需要StrOutputParser
    chain = CHAT_PROMPT | llm 

    return chain.invoke({"user_message":message})


def stream_chat_answer(messages:str) -> Iterator[str]:
    llm = get_llm()
    chain = CHAT_PROMPT | llm | StrOutputParser()

    # yield chain.stream({"user_message":messages})
    """
    >>> def f():
...     yield range(3)
...
>>> def g():
...     yield from rang(3)
...
>>> list(f())
[range(0, 3)]
>>> def g():
...     yield from range(3)
...
>>> list(g())
[0, 1, 2]
    """
    yield from chain.stream({"user_message":messages}) # 把可迭代对象逐项透传	
