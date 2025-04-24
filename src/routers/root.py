# -*- coding: utf-8 -*-
# @Time    : 2024/12/19 15:50
# @Author  : codewen77
from fastapi import APIRouter

root_router = APIRouter(tags=["root"])


@root_router.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to openai compatible Server!"}
