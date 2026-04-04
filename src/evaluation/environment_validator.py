#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境验证模块

功能：
1. 验证环境配置是否满足要求
2. 检查Python版本
3. 检查虚拟环境是否存在
4. 检查依赖是否完整
"""

import os
import sys


def validate_environment(config: dict) -> bool:
    """
    验证环境配置是否满足要求
    
    Args:
        config: 环境配置字典
    
    Returns:
        bool: 环境是否满足要求
    """
    # 检查config参数是否为空字典
    if not config:
        return False
    
    # 检查Python版本是否低于3.10
    if sys.version_info < (3, 10):
        return False
    
    # 检查虚拟环境是否存在
    venv_path = config.get('venv_path', 'venv')
    if not os.path.exists(venv_path):
        return False
    
    # 检查依赖是否缺失
    required_deps = config.get('required_deps', [])
    for dep in required_deps:
        try:
            __import__(dep)
        except ImportError:
            return False
    
    # 所有条件都满足
    return True