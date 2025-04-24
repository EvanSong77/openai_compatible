from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:12555/v1",
    api_key='yLZJJb8-EBsdUf2IimbGFNkaONMwbZy2WNh5luqpkWk',
)
messages = [
    {"role": "system", "content": "你是一个能干的助手."},
    {"role": "user", "content": "请写一篇文章关于宇宙的奥秘，100字左右?"},
]
stream = True
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    stream=stream
)
if stream:
    # 流式响应
    for chunk in response:
        # 每个chunk是一个部分的响应内容
        print(chunk.choices[0].delta.content, end="", flush=True)

    print()
else:
    # 非流式响应
    print(response)

# import json
# import requests
#
# url = "http://localhost:12555/v1/chat/completions"
# headers = {
#     "accept": "application/json",
#     "Content-Type": "application/json",
#     "Authorization": "Bearer yLZJJb8-EBsdUf2IimbGFNkaONMwbZy2WNh5luqpkWk"
# }
#
# data = {
#     "model": "qwen-2.5",
#     "messages": [{"role": "user", "content": "请写一篇文章关于宇宙的奥秘，1000字左右"}],
#     "temperature": 0.7,
#     "top_p": 0.9,
#     "stream": True
# }
#
# response = requests.post(url, headers=headers, json=data, stream=True)
#
# for chunk in response.iter_lines(decode_unicode=True):
#     if not chunk.startswith("data:"):
#         continue
#     data = json.loads(chunk[6:])
#     if 'content' in data["choices"][0]["delta"]:
#         print(data["choices"][0]["delta"]['content'], end='', flush=True)
#
# print()
