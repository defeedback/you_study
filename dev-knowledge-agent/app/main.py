"""
入口文件
创建Fastapi 实例
注册路由
配置中间件
配置启动关闭事件
暴露健康检查接口

"""

from fastapi import FastAPI
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api import chat


settings = get_settings()
setup_logging(debug=settings.debug)

app = FastAPI(
    title=settings.app_name,
    description="面向技术学习和代码仓库探索的智能体知识库 Agent API",
    version=settings.app_version
)


app.include_router(chat.router)

@app.get(
        "/",
        summary="项目首页",
        description="用于确认Dev Knowledge Agent 服务是否已经启动",
        tags=["基础接口"],
)
def root():
    return {"message":"Dev Knowledge Agent is running"}


@app.get(
        "/health",
        summary="健康检查",
        description="用于检查服务是否正常运行，通常给监控系统或者部署平台使用",
        tags=["基础接口"]
)
def helth_check():
    """
    检查当前服务是否正常运行。

    返回'status: ok' 表示服务可用
    """
    return {"status":"ok"}



