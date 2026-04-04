#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 validate_environment 函数的分支覆盖率

功能：
1. 测试 validate_environment 函数的各种分支条件
2. 确保每个分支都被覆盖
3. 使用 pytest.mark.parametrize 进行参数化测试
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.evaluation.environment_validator import validate_environment


class TestValidateEnvironment:
    """测试 validate_environment 函数"""
    
    @pytest.mark.parametrize(
        "config, expected",
        [
            # 测试用例1：验证当config参数为空字典时，函数应返回False
            ({}, False),
            # 测试用例5：验证当所有条件都满足时，函数应返回True
            ({
                'venv_path': 'venv',
                'required_deps': ['os', 'sys']
            }, True)
        ],
        ids=[
            "空配置字典",
            "所有条件都满足"
        ]
    )
    def test_basic_cases(self, config, expected):
        """测试基本情况"""
        result = validate_environment(config)
        assert result == expected
    
    def test_python_version(self):
        """测试Python版本分支"""
        # 保存原始版本信息
        original_version = sys.version_info
        
        try:
            # 模拟Python版本低于3.10
            # 注意：这只是模拟，实际上无法修改sys.version_info
            # 我们通过修改函数行为来测试这个分支
            # 由于无法直接修改sys.version_info，我们需要使用monkey patching
            import environment_validator
            original_version_check = environment_validator.sys.version_info
            
            # 模拟版本检查函数
            def mock_version_check():
                return (3, 9, 0, 'final', 0)
            
            # 应用猴子补丁
            environment_validator.sys.version_info = (3, 9, 0, 'final', 0)
            
            # 测试版本低于3.10的情况
            config = {
                'venv_path': 'venv',
                'required_deps': ['os', 'sys']
            }
            result = validate_environment(config)
            assert result is False
        finally:
            # 恢复原始版本信息
            import environment_validator
            environment_validator.sys.version_info = original_version
    
    def test_venv_not_exists(self):
        """测试虚拟环境不存在的情况"""
        # 使用一个不存在的虚拟环境路径
        config = {
            'venv_path': 'non_existent_venv',
            'required_deps': ['os', 'sys']
        }
        result = validate_environment(config)
        assert result is False
    
    def test_missing_dependency(self):
        """测试依赖缺失的情况"""
        # 使用一个不存在的依赖
        config = {
            'venv_path': 'venv',
            'required_deps': ['os', 'sys', 'non_existent_module_12345']
        }
        result = validate_environment(config)
        assert result is False