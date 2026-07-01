from app.schemas.chunk import DocumentChunk,RawDocument



def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_overlap must be smaller than chunk_size")
    
    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks

def chunk_document(
        document: RawDocument,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
) -> list[DocumentChunk]:
    text_chunks = split_text(
        document.content,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks: list[DocumentChunk] = []

    for index, text_chunk in enumerate(text_chunks):
        metadata = {
            **document.metadata,
            "chunk_index": str(index)
        }

        chunks.append(
            DocumentChunk(
                content=text_chunk,
                metadata=metadata
            )
        )
    return chunks

def chunk_documents(
        documents: list[RawDocument],
        chunk_size: int = 500,
        chunk_overlap: int = 50
) -> list[DocumentChunk]:
    all_chunks: list[DocumentChunk] = []

    for document in documents:
        chunks = chunk_document(
            document,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        all_chunks.extend(chunks)

    return all_chunks