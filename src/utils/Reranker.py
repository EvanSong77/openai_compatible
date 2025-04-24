# -*- coding: utf-8 -*-
# @Time    : 2025/3/17 9:56
# @Author  : EvanSong
import asyncio
import time

import aiohttp
import numpy as np

from src.config.env import RERANKER_BASE_URL, RERANKER_BEARER
from src.utils import logs

logger = logs.logger


class RerankerModel:
    def __init__(self):
        self.reranker_url = RERANKER_BASE_URL
        self.headers = {'Authorization': f'Bearer {RERANKER_BEARER}'}
        self.model_type = 'bge-reranker-m3'

    def _prepare_payload(self, user_input, contexts):
        payload = {
            "model": self.model_type,
            "text_1": user_input,
            "text_2": contexts,
            "truncate_prompt_tokens": 8192
        }
        return payload

    def _restore_softmax_score(self, score):
        """对score进行处理"""
        return np.log(score / (1 - score + 0.0001106))

    async def model_response(self, user_input, contexts):
        return await self._single_request(user_input, contexts)

    async def _single_request(self, user_input, contexts):
        payload = self._prepare_payload(user_input, contexts)
        async with aiohttp.ClientSession() as session:
            try:
                s_t = time.time()
                async with session.post(self.reranker_url, headers=self.headers, json=payload) as resp:
                    response_data = await resp.json()
                    logger.info(f'{self.model_type}请求耗时{time.time() - s_t}s')

                    # 对每个数据项的 score 进行处理
                    for entry in response_data['data']:
                        original_score = entry['score']
                        entry['score'] = self._restore_softmax_score(original_score)

                    return response_data
            except Exception as e:
                logger.info(f'执行错误，出现:{e}...')
                return None

    async def __call__(self, user_input, contexts):
        return await self.model_response(user_input, contexts)


async def main():
    reranker = RerankerModel()

    query = "滴滴报警声的音频文件在哪里找"
    contexts = ["你好", "哈哈哈", "ok", "滴滴报警声xxxxx"]

    response = await reranker(query, contexts)
    print(response)


if __name__ == '__main__':
    asyncio.run(main())
