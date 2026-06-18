'''
Author: DefeedBack
Date: 2026-06-12 15:10:26
LastEditors: DefeedBack
LastEditTime: 2026-06-18 16:09:37
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
from functools import lru_cache
from typing import Type
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from app.core.config import get_settings

@lru_cache
def get_llm() -> BaseChatModel:
    settings = get_settings()
    return init_chat_model(
        model=settings.llm_model,
        api_key = settings.llm_api_key,
        temperature = settings.llm_temperature,
        model_provider="openai",
        base_url = settings.llm_base_url
    )

def get_llm_with_structuring(schema: Type[BaseModel]) -> Runnable:

    return get_llm().with_structured_output(schema)