'''
Author: DefeedBack
Date: 2026-06-25 22:33:09
LastEditors: DefeedBack
LastEditTime: 2026-06-25 23:20:02
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
import time
import uuid
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    # 1. 生成trace_id
    trace_id = uuid.uuid4().hex[:8]
    request.state.trace_id = trace_id

    # 2. 记录请求开始
    logger.info("[%s] %s %s - 请求开始",trace_id, request.method, request.url.path)
    start_time = time.time()

    # 3. 调用下一个处理器
    response = await call_next(request)

    # 4. 记录请求结束
    duration = (time.time() - start_time) *1000
    logger.info("[%s] 状态码=%d 耗时=%.2fms",trace_id,response.status_code, duration)

    # 5. 把trace_id 放到请求头
    response.headers["X-Trace-Id"] = trace_id

    return response
