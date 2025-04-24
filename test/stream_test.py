import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI()

# 外部 API 的 URL
EXTERNAL_API_URL = "https://aichat.dahuatech.com/api/conversation/qwen"  # 替换为实际的 API URL


# 获取 token
def get_token():
    headers = {'Authorization': 'Basic NDQ0MjY6MG9rbShJSk4mKigp'}
    return requests.post('https://aichat.dahuatech.com/uac/login/token', headers=headers).json()['result'][
        'access_token']


# 设置请求头
headers = {'Authorization': f'Bearer {get_token()}'}


# 同步请求并流式返回数据
def stream_external_api_data(question):
    # 使用 requests 发送 POST 请求并启用流式处理
    with requests.post(EXTERNAL_API_URL, headers=headers, json=question, stream=True) as response:
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from external API")

        # 流式处理每个返回的数据块
        for chunk in response.iter_lines():
            if chunk:
                # 解码bytes为字符串
                if isinstance(chunk, bytes):
                    decoded_chunk = chunk.decode('utf-8', errors='ignore')
                else:
                    decoded_chunk = chunk

                # 去掉 'data:' 前缀
                if decoded_chunk.startswith('data:'):
                    decoded_chunk = decoded_chunk[5:].strip()
                else:
                    print(f"数据块没有 'data:' 前缀，内容: {decoded_chunk}")

                # 解析JSON
                try:
                    resp_json = json.loads(decoded_chunk)
                    content = resp_json.get("content", "")
                    yield json.dumps({"content": content}, ensure_ascii=False) + '\n'  # 每次返回当前数据块
                except json.JSONDecodeError as e:
                    print(f"JSON解析失败，内容: {decoded_chunk}, 错误: {e}")
                    raise HTTPException(status_code=500, detail=f"JSON解析失败: {e}")


@app.post("/stream")
async def stream_data():
    messages = [{'role': 'system', 'content': '你是一个非常出色的小说家'},
                {'role': 'user', 'content': '请写一篇文章关于宇宙的奥秘，1000字左右'}]
    question = {
        "messages": messages,
        "chatOptions": {
            "temperature": 0.7,
            "topP": 0.9,
            "presencePenalty": 0,
            "frequencyPenalty": 0
        },
        "stream": True,
        "ignoreStatistics": "ignore",
        "userId": "44426"
    }

    # 通过 StreamingResponse 返回流式数据
    return StreamingResponse(stream_external_api_data(question), media_type="application/json")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=12555)
