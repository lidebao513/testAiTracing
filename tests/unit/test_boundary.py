#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 chunk_text 函数的边界条件

功能：
1. 测试最小分块场景
2. 测试恰好一块场景
3. 测试单块场景
4. 测试无重叠场景
5. 测试完全重叠场景
6. 测试空字符串输入
7. 测试空值输入
"""

import pytest
from text_chunk import chunk_text


class TestChunkTextBoundary:
    """测试 chunk_text 函数的边界条件"""
    
    def test_minimum_chunk_size(self):
        """测试最小分块场景：当chunk_size=1时"""
        text = "test"
        chunks = chunk_text(text, chunk_size=1, overlap=0)
        assert len(chunks) == 4
        assert chunks == ['t', 'e', 's', 't']
        
        # 测试带重叠的情况
        chunks_with_overlap = chunk_text(text, chunk_size=1, overlap=0)
        assert len(chunks_with_overlap) == 4
        assert chunks_with_overlap == ['t', 'e', 's', 't']
    
    def test_exact_chunk_size(self):
        """测试恰好一块场景：当chunk_size等于输入文本长度时"""
        text = "test"
        chunks = chunk_text(text, chunk_size=4)
        assert len(chunks) == 1
        assert chunks == ['test']
    
    def test_single_chunk(self):
        """测试单块场景：当chunk_size大于输入文本长度时"""
        text = "test"
        chunks = chunk_text(text, chunk_size=10)
        assert len(chunks) == 1
        assert chunks == ['test']
        
        # 测试不同的overlap值
        chunks_with_overlap = chunk_text(text, chunk_size=10, overlap=5)
        assert len(chunks_with_overlap) == 1
        assert chunks_with_overlap == ['test']
    
    def test_no_overlap(self):
        """测试无重叠场景：当overlap=0时"""
        text = "0123456789"
        chunks = chunk_text(text, chunk_size=3, overlap=0)
        assert len(chunks) == 4
        assert chunks == ['012', '345', '678', '9']
    
    def test_full_overlap(self):
        """测试完全重叠场景：当overlap等于chunk_size时"""
        text = "test"
        chunks = chunk_text(text, chunk_size=2, overlap=2)
        assert len(chunks) == 1
        assert chunks == ['test']
    
    def test_empty_string(self):
        """测试空字符串输入：当text=""时"""
        chunks = chunk_text("")
        assert len(chunks) == 0
        assert chunks == []
    
    def test_none_input(self):
        """测试空值输入：当text=None时"""
        chunks = chunk_text(None)
        assert len(chunks) == 0
        assert chunks == []
    
    def test_negative_overlap(self):
        """测试负重叠值"""
        text = "0123456789"
        chunks = chunk_text(text, chunk_size=3, overlap=-5)
        assert len(chunks) == 4
        assert chunks == ['012', '345', '678', '9']
    
    def test_negative_chunk_size(self):
        """测试负分块大小"""
        text = "test"
        chunks = chunk_text(text, chunk_size=-1, overlap=0)
        assert len(chunks) == 4
        assert chunks == ['t', 'e', 's', 't']