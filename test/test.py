# -*- coding: utf-8 -*-
# @Time    : 2025/1/2 9:52
# @Author  : codewen77
# -*- coding: utf-8 -*-
# @Time    : 2025/1/2 9:24
# @Author  : codewen77
from openai import OpenAI
import time

# 初始化客户端
# 6fcf3eaf8297ab66c9bc76e54920c8ec
# yLZJJb8-EBsdUf2IimbGFNkaONMwbZy2WNh5luqpkWk
client = OpenAI(api_key="yLZJJb8-EBsdUf2IimbGFNkaONMwbZy2WNh5luqpkWk", base_url="http://localhost:12556/v1")

# 记录开始时间
start_time = time.time()

# 发送请求
response = client.chat.completions.create(
    model="deepseek-v3",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "请讲一个笑话，50字。"},
    ],
    stream=False
)

# 记录结束时间
end_time = time.time()

# 提取生成的文本和 token 数量
if response.choices[0].message.reasoning_content:
    reasoning_text = response.choices[0].message.reasoning_content
    print(reasoning_text)
generated_text = response.choices[0].message.content
completion_tokens = response.usage.completion_tokens  # 生成的 token 数量

# 计算推理速度
total_time = end_time - start_time
speed = completion_tokens / total_time

print(f"生成的文本: {generated_text}")
print(f"生成的 token 数量: {completion_tokens}")
print(f"总时间: {total_time:.2f} 秒")
print(f"推理速度: {speed:.2f} token/s")