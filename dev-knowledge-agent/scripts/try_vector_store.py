'''
Author: DefeedBack
Date: 2026-07-14 17:42:44
LastEditors: DefeedBack
LastEditTime: 2026-07-14 17:43:07
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.schemas.chunk import DocumentChunk

texts = [
    "Python 是一门解释型编程语言",
    "FAISS 是 Meta 开源的向量检索库",
    "今天成都的天气很热",
]
emb = EmbeddingService()
vectors = emb.embed_texts(texts)

store = VectorStore()
chunks = [DocumentChunk(content=t, metadata={}) for t in texts]
store.add(chunks, vectors)

query = "向量数据库怎么用"
q_vec = emb.embed_texts([query])[0]      # 注意取 [0]
results = store.search(q_vec, top_k=2)

for chunk, score in results:
    print(f"{score:.4f}  {chunk.content}")