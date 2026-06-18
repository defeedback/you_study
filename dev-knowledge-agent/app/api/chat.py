'''
Author: DefeedBack
Date: 2026-06-11 18:04:11
LastEditors: DefeedBack
LastEditTime: 2026-06-18 09:52:42
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
import logging
from fastapi import APIRouter,HTTPException
from app.schemas.chat import ChatRequest, ChatResponse,ChatResponseWithStructuring
from app.services.llm_service import generate_chat_answer,generate_chat_answer_with_structuring

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat",tags=["聊天接口"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="普通聊天接口",
    description="接收用户问题，调用大模型生成回答"
)
def chat(request: ChatRequest) -> ChatResponse:
    logger.info("收到聊天请求: %s",request.message[:80])

    try:
        answer = generate_chat_answer(request.message)

    except Exception as e:
        logger.exception("llm调用失败")

        raise HTTPException(status_code=502,detail="LLM 调用失败") from e
    
    return ChatResponse(answer=answer)

@router.post(
    "/with_structuring",
    response_model=ChatResponseWithStructuring,
    summary="聊天接口,加入了Structuring模型结构化输出",
    description="接收用户问题，调用大模型生成回答"
)
def chat_with_structuring(request: ChatRequest) -> ChatResponseWithStructuring:
    logger.info("收到聊天请求: %s",request.message[:80])

    try:
        result = generate_chat_answer_with_structuring(request.message)# 直接就是ChatResponseWithStructuring对象

    except Exception as e:
        logger.exception("llm调用失败")

        raise HTTPException(status_code=502,detail="LLM 调用失败") from e
    
    return result 