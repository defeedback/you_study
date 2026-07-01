'''
Author: DefeedBack
Date: 2026-06-29 15:02:52
LastEditors: DefeedBack
LastEditTime: 2026-06-29 15:43:42
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
from pathlib import Path
from app.schemas.chunk import RawDocument


SUPPORTED_SUFFIXES = {".md",".txt"}


def clean_text(text: str) -> str:
    text = text.replace("\r\n","\n")
    text = text.strip()

    while "\n\n\n" in text:
        text = text.replace("\n\n\n","\n\n")

    return text

def load_text_file(file_path: Path) -> RawDocument:
    text = file_path.read_text(encoding="utf-8")
    cleaned_text = clean_text(text)

    return RawDocument(
        content = cleaned_text,
        metadata={
            "source":file_path.name,
            "file_path":str(file_path)
        }
    )

def load_documents_from_directory(directory: Path) -> list[RawDocument]:
    documents : list[RawDocument] = []

    for file_path  in directory.rglob("*"):
        if not file_path.is_file():
            continue
        
        if file_path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue

        document = load_text_file(file_path)
        documents.append(document)

    return documents
