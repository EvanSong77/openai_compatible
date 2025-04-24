# -*- coding: utf-8 -*-
# @Time    : 2024/10/30 17:08
# @Author  : codewen77
from fastapi import APIRouter

from src.routers.chat_router import chat_router
from src.routers.embedding_router import embedding_router
from src.routers.reranker_router import reranker_router
from src.routers.root import root_router

v1_router = APIRouter(prefix="/v1", tags=["v1"])
v1_router.include_router(chat_router, tags=["chat completion"])
v1_router.include_router(embedding_router, tags=["embeddings"])
v1_router.include_router(reranker_router, tags=["embeddings"])

__all__ = ["v1_router", "root_router"]
