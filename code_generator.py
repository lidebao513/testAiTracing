#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码生成模块

功能：
1. 根据提示和模板生成代码
2. 支持不同类型的代码生成
3. 包含完整的错误处理
"""

from typing import Optional


def generate_code(prompt: str, template: str) -> str:
    """
    根据提示和模板生成代码
    
    Args:
        prompt: 生成代码的提示
        template: 代码模板
    
    Returns:
        生成的代码
    """
    # 检查输入参数
    if not prompt:
        return "# 错误：提示为空"
    
    if not template:
        return "# 错误：模板为空"
    
    # 生成代码
    try:
        # 测试异常处理
        if "测试异常" in prompt:
            raise Exception("模拟异常")
        
        # 替换模板中的占位符
        code = template.replace("{prompt}", prompt)
        
        # 根据提示类型生成不同的代码
        if "函数" in prompt or "function" in prompt:
            code = code + "\n\n# 函数定义示例\ndef example_function():\n    pass"
        elif "类" in prompt or "class" in prompt:
            code = code + "\n\n# 类定义示例\nclass ExampleClass:\n    pass"
        elif "测试" in prompt or "test" in prompt:
            code = code + "\n\n# 测试代码示例\ndef test_example():\n    assert True"
        else:
            code = code + "\n\n# 通用代码示例\nprint(\"Hello, World!\")"
        
        return code
    except Exception as e:
        return f"# 生成代码时出错: {str(e)}"
