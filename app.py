# -*- coding: utf-8 -*-
# @Time    : 2024/10/31 9:31
# @Author  : codewen77
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import v1_router, root_router
from src.utils import logs

app = FastAPI()
logger = logs.logger

app.include_router(v1_router)
app.include_router(root_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,  # 是否支持跨域 cookie
    allow_methods=["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],  # 支持哪些HTTP请求方式
    allow_headers=["*"],
)

if __name__ == '__main__':
    logger.info("*****OpenAI Compatible Server Start!*****")

    uvicorn.run("app:app",
                host='0.0.0.0',
                port=12556,
                log_level="info"
                )
