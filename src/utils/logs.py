# -*- coding: utf-8 -*-
# @Time    : 2024/10/30 17:17
# @Author  : codewen77
import logging
import os

from src.config.env import LOGGER_PATH

log_dir = LOGGER_PATH
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 创建一个 logger 对象
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

# 检查处理器是否已存在，以避免重复添加
if not logger.handlers:
    # 创建一个文件处理器，并设置编码为UTF-8
    file_handler = logging.FileHandler(f'{log_dir}/app.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 创建一个控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 创建一个格式化器
    formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')

    # 将格式化器添加到处理器中
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 将处理器添加到 logger 对象中
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_user_model_interaction(task, user_input, model_output):
    """用于记录五个模型接口的输入和输出"""
    save_path = f'{log_dir}/{task}.txt'
    with open(save_path, 'a', encoding='utf-8') as f:
        one_json = {"input": user_input, "output": model_output}
        f.write(f'{one_json}\n')
        logger.info("Logged user input and model output.")
