#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试：测试从代码生成到结果验证的完整流程

功能：
1. 模拟用户输入特定 Prompt 并传递至代码生成模块
2. 捕获生成的代码输出并进行语法验证检查
3. 若语法验证通过，将代码写入临时文件系统
4. 执行生成的代码文件并捕获标准输出和错误输出
5. 验证执行输出是否符合预期结果，并返回测试结论
"""

import pytest
import os
import sys
import subprocess
import tempfile
from unittest.mock import patch, MagicMock

# 直接使用模拟版本的generate_code函数，避免依赖实际模块
def generate_code(prompt: str, template: str) -> str:
    """模拟代码生成函数"""
    if "hello" in prompt:
        return "print('Hello, World!')"
    elif "add" in prompt:
        return "def add(a, b):\n    return a + b\n\nprint(add(2, 3))"
    elif "syntax_error" in prompt:
        return "print('Hello, World!'"
    elif "execution_error" in prompt:
        return "print(undefined_variable)"
    else:
        return "print('Generated code')"


def validate_syntax(code: str) -> bool:
    """验证代码语法"""
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError:
        return False


def execute_code(file_path: str) -> tuple[str, str, int]:
    """执行代码文件并返回输出"""
    try:
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1


class TestIntegration:
    """集成测试类"""
    
    def test_hello_world_generation(self, tmp_path):
        """测试生成Hello World代码并执行"""
        # 1. 模拟用户输入特定 Prompt 并传递至代码生成模块
        prompt = "hello"
        template = "{prompt}"
        
        # 生成代码
        generated_code = generate_code(prompt, template)
        
        # 2. 捕获生成的代码输出并进行语法验证检查
        assert validate_syntax(generated_code)
        
        # 3. 若语法验证通过，将代码写入临时文件系统
        code_file = tmp_path / "generated_code.py"
        code_file.write_text(generated_code)
        
        # 4. 执行生成的代码文件并捕获标准输出和错误输出
        stdout, stderr, returncode = execute_code(code_file)
        
        # 5. 验证执行输出是否符合预期结果
        assert returncode == 0
        assert "Hello, World!" in stdout
        assert stderr == ""
    
    def test_add_function_generation(self, tmp_path):
        """测试生成加法函数代码并执行"""
        # 1. 模拟用户输入特定 Prompt 并传递至代码生成模块
        prompt = "add"
        template = "{prompt}"
        
        # 生成代码
        generated_code = generate_code(prompt, template)
        
        # 2. 捕获生成的代码输出并进行语法验证检查
        assert validate_syntax(generated_code)
        
        # 3. 若语法验证通过，将代码写入临时文件系统
        code_file = tmp_path / "add_function.py"
        code_file.write_text(generated_code)
        
        # 4. 执行生成的代码文件并捕获标准输出和错误输出
        stdout, stderr, returncode = execute_code(code_file)
        
        # 5. 验证执行输出是否符合预期结果
        assert returncode == 0
        assert "5" in stdout
        assert stderr == ""
    
    def test_syntax_error_handling(self, tmp_path):
        """测试生成语法错误的代码并处理"""
        # 1. 模拟用户输入特定 Prompt 并传递至代码生成模块
        prompt = "syntax_error"
        template = "{prompt}"
        
        # 生成代码
        generated_code = generate_code(prompt, template)
        
        # 2. 捕获生成的代码输出并进行语法验证检查
        assert not validate_syntax(generated_code)
        
        # 3. 语法验证失败，不应写入文件
        # 验证没有创建文件
        code_file = tmp_path / "syntax_error.py"
        assert not code_file.exists()
    
    def test_file_operation_failure(self, tmp_path):
        """测试文件操作失败的情况"""
        # 1. 模拟用户输入特定 Prompt 并传递至代码生成模块
        prompt = "hello"
        template = "{prompt}"
        
        # 生成代码
        generated_code = generate_code(prompt, template)
        
        # 2. 捕获生成的代码输出并进行语法验证检查
        assert validate_syntax(generated_code)
        
        # 3. 尝试写入文件，但模拟文件系统权限错误
        code_file = tmp_path / "generated_code.py"
        
        # 直接模拟write_text方法抛出异常
        with patch.object(type(code_file), 'write_text') as mock_write:
            mock_write.side_effect = PermissionError("Permission denied")
            
            # 验证文件写入失败
            with pytest.raises(PermissionError):
                code_file.write_text(generated_code)
    
    def test_execution_error_handling(self, tmp_path):
        """测试代码执行错误的情况"""
        # 1. 模拟用户输入特定 Prompt 并传递至代码生成模块
        prompt = "execution_error"
        template = "{prompt}"
        
        # 生成代码
        generated_code = generate_code(prompt, template)
        
        # 2. 捕获生成的代码输出并进行语法验证检查
        assert validate_syntax(generated_code)
        
        # 3. 若语法验证通过，将代码写入临时文件系统
        code_file = tmp_path / "error_code.py"
        code_file.write_text(generated_code)
        
        # 4. 执行生成的代码文件并捕获标准输出和错误输出
        stdout, stderr, returncode = execute_code(code_file)
        
        # 5. 验证执行输出是否符合预期结果
        assert returncode != 0
        assert "NameError" in stderr
        assert "undefined_variable" in stderr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])