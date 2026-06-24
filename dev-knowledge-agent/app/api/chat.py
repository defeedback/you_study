'''
Author: DefeedBack
Date: 2026-06-11 18:04:11
LastEditors: DefeedBack
LastEditTime: 2026-06-24 15:23:30
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
import logging
from fastapi import APIRouter,HTTPException
from app.schemas.chat import ChatRequest, ChatResponse,ChatResponseWithStructuring
from app.services.llm_service import generate_chat_answer,generate_chat_answer_with_structuring,stream_chat_answer
from fastapi.responses import StreamingResponse

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

def _sse_format(text: str) -> str:
    """
    把一段文本包成一条 SSE event
    """

    # 1. 统一换行符
    safe = text.replace("\r\n","\n").replace("\r", "\n")

    # 2. 每行前加data

    lines = safe.split("\n")
    payload = "\n".join(f"data: {line}" for line in lines)
    
    # 3. 以空行结尾
    return payload + "\n\n"

@router.post(
    "/stream",
    summary="流式聊天接口(SSE)",
    description="以server-sent events形式逐 token 返回模型回答"
)
def chat_stream(request: ChatRequest):
    logger.info("收到流式聊天请求 %s",request.message[:80])

    def event_generator():
        try:
            for chunk in stream_chat_answer(request.message):
                if chunk:
                    yield _sse_format(chunk)
            yield "data: [DONE]\n\n"

        except Exception:
            logger.exception("LLM大模型流式调用失败")
            yield _sse_format("[ERROR] LLm 调用失败")
            yield "data: [DONE]\n\n"
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":"no-cache",
            "X-Accel-Buffering":"no"
        }
    )