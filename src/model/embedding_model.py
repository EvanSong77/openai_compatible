# -*- coding: utf-8 -*-
# @Time    : 2024/10/30 17:25
# @Author  : codewen77
from typing import List, Optional, Union

from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    model: str
    input: Union[str, List[str]]


class Embedding(BaseModel):
    index: int
    embedding: List[float]


class EmbeddingResponse(BaseModel):
    data: List[Embedding]
    model: str
    usage: Optional[dict] = None
