# -*- coding: utf-8 -*-
# @Time    : 2025/4/23 14:00
# @Author  : EvanSong
import shortuuid


def random_uuid(length=22) -> str:
    return str(shortuuid.random(length=length))
