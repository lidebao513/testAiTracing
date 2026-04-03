#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 call_ollama_api 函数的异常处理机制

功能：
1. 测试各种异常场景
2. 验证异常类型和错误消息
3. 使用 mock 技术模拟不同的异常情况
"""

import pytest
from unittest.mock import patch, MagicMock
from ollama_api import call_ollama_api, ModelNotFoundError, APIError, ParseError


class TestOllamaAPIExceptionHandling:
    """测试 call_ollama_api 函数的异常处理"""
    
    def test_normal_case(self):
        """测试正常情况"""
        result = call_ollama_api("Hello")
        assert result == "API 响应: Hello"
    
    def test_timeout_error(self):
        """测试场景1（连接超时）：模拟API连接超时情况"""
        # 使用patch模拟time.sleep函数，使其立即抛出TimeoutError
        with patch('ollama_api.time.sleep') as mock_sleep:
            mock_sleep.side_effect = TimeoutError
            
            # 验证是否正确抛出TimeoutError，并检查错误消息内容
            with pytest.raises(TimeoutError) as excinfo:
                call_ollama_api("timeout", timeout=1)
            assert "API连接超时" in str(excinfo.value)
    
    def test_model_not_found_error(self):
        """测试场景2（模型不存在）：模拟请求不存在的模型"""
        # 验证是否正确抛出ModelNotFoundError，并检查错误消息内容
        with pytest.raises(ModelNotFoundError) as excinfo:
            call_ollama_api("model_not_found")
        assert "请求的模型不存在" in str(excinfo.value)
    
    def test_api_error(self):
        """测试场景3（API返回500）：模拟API返回500状态码"""
        # 验证是否正确抛出APIError，并检查错误消息内容
        with pytest.raises(APIError) as excinfo:
            call_ollama_api("api_error")
        assert "API返回500错误" in str(excinfo.value)
    
    def test_connection_error(self):
        """测试场景4（网络中断）：模拟网络连接中断情况"""
        # 验证是否正确抛出ConnectionError，并检查错误消息内容
        with pytest.raises(ConnectionError) as excinfo:
            call_ollama_api("connection_error")
        assert "网络连接中断" in str(excinfo.value)
    
    def test_parse_error(self):
        """测试场景5（响应格式错误）：模拟API返回格式错误的响应"""
        # 验证是否正确抛出ParseError，并检查错误消息内容
        with pytest.raises(ParseError) as excinfo:
            call_ollama_api("parse_error")
        assert "API响应格式错误" in str(excinfo.value)
    
    def test_unknown_error(self):
        """测试未知错误情况"""
        # 验证是否正确抛出Exception，并检查错误消息内容
        with pytest.raises(Exception) as excinfo:
            call_ollama_api("unknown_error")
        assert "未知错误" in str(excinfo.value)