# -*- coding: utf-8 -*-
# @Time    : 2024/10/30 17:11
# @Author  : codewen77
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from openai import OpenAIError, AsyncOpenAI, OpenAI

import src.model.openai_schema as protocol
from src.config.env import INTERNAL_MODEL, INTERNAL_API_KEY, INTERNAL_BASE_URL, INTERNAL_MODEL_DICT
from src.model.chat_model import ChatCompletionResponse, Message, Choice
from src.utils.LLM import ChatModel
from src.utils.bearer import verify_token

chat_router = APIRouter()


def parse_openai_response_to_protocol(response) -> protocol.ChatCompletionResponse:
    """
    Convert OpenAI completion response to protocol.ChatCompletionResponse.
    Handles both OpenAI response and protocol's expected fields.
    """
    # OpenAI v1 responses have choices: [{'message': {'role': ..., 'content': ...}, ...}]
    try:
        # For OpenAI 1.x style
        choices = []
        for idx, ch in enumerate(response.choices):
            finish_reason = getattr(ch, "finish_reason", None)
            msg = getattr(ch, "message", None)
            if msg is None:
                # Sometimes response.content may exist (older/compat OpenAI clients)
                msg = {"role": "assistant", "content": getattr(response, "content", None)}
            else:
                msg = msg.model_dump() if hasattr(msg, "model_dump") else dict(msg)
            tool_calls = msg.get("tool_calls")
            if not isinstance(tool_calls, list):
                tool_calls = []
            choices.append(protocol.ChatCompletionResponseChoice(
                index=idx,
                message=protocol.ChatMessage(
                    role=msg.get("role", "assistant"),
                    content=msg.get("content", ""),
                    tool_calls=tool_calls,
                ),
                finish_reason=finish_reason
            ))
        usage = getattr(response, "usage", None)
        if usage:
            usage = protocol.UsageInfo(
                prompt_tokens=getattr(usage, "prompt_tokens", 0),
                total_tokens=getattr(usage, "total_tokens", 0),
                completion_tokens=getattr(usage, "completion_tokens", 0)
            )
        else:
            usage = protocol.UsageInfo()
        return protocol.ChatCompletionResponse(
            model=getattr(response, "model", ""),
            choices=choices,
            usage=usage
        )
    except Exception as e:
        raise RuntimeError(f"Failed to parse OpenAI response: {e}")


@chat_router.post("/chat/completions")
async def chat_completions(request: protocol.ChatCompletionRequest, token: str = Depends(verify_token)):
    # TODO
    print("=" * 50)
    print(request.messages)
    print("=" * 50)
    try:
        if request.stream:
            if request.model in INTERNAL_MODEL:
                client = AsyncOpenAI(
                    api_key=INTERNAL_API_KEY,
                    base_url=f"{INTERNAL_BASE_URL}/{INTERNAL_MODEL_DICT[request.model]}/v1")

                # 使用 await 创建异步流
                stream = await client.chat.completions.create(
                    model=request.model,
                    messages=request.messages,
                    tools=request.tools,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    stream=True
                )

                # 定义异步生成器
                async def generate():
                    async for chunk in stream:  # 正确遍历异步流
                        yield f"data: {chunk.model_dump_json()}\n\n"  # 确保符合SSE格式

                # 返回流式响应
                return StreamingResponse(generate(), media_type="text/event-stream")
            else:
                temperature = request.temperature or None
                top_p = request.top_p or None
                model = ChatModel(request.model, stream=request.stream)
                # 返回流式响应
                return StreamingResponse(model(request.messages, temperature=temperature, top_p=top_p),
                                         media_type="text/event-stream")

        else:
            if request.model in INTERNAL_MODEL:
                client = OpenAI(api_key=INTERNAL_API_KEY,
                                base_url=f"{INTERNAL_BASE_URL}/{INTERNAL_MODEL_DICT[request.model]}/v1")
                response = client.chat.completions.create(
                    model=request.model,
                    messages=request.messages,
                    tools=request.tools,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    stream=False
                )

                protocol_response = parse_openai_response_to_protocol(response)
                return JSONResponse(content=protocol_response.model_dump())
            else:
                temperature = request.temperature or None
                top_p = request.top_p if request.top_p else None
                model = ChatModel(request.model, stream=request.stream)
                response_generator = model(request.messages, temperature=temperature, top_p=top_p)
                if isinstance(response_generator, dict):
                    message = Message(role="assistant", content=response_generator['content'],
                                      reasoning_content=response_generator['reasoning_content'])
                else:
                    message = Message(role="assistant", content=response_generator)
                response = ChatCompletionResponse(
                    id="chatcmpl-12345",
                    object="chat.completion",
                    created=1690000000,
                    model=request.model,
                    choices=[
                        Choice(
                            index=0,
                            message=message,
                            finish_reason="stop"
                        )
                    ],
                    usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                )
                # TODO
                print(response_generator)
                return response
    except OpenAIError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
