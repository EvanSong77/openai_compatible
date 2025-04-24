# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 15:03
# @Author  : codewen77
from fastapi import APIRouter, Depends, HTTPException

from src.model.jina_reranker_model import RerankerResponse, RerankerRequest, Result, Usage
from src.utils.Reranker import RerankerModel
from src.utils.bearer import verify_token

reranker_router = APIRouter()
reranker = RerankerModel()


@reranker_router.post("/rerank", response_model=RerankerResponse)
async def create_embeddings(request: RerankerRequest, token: str = Depends(verify_token)):
    try:
        if isinstance(request.query, str):
            try:
                request.query = eval(request.query)
            except:
                pass
        resp = await reranker(request.query, request.documents)
        if request.top_n:
            sorted_results = sorted(resp['data'], key=lambda x: x['score'], reverse=True)
            top_n_results = sorted_results[:request.top_n]
            results = [
                Result(
                    index=i,
                    document={"text": request.documents[i]},
                    relevance_score=r['score']
                )
                for i, r in enumerate(top_n_results)
            ]
        else:
            results = [
                Result(
                    index=i,
                    document={"text": request.documents[i]},
                    relevance_score=r['score']
                )
                for i, r in enumerate(resp['data'])
            ]
        response = RerankerResponse(
            model=request.model,
            usage=Usage(total_tokens=resp['usage']['total_tokens']),
            results=results
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
