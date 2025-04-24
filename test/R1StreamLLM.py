# -*- coding: utf-8 -*-
# @Time    : 2025/3/20 20:47
# @Author  : EvanSong

# 流式
from openai import OpenAI

# 6fcf3eaf8297ab66c9bc76e54920c8ec http://10.1.110.2:8888/qwq/v1
# yLZJJb8-EBsdUf2IimbGFNkaONMwbZy2WNh5luqpkWk http://10.25.72.148:12556 http://10.1.110.2:8888/open-api
client = OpenAI(api_key="yLZJJb8-EBsdUf2IimbGFNkaONMwbZy2WNh5luqpkWk", base_url="http://localhost:12556/v1")

messages = [
    {"role": "system", "content": "你是一个AI助手。"},
    {"role": "user", "content": "9.11 and 9.8, which is greater?"}
]
# 非流式
# response = client.chat.completions.create(
#     model="deepseek-r1",
#     messages=messages,
# )
# reasoning_content = response.choices[0].message.reasoning_content
# content = response.choices[0].message.content
# print(f"reasoning_content: {reasoning_content}")
# print(f"content: {content}")

# 流式请求
stream = client.chat.completions.create(
    model="qwq-32b",
    messages=messages,
    stream=False
)


def handle_output(response):
    has_thinking = False
    print("=" * 80)
    reasoning_content = ""
    for chunk in response:
        delta_content = chunk.choices[0].delta.content
        if hasattr(chunk.choices[0].delta, "reasoning_content"):
            reasoning_content = chunk.choices[0].delta.reasoning_content
        if reasoning_content:
            if not has_thinking:
                print("<thinking>", flush=True)
            print(reasoning_content, end="", flush=True)
            has_thinking = True
        if delta_content:
            if has_thinking:
                print("</thinking>", flush=True)
            print(delta_content, end="", flush=True)
            has_thinking = False


handle_output(stream)
