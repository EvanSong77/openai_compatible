# -*- coding: utf-8 -*-
# @Time    : 2024/10/30 17:10
# @Author  : codewen77
from typing import Optional, Literal

from pydantic import BaseModel, conlist


class Message(BaseModel):
    role: str
    content: str
    reasoning_content: Optional[str] = None
    tool_calls: Optional[list] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: conlist(Message)
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stream: bool = False
    tools: Optional[list] = None


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: conlist(Choice)
    usage: Optional[dict] = None


class Choice2(BaseModel):
    index: int
    delta: Message
    logprobs: Optional[object] = None
    finish_reason: Optional[str] = None


class ChatCompletionChunkResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: conlist(Choice2)
    usage: Optional[dict] = None
    service_tier: Optional[str] = None
    system_fingerprint: str
