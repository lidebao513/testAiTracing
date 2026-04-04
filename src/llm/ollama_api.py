#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama API 调用模块

功能：
1. 调用 Ollama API 生成文本
2. 处理各种异常情况
"""

import time
import requests


# 自定义异常类
class ModelNotFoundError(Exception):
    """当请求的模型不存在时抛出"""
    pass


class APIError(Exception):
    """当API返回500状态码时抛出"""
    pass


class ParseError(Exception):
    """当API响应格式不符合预期时抛出"""
    pass


def call_ollama_api(prompt: str, timeout: int = 30) -> str:
    """
    调用 Ollama API
    
    Args:
        prompt: 提示文本
        timeout: 超时时间（秒）
    
    Returns:
        str: API 返回的文本
    
    Raises:
        TimeoutError: 当API连接超时时
        ModelNotFoundError: 当请求的模型不存在时
        APIError: 当API返回500状态码时
        ConnectionError: 当网络连接中断时
        ParseError: 当API响应格式不符合预期时
    """
    try:
        # 模拟API调用
        # 实际项目中这里会是真实的API调用
        # 这里我们模拟不同的异常场景
        if "timeout" in prompt:
            time.sleep(timeout + 1)  # 模拟超时
        elif "model_not_found" in prompt:
            raise ModelNotFoundError("请求的模型不存在")
        elif "api_error" in prompt:
            raise APIError("API返回500错误")
        elif "connection_error" in prompt:
            raise ConnectionError("网络连接中断")
        elif "parse_error" in prompt:
            raise ParseError("API响应格式错误")
        elif "unknown_error" in prompt:
            raise ValueError("未知错误")
        else:
            # 正常情况
            return "API 响应: " + prompt
    except TimeoutError:
        raise TimeoutError("API连接超时")
    except ModelNotFoundError:
        raise
    except APIError:
        raise
    except ConnectionError:
        raise
    except ParseError:
        raise
    except Exception as e:
        raise Exception(f"未知错误: {str(e)}")