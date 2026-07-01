from pydantic import BaseModel

class RawDocument(BaseModel):
    content:str
    metadata:dict[str,str]    

class DocumentChunk(BaseModel):
    content: str
    metadata: dict[str,str]