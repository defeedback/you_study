'''
Author: DefeedBack
Date: 2026-07-10 10:42:22
LastEditors: DefeedBack
LastEditTime: 2026-07-10 13:36:28
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
import faiss
import numpy as np
from app.schemas.chunk import DocumentChunk

class VectorStore:
    def __init__(self,dim:int=2048):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.chunks: list[DocumentChunk] = []

    def _to_normalized_array(self, vectors: list[list[float]]) -> np.ndarray:
        arr = np.array(vectors, dtype=np.float32)
        faiss.normalize_L2(arr)
        return arr
    
    def add(self,chunks: list[DocumentChunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("文本块和向量长度不一致")
        
        vectors = self._to_normalized_array(vectors)
        self.index.add(vectors)
        self.chunks.extend(chunks)

    def search(self,query_vector: list[float], top_k: int=3) -> list[tuple[DocumentChunk,float]]:
        arr = self._to_normalized_array([query_vector]) # 查询归一化
        scores, indices = self.index.search(arr,top_k) #  scores (1,top_k)  indices (1,top_k)  indices 是chunk的下标

        res = []
        for i,idx in enumerate(indices[0]):
            if idx == -1:
                continue
            res.append((self.chunks[idx],float(scores[0][i])))

        return res
    
if __name__ == "__main__":
    from app.services.embedding_service import EmbeddingService
    embeddingService = EmbeddingService()
    vec = VectorStore()
    

        

