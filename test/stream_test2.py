# -*- coding: utf-8 -*-
# @Time    : 2024/12/20 14:21
# @Author  : codewen77
import json

import requests

url = "http://localhost:12555/stream"
headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer yLZJJb8-EBsdUf2IimbGFNkaONMwbZy2WNh5luqpkWk",
}

data = {
    "user_input": [{"role": "user", "content": "请写一篇关于宇宙的奥秘的文章，100字"}]
}

# 发起POST请求，stream=True 表示流式处理响应
response = requests.post(url, headers=headers, json=data, stream=True)

# 检查响应是否有效
if response.status_code == 200:
    # 打印每一块返回的二进制数据，解码为字符串并输出
    for chunk in response.iter_lines(decode_unicode=True):
        if chunk:  # 过滤掉keep-alive新行
            json_data = json.loads(chunk)
            # 处理每个JSON对象
            print(json_data)
