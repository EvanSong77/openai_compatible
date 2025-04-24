# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 15:16
# @Author  : codewen77
from typing import List, Optional, Union

from pydantic import BaseModel


class RerankerRequest(BaseModel):
    """JinaAI reranker model api"""
    model: str
    query: str
    top_n: Optional[int] = None
    documents: Union[str, List[str]]


class Result(BaseModel):
    index: int
    document: dict
    relevance_score: float


class Usage(BaseModel):
    total_tokens: int


class RerankerResponse(BaseModel):
    """JinaAI reranker model api"""
    model: str
    usage: Usage
    results: List[Result]
