#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 generate_code 函数的语句覆盖率

功能：
1. 测试 generate_code 函数的各种输入情况
2. 确保每一行可执行代码都被覆盖
3. 生成 HTML 格式的覆盖率报告
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.code_generator import generate_code


class TestGenerateCode:
    """测试 generate_code 函数"""
    
    def test_empty_prompt(self):
        """测试空提示的情况"""
        result = generate_code("", "# 模板")
        assert result == "# 错误：提示为空"
    
    def test_empty_template(self):
        """测试空模板的情况"""
        result = generate_code("生成一个函数", "")
        assert result == "# 错误：模板为空"
    
    def test_function_prompt(self):
        """测试函数提示的情况"""
        result = generate_code("生成一个函数", "# 代码模板\n{prompt}")
        assert "# 函数定义示例" in result
        assert "def example_function()" in result
    
    def test_class_prompt(self):
        """测试类提示的情况"""
        result = generate_code("生成一个类", "# 代码模板\n{prompt}")
        assert "# 类定义示例" in result
        assert "class ExampleClass" in result
    
    def test_test_prompt(self):
        """测试测试提示的情况"""
        result = generate_code("生成测试代码", "# 代码模板\n{prompt}")
        assert "# 测试代码示例" in result
        assert "def test_example()" in result
    
    def test_generic_prompt(self):
        """测试通用提示的情况"""
        result = generate_code("生成代码", "# 代码模板\n{prompt}")
        assert "# 通用代码示例" in result
        assert 'print("Hello, World!")' in result
    
    def test_function_english_prompt(self):
        """测试英文函数提示的情况"""
        result = generate_code("generate a function", "# 代码模板\n{prompt}")
        assert "# 函数定义示例" in result
        assert "def example_function()" in result
    
    def test_class_english_prompt(self):
        """测试英文类提示的情况"""
        result = generate_code("generate a class", "# 代码模板\n{prompt}")
        assert "# 类定义示例" in result
        assert "class ExampleClass" in result
    
    def test_test_english_prompt(self):
        """测试英文测试提示的情况"""
        result = generate_code("generate test code", "# 代码模板\n{prompt}")
        assert "# 测试代码示例" in result
        assert "def test_example()" in result
    
    def test_exception_handling(self):
        """测试异常处理的情况"""
        # 测试异常处理逻辑
        result = generate_code("测试异常", "# 模板\n{prompt}")
        assert "# 生成代码时出错" in result
        assert "模拟异常" in result



