# -*- coding: utf-8 -*-
# @Time    : 2024/12/24 11:56
# @Author  : codewen77
import json
import sys

import nest_asyncio
import requests
from fastapi import HTTPException

from openai_compatible.src.config.env import LLM_BASE_URL

if 'ipykernel' in sys.modules:
    nest_asyncio.apply()


class ChatModel:
    """兼容AIGC中台外部模型"""

    def __init__(self, model_type, stream=False):
        self.base_url = LLM_BASE_URL
        self.conversation_url = self.base_url + '/api/conversation/'
        self.token_url = self.base_url + '/uac/login/token'

        self.headers = {'Authorization': f'Bearer {self.get_token()}'}
        self.stream = stream
        self.url = self._set_url(model_type)
        self.model_type = model_type

    def _set_url(self, model_type):
        if model_type == 'gpt-3.5':
            return self.conversation_url + 'gpt35'
        elif model_type == 'gpt4':
            return self.conversation_url + 'gpt4'
        elif model_type == 'gpt-4o-mini':
            return self.conversation_url + 'gpt4oMini'
        elif model_type == 'deepseek-v3':
            return self.conversation_url + 'deepseek-v3'
        elif model_type == 'deepseek-r1':
            return self.conversation_url + 'deepseek-r1'
        else:
            raise ValueError(
                f"Unknown Type: {model_type}, we support: gpt-3.5, gpt4, gpt-4o-mini, deepseek-v3, deepseek-r1")

    def get_token(self):
        headers = {'Authorization': 'Basic NDQ0MjY6MG9rbShJSk4mKigp'}
        return requests.post(self.token_url, headers=headers).json()['result']['access_token']

    def _prepare_payload(self, user_input, history, temperature, topP, tools):
        if isinstance(user_input, str):
            messages = history + [{"role": "user", "content": user_input}]
        else:
            if not isinstance(user_input[0], dict):
                messages = [{"role": user.role, "content": user.content} for user in user_input]
            else:
                messages = user_input
            messages = history + messages
        payload = {
            "messages": messages,
            "functions": tools,
            "chatOptions": {
                "temperature": temperature,
                "topP": topP,
                "presencePenalty": 0,
                "frequencyPenalty": 0,
            },
            "stream": self.stream,
            "ignoreStatistics": "ignore",
            "userId": "446047"
        }
        return payload

    def model_response(self, user_inputs, history, temperatures, topPs, tools):
        if history is None:
            history = []
        if temperatures is None:
            if 'r1' in self.model_type:
                temperatures = 0.6
            else:
                temperatures = 0.7
        if topPs is None:
            topPs = 0.95
        if self.stream:
            return self._stream_request(user_inputs, history, temperatures, topPs, tools)
        else:
            return self._single_request(user_inputs, history, temperatures, topPs, tools)

    def _single_request(self, user_input, history, temperature, topP, tools):
        payload = self._prepare_payload(user_input, history, temperature, topP, tools)
        try:
            resp = requests.post(self.url, headers=self.headers, json=payload).json()
            if 'r1' in self.model_type:
                return {"reasoning_content": resp['result']['reasoningContent'], "content": resp['result']['content']}
            else:
                return resp['result']['content']
        except Exception as e:
            print(f'执行错误，出现:{e}...')
            raise HTTPException(status_code=500, detail=f'执行错误，出现: {e}...')

    def _stream_request(self, user_input, history, temperature, topP, tools):
        """流式请求，逐块读取响应内容"""
        payload = self._prepare_payload(user_input, history, temperature, topP, tools)
        try:
            with requests.post(self.url, headers=self.headers, json=payload, stream=True) as resp:
                # 判断请求是否成功
                if resp.status_code != 200:
                    raise HTTPException(status_code=500, detail=f"请求失败，状态码: {resp.status_code}")

                for chunk in resp.iter_lines():
                    if chunk:
                        if isinstance(chunk, bytes):
                            decoded_chunk = chunk.decode('utf-8', errors='ignore')
                        else:
                            decoded_chunk = chunk

                        if decoded_chunk.startswith('data:'):
                            decoded_chunk = decoded_chunk[5:].strip()

                        # 解析JSON
                        try:
                            resp_json = json.loads(decoded_chunk)  # 解析去掉前缀后的JSON数据
                            content = resp_json.get("content", "")  # 提取content字段内容
                            if 'r1' in self.model_type:
                                reasoning_content = resp_json.get('reasoningContent', "")
                                chunk_response = json.dumps({
                                    "choices": [
                                        {
                                            "index": 0,
                                            "delta": {
                                                "content": content, "reasoning_content": reasoning_content
                                            },
                                            "finish_reason": "stop",
                                        }
                                    ],
                                    "id": "chatcmpl-12345",
                                    "object": "chat.completion.chunk",
                                    "created": 1690000000,
                                    "model": self.model_type,
                                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                                }, ensure_ascii=False)
                            else:
                                # TODO
                                print(content, end="")
                                chunk_response = json.dumps({
                                    "choices": [
                                        {
                                            "index": 0,
                                            "delta": {"role": "assistant", "content": content},
                                            "finish_reason": "stop",
                                        }
                                    ],
                                    "id": "chatcmpl-12345",
                                    "object": "chat.completion.chunk",
                                    "created": 1690000000,
                                    "model": self.model_type,
                                    "usage": {
                                        "prompt_tokens": 0,
                                        "completion_tokens": 0,
                                        "total_tokens": 0,
                                        "completion_tokens_details": {
                                            "reasoning_tokens": 0,
                                            "accepted_prediction_tokens": 0,
                                            "rejected_prediction_tokens": 0
                                        }
                                    }
                                }, ensure_ascii=False)
                            yield f"data: {chunk_response}\n\n"
                        except json.JSONDecodeError as e:
                            raise HTTPException(status_code=500, detail=f"JSON解析失败: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'执行错误，出现: {e}...')

    def _print(self, response_generator):
        if self.stream:
            # 逐块接收流式响应
            for chunk in response_generator:
                if chunk.startswith('data:'):
                    chunk = chunk[5:].strip()

                # 解析JSON
                resp_json = json.loads(chunk)  # 解析去掉前缀后的JSON数据
                content = resp_json['choices'][0]['delta']['content']  # 提取content字段内容
                print(content, end="", flush=True)
            print()
        else:
            print(response_generator)

    def __call__(self, user_inputs, history=None, temperature=None, top_p=None, tools=None):
        return self.model_response(user_inputs, history, temperature, top_p, tools)
