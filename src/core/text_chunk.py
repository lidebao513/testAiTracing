#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本分块模块

功能：
1. 将文本分割成指定大小的块
2. 支持块之间的重叠
3. 处理各种边界情况
"""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    文本分块函数
    
    Args:
        text: 要分块的文本
        chunk_size: 每个块的大小，默认为500
        overlap: 块之间的重叠大小，默认为50
    
    Returns:
        list: 分块后的文本列表
    """
    # 处理空字符串输入
    if not text:
        return []
    
    # 处理text为None的情况
    if text is None:
        return []
    
    # 确保chunk_size至少为1
    if chunk_size < 1:
        chunk_size = 1
    
    # 确保overlap不小于0
    if overlap < 0:
        overlap = 0
    
    # 确保overlap不大于chunk_size
    if overlap >= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        # 确保最后一块不会超出文本长度
        if end > text_length:
            end = text_length
        
        # 添加当前块
        chunks.append(text[start:end])
        
        # 计算下一块的起始位置
        start += chunk_size - overlap
        
        # 避免无限循环
        if start >= text_length:
            break
    
    return chunks