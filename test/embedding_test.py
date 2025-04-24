# -*- coding: utf-8 -*-
# @Time    : 2024/12/26 16:12
# @Author  : codewen77
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:12556/v1",
    api_key='yLZJJb8-EBsdUf2IimbGFNkaONMwbZy2WNh5luqpkWk',
)

response = client.embeddings.create(
    model="bge-m3",
    input="The food was delicious and the waiter..."
)
embedding = response.data[0].embedding
print("Embedding vector:", embedding)

