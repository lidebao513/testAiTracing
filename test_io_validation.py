#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 parse_user_input 函数的输入输出验证功能

功能：
1. 测试正常输入情况
2. 测试边界输入情况
3. 测试格式错误情况
4. 测试类型转换情况
5. 测试特殊字符情况
"""

import unittest
from input_parser import parse_user_input


class TestParseUserInput(unittest.TestCase):
    """测试 parse_user_input 函数"""
    
    def test_parse_normal_input(self):
        """测试正常输入"""
        # 测试包含多个参数的标准输入格式
        user_input = "generate:model=deepseek, temperature=0.7, max_tokens=1000"
        result = parse_user_input(user_input)
        
        # 验证返回的字典包含所有正确解析的键值对
        self.assertEqual(result['command'], 'generate')
        self.assertEqual(result['model'], 'deepseek')
        self.assertEqual(result['temperature'], 0.7)
        self.assertEqual(result['max_tokens'], 1000)
        
        # 验证参数值类型
        self.assertIsInstance(result['model'], str)
        self.assertIsInstance(result['temperature'], float)
        self.assertIsInstance(result['max_tokens'], int)
    
    def test_parse_boundary_input(self):
        """测试边界输入"""
        # 测试空字符串输入
        empty_input = ""
        result = parse_user_input(empty_input)
        self.assertEqual(result, {})
        
        # 测试接近最大长度限制的输入字符串
        # 创建一个长度接近1000的输入
        long_param = 'x' * 950
        long_input = f"generate:param={long_param}"
        result = parse_user_input(long_input)
        self.assertEqual(result['command'], 'generate')
        self.assertEqual(result['param'], long_param)
        
        # 测试超过长度限制的输入
        very_long_param = 'x' * 990
        very_long_input = f"generate:param={very_long_param}"
        with self.assertRaises(ValueError) as context:
            parse_user_input(very_long_input)
        self.assertIn("输入字符串长度超过限制", str(context.exception))
    
    def test_parse_format_errors(self):
        """测试格式错误"""
        # 测试缺少冒号的输入
        no_colon_input = "generate model=deepseek"
        with self.assertRaises(ValueError) as context:
            parse_user_input(no_colon_input)
        self.assertIn("缺少冒号分隔符", str(context.exception))
        
        # 测试参数格式错误的输入（使用破折号而不是等号）
        bad_param_input = "generate:model=deepseek, temperature-0.7"
        with self.assertRaises(ValueError) as context:
            parse_user_input(bad_param_input)
        self.assertIn("参数格式错误", str(context.exception))
    
    def test_parse_type_conversion(self):
        """测试类型转换"""
        # 测试包含数字参数的输入
        numeric_input = "generate:temperature=0.7, max_tokens=1000, batch_size=5"
        result = parse_user_input(numeric_input)
        
        # 验证数值参数被正确转换为相应的Python类型
        self.assertIsInstance(result['temperature'], float)
        self.assertIsInstance(result['max_tokens'], int)
        self.assertIsInstance(result['batch_size'], int)
        
        # 验证值的正确性
        self.assertEqual(result['temperature'], 0.7)
        self.assertEqual(result['max_tokens'], 1000)
        self.assertEqual(result['batch_size'], 5)
    
    def test_parse_special_characters(self):
        """测试特殊字符"""
        # 测试包含中文字符的输入
        chinese_input = "生成:模型=深度求索, 温度=0.7"
        result = parse_user_input(chinese_input)
        self.assertEqual(result['command'], '生成')
        self.assertEqual(result['模型'], '深度求索')
        self.assertEqual(result['温度'], 0.7)
        
        # 测试包含转义字符的输入
        quoted_input = 'generate:prompt="Hello, world!", temperature=0.7'
        result = parse_user_input(quoted_input)
        self.assertEqual(result['command'], 'generate')
        self.assertEqual(result['prompt'], 'Hello, world!')
        self.assertEqual(result['temperature'], 0.7)
        
        # 测试包含单引号的输入
        single_quoted_input = "generate:prompt='Hello, world!', temperature=0.7"
        result = parse_user_input(single_quoted_input)
        self.assertEqual(result['command'], 'generate')
        self.assertEqual(result['prompt'], 'Hello, world!')
        self.assertEqual(result['temperature'], 0.7)


if __name__ == '__main__':
    unittest.main()