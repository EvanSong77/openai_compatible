# -*- coding: utf-8 -*-
# @Time    : 2024/10/30 17:33
# @Author  : codewen77
import asyncio
import sys
import time

import aiohttp
import nest_asyncio
import requests
from tqdm import tqdm

from src.config.env import EMBEDDING_BASE_URL, EMBEDDING_BEARER
from src.utils import logs

logger = logs.logger
if 'ipykernel' in sys.modules:
    nest_asyncio.apply()


class EmbeddingModel:
    def __init__(self, concurrent_requests=1):
        self.base_url = EMBEDDING_BASE_URL
        self.embedding_url = self.base_url + '/embedding'
        self.concurrent_requests = concurrent_requests

        self.headers = {'Authorization': f'Bearer {EMBEDDING_BEARER}'}

        self.model_type = 'bge-m3'

    def _prepare_payload(self, user_input):
        payload = {
            "model": self.model_type,
            "input": user_input,
        }
        return payload

    def model_response(self, user_input):
        if self.concurrent_requests == 1:
            return self._single_request(user_input)
        else:
            return self.auto_run(user_input)

    def _single_request(self, user_input):
        payload = self._prepare_payload(user_input)
        try:
            s_t = time.time()
            resp = requests.post(self.embedding_url, headers=self.headers, json=payload).json()
            logger.info(f'{self.model_type}请求耗时{time.time() - s_t}s')
            return resp
        except Exception as e:
            logger.info(f'执行错误，出现:{e}...')
            return None

    async def async_model_response(self, session, semaphore, user_input):
        payload = self._prepare_payload(user_input)

        async with semaphore:
            async with session.post(self.embedding_url, json=payload, headers=self.headers) as response:
                resp = await response.json()
                return resp

    async def run_async(self, user_input):
        semaphore = asyncio.Semaphore(self.concurrent_requests)
        async with aiohttp.ClientSession() as session:
            tasks = []
            s_t = time.time()
            with tqdm(total=len(user_input), desc="处理请求") as pbar:
                async def track_progress(coro):
                    result = await coro
                    pbar.update(1)
                    return result

                for i, user_input in enumerate(user_input):
                    task = track_progress(
                        self.async_model_response(session, semaphore, user_input)
                    )
                    tasks.append(task)

                responses = await asyncio.gather(*tasks)
            logger.info(f'{self.model_type}请求耗时{time.time() - s_t}s')
            return responses

    def auto_run(self, user_input):
        if 'ipykernel' in sys.modules:
            return asyncio.run(self.run_async(user_input))
        else:
            return self.run_concurrent(user_input)

    def run_concurrent(self, user_input):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.run_async(user_input))
        except RuntimeError:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            return new_loop.run_until_complete(self.run_async(user_input))

    def __call__(self, user_input):
        return self.model_response(user_input)


if __name__ == '__main__':
    # =====================调用示例=====================
    # 单线程调用（默认concurrent_requests=1)
    emb = EmbeddingModel()
    message = ["1.xxx \t", "哈哈哈", "你好"]
    print(emb(message))

    # 并发调用（设置并发数 concurrent_requests 并为每个请求指定不同的 temperature 和 topP)
    emb_async = EmbeddingModel(concurrent_requests=4)
    user_inputs = [
        ["1.xxxx \t", "哈哈哈", "你好"],
        ["2.xxxx \t", "哈哈哈", "你好"],
        ["3.xxxx \t", "哈哈哈", "你好"]
    ]
    print(emb_async(user_inputs))
