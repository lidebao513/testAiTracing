#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入解析模块

功能：
1. 解析用户输入的命令格式
2. 支持参数解析和类型转换
3. 处理各种输入格式和边界情况
"""


def parse_user_input(user_input: str) -> dict:
    """
    解析用户输入的命令格式
    
    输入格式示例："generate:model=deepseek, temperature=0.7, max_tokens=1000"
    
    Args:
        user_input: 用户输入的字符串
    
    Returns:
        dict: 解析后的参数字典
    
    Raises:
        ValueError: 当输入格式错误时
    """
    # 处理空字符串输入
    if not user_input:
        return {}
    
    # 检查输入长度限制（假设最大长度为1000）
    if len(user_input) > 1000:
        raise ValueError("输入字符串长度超过限制")
    
    # 解析命令和参数部分
    if ':' not in user_input:
        raise ValueError("输入格式错误：缺少冒号分隔符")
    
    # 分割命令和参数
    command_part, params_part = user_input.split(':', 1)
    
    # 初始化结果字典，包含命令部分
    result = {'command': command_part.strip()}
    
    # 处理参数部分
    if params_part:
        # 更复杂的参数解析，处理包含逗号的引号值
        params = []
        current_param = []
        in_quotes = False
        quote_char = None
        
        for char in params_part:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_param.append(char)
            elif char == quote_char and in_quotes:
                in_quotes = False
                current_param.append(char)
            elif char == ',' and not in_quotes:
                # 分割参数
                param_str = ''.join(current_param).strip()
                if param_str:
                    params.append(param_str)
                current_param = []
            else:
                current_param.append(char)
        
        # 添加最后一个参数
        if current_param:
            param_str = ''.join(current_param).strip()
            if param_str:
                params.append(param_str)
        
        for param in params:
            # 检查参数格式
            if '=' not in param:
                raise ValueError(f"参数格式错误：{param}")
            
            # 分割参数名和值
            key, value = param.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # 处理引号包围的值
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            
            # 尝试类型转换
            try:
                # 尝试转换为整数
                if value.isdigit():
                    value = int(value)
                # 尝试转换为浮点数
                elif '.' in value and all(c.isdigit() or c == '.' for c in value):
                    value = float(value)
            except (ValueError, TypeError):
                # 保持为字符串类型
                pass
            
            result[key] = value
    
    return result