#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重试决策模块

功能：
1. 根据错误码、重试次数和超时状态决定是否应该重试
2. 实现复合条件表达式：(error_code in [500, 503]) and (retry_count < 3) and (not timeout)
"""


def should_retry(error_code: int, retry_count: int, timeout: bool) -> bool:
    """
    决定是否应该重试操作
    
    Args:
        error_code: 错误码
        retry_count: 已重试次数
        timeout: 是否超时
    
    Returns:
        bool: 是否应该重试
    """
    return (error_code in [500, 503]) and (retry_count < 3) and (not timeout)