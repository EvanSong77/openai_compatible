# -*- coding: utf-8 -*-
# @Time    : 2024/10/30 17:13
# @Author  : codewen77
import json
import os

from dotenv import load_dotenv

load_dotenv()
BEARER = os.environ.get("BEARER")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL")
LOGGER_PATH = os.environ.get("LOGGER_PATH")
EMBEDDING_BASE_URL = os.environ.get("EMBEDDING_BASE_URL")
EMBEDDING_BEARER = os.environ.get("EMBEDDING_BEARER")
RERANKER_BASE_URL = os.environ.get("RERANKER_BASE_URL")
RERANKER_BEARER = os.environ.get("RERANKER_BEARER")

INTERNAL_MODEL = eval(os.environ.get("INTERNAL_MODEL"))
INTERNAL_BASE_URL = os.environ.get("INTERNAL_BASE_URL")
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY")
INTERNAL_MODEL_PATH = os.environ.get("INTERNAL_MODEL_PATH")
with open(INTERNAL_MODEL_PATH, "r", encoding="utf-8") as fp:
    INTERNAL_MODEL_DICT = json.load(fp)
