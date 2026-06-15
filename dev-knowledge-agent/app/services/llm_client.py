from functools import lru_cache
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
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