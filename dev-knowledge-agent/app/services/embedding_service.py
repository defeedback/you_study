'''
Author: DefeedBack
Date: 2026-06-29 17:21:11
LastEditors: DefeedBack
LastEditTime: 2026-06-30 13:51:34
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
from app.core.config import get_settings
import httpx
class EmbeddingService():
    def __init__(self):
        settings = get_settings()
        self.embedding_model = settings.embedding_model
        self.embedding_base_url = settings.embedding_base_url
        self.api_key = settings.llm_api_key
    
    def embed_texts(self,texts:list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            res = httpx.post(
                self.embedding_base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model":self.embedding_model,
                    "encoding_format": "float",
                    "input":[{"type":"text","text":text}]
                },
                timeout=30
            )
            res.raise_for_status()
            vectors.append(res.json()["data"]["embedding"])

        return vectors