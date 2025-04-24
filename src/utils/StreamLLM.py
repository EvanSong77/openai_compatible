import json
import sys
import time

import nest_asyncio
import requests
from fastapi import HTTPException

from src.config.env import LLM_BASE_URL
from src.model.chat_model import Message
from src.utils import logs

logger = logs.logger
if 'ipykernel' in sys.modules:
    nest_asyncio.apply()


class ChatModel:
    def __init__(self, model_type, stream=False):
        self.base_url = LLM_BASE_URL
        self.conversation_url = self.base_url + '/api/conversation/'
        self.token_url = self.base_url + '/uac/login/token'

        self.headers = {'Authorization': f'Bearer {self.get_token()}'}
        self.stream = stream
        self.url = self._set_url(model_type)
        self.model_type = model_type

    def _set_url(self, model_type):
        if model_type == 'gpt-4o-mini':
            return self.conversation_url + 'gpt4oMini'
        elif model_type == 'qwen-2.5':
            return self.conversation_url + 'qwen'
        else:
            raise ValueError(f"未知的模型类型: {model_type}")

    def get_token(self):
        headers = {'Authorization': 'Basic NDQ0MjY6MG9rbShJSk4mKigp'}
        return requests.post(self.token_url, headers=headers).json()['result']['access_token']

    def _prepare_payload(self, user_input, history, temperature, topP, tools):
        if isinstance(user_input, str):
            messages = history + [{"role": "user", "content": user_input}]
        else:
            if isinstance(user_input[0], Message):
                messages = [{"role": user.role, "content": user.content} for user in user_input]
            else:
                messages = user_input
            messages = history + messages
        if self.model_type == 'qwen2-72b-instruct':
            payload = {
                "messages": messages,
                "functions": tools,
                "temperature": temperature,
                "top_p": topP,
                "model": "qwen"
            }
            self.headers = {'Authorization': 'Bearer 6fcf3eaf8297ab66c9bc76e54920c8ec'}
        else:
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
            s_t = time.time()
            resp = requests.post(self.url, headers=self.headers, json=payload).json()
            if self.model_type == "qwen2-72b-instruct":
                return resp['result']['content']
            else:
                return resp['result']['content']
        except Exception as e:
            logger.info(f'执行错误，出现:{e}...')
            return None

    def _stream_request(self, user_input, history, temperature, topP, tools):
        """流式请求，逐块读取响应内容"""
        payload = self._prepare_payload(user_input, history, temperature, topP, tools)
        try:
            with requests.post(self.url, headers=self.headers, json=payload, stream=True) as resp:
                # 判断请求是否成功
                if resp.status_code != 200:
                    logger.error(f"请求失败，状态码: {resp.status_code}")
                    raise HTTPException(status_code=500, detail=f"请求失败，状态码: {resp.status_code}")

                for chunk in resp.iter_lines():
                    if chunk:
                        if isinstance(chunk, bytes):
                            decoded_chunk = chunk.decode('utf-8', errors='ignore')
                        else:
                            decoded_chunk = chunk

                        if decoded_chunk.startswith('data:'):
                            decoded_chunk = decoded_chunk[5:].strip()
                        else:
                            logger.warning(f"数据块没有 'data:' 前缀，内容: {decoded_chunk}")

                        # 解析JSON
                        try:
                            resp_json = json.loads(decoded_chunk)  # 解析去掉前缀后的JSON数据
                            content = resp_json.get("content", "")  # 提取content字段内容
                            chunk_response = json.dumps({
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": {"role": "assistant", "content": content},
                                        "finish_reason": "stop"
                                    }
                                ],
                                "id": "chatcmpl-12345",
                                "object": "chat.completion.chunk",
                                "created": 1690000000,
                                "model": "qwen-2.5",
                                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                            }, ensure_ascii=False)

                            yield f"data: {chunk_response}\n\n"
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON解析失败，内容: {decoded_chunk}, 错误: {e}")
                            raise HTTPException(status_code=500, detail=f"JSON解析失败: {e}")
        except Exception as e:
            logger.error(f'执行错误，出现: {e}...')
            return None

    def __call__(self, user_inputs, history=None, temperature=None, top_p=None, tools=None):
        return self.model_response(user_inputs, history, temperature, top_p, tools)


if __name__ == '__main__':
    stream = True
    # 初始化ChatModel，启用流式请求
    gpt = ChatModel('qwen-2.5', stream=stream)

    # 设置用户消息
    messages = [{"role": "user", "content": "请写一篇文章关于宇宙的奥秘，100字左右"}]

    # 获取流式响应
    response_generator = gpt(messages, temperature=0.7, top_p=0.9)

    if stream:
        # 逐块接收流式响应
        for chunk in response_generator:
            print("接收到数据块:", chunk)  # 可选：实时打印每个数据块
    else:
        print(response_generator)
