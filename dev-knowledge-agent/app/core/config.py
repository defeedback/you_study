'''
Author: DefeedBack
Date: 2026-06-11 18:07:00
LastEditors: DefeedBack
LastEditTime: 2026-06-29 17:20:51
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict


class Settings(BaseSettings):
    # BaseSettings 自动加载.env文件配置
    app_name: str = "Dev Knowledge Agent"
    app_version: str = "0.1.0"
    debug: bool = False

    llm_api_key: str
    llm_base_url: str
    llm_model:str
    llm_temperature: float = 0.7
    llm_timeout: int = 60

    embedding_base_url: str
    embedding_model: str
    """
    BaseSettings 会依次从多个数据源加载配置
    1. 初始化参数
    2. 环境变量(os.environ)
    3. .env文件
    4. secrets文件
    5. 默认值

    """
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

