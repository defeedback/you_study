'''
Author: DefeedBack
Date: 2026-06-25 17:15:31
LastEditors: DefeedBack
LastEditTime: 2026-06-25 22:11:27
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
import time
import uuid
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse


app = FastAPI()

#  自定义异常类
class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 500):
        super().__init__(code, message, status_code)
        self.code = code
        self.message = message
        self.status_code  = status_code 

# 全局异常处理器
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    trace_id = getattr(request.state, "trace_id","unknown")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code":exc.code,
            "message":exc.message,
            "trace_id":trace_id
        }
    )

# 中间件
@app.middleware("http")# 拦截所有http请求
async def logging_middleware(request:Request, call_next):
    # 生成 trace_id
    trace_id = uuid.uuid4().hex[:8]
    request.state.trace_id = trace_id

    print(f"[{trace_id}] 请求开始： {request.method}  {request.url.path}")

    # 调用下一个处理器
    response = await call_next(request)

    duration = time.time()
    print(f"[{trace_id}] 请求结束： 状态码={response.status_code}, 耗时={duration*1000:.2f}ms")


    return response

# 路由
@app.get("/ok")
def ok_endpoing():
    return {"messages":"正常"}

@app.get("/error")
def error_endpoint():
    # 直接抛出异常
    raise AppException(code="TEST_ERROR",message="这是一个测试错误",status_code=400)