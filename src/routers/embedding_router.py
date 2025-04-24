# -*- coding: utf-8 -*-
# @Time    : 2024/10/30 17:26
# @Author  : codewen77
from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAIError

from src.model.embedding_model import EmbeddingResponse, EmbeddingRequest, Embedding
from src.utils.Embedding import EmbeddingModel
from src.utils.bearer import verify_token

embedding_router = APIRouter()
emb = EmbeddingModel()


@embedding_router.post("/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest, token: str = Depends(verify_token)):
    try:
        print(f"============embedding:{request.input}============")
        if isinstance(request.input, str):
            try:
                request.input = eval(request.input)
            except:
                pass
        resp = emb(request.input)
        embeddings = [
            Embedding(index=r['index'], embedding=r['embedding']) for r in resp['data']
        ]
        response = EmbeddingResponse(
            data=embeddings,
            model=resp['model'],
            usage=resp['usage']
        )
        return response
    except OpenAIError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
