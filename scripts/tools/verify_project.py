#!/usr/bin/env python3
"""
项目文件整理后功能验证脚本
用于验证项目文件整理后所有功能是否正常
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def verify_directory_structure():
    """验证目录结构"""
    print("=" * 60)
    print("1. 目录结构验证")
    print("=" * 60)
    
    required_dirs = [
        "src/core",
        "src/llm",
        "src/evaluation",
        "src/utils",
        "tests/unit",
        "tests/integration",
        "config/env",
        "config/pytest",
        "docs/guides",
        "docs/manuals",
        "scripts/setup",
        "scripts/tools",
        "logs",
        "temp"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} (缺失)")
            all_exist = False
    
    return all_exist

def verify_files():
    """验证关键文件"""
    print("\n" + "=" * 60)
    print("2. 关键文件验证")
    print("=" * 60)
    
    required_files = [
        "src/core/code_generator.py",
        "src/core/input_parser.py",
        "src/core/text_chunk.py",
        "src/llm/local_llm_config.py",
        "src/llm/ollama_api.py",
        "src/evaluation/environment_validator.py",
        "src/utils/retry_decider.py",
        "config/env/.env.example",
        "config/pytest/pytest.ini",
        "docs/guides/README.md",
        "requirements.txt"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (缺失)")
            all_exist = False
    
    return all_exist

def verify_imports():
    """验证模块导入"""
    print("\n" + "=" * 60)
    print("3. 模块导入验证")
    print("=" * 60)
    
    imports_to_test = [
        ("src.core.code_generator", "generate_code"),
        ("src.core.input_parser", "parse_user_input"),
        ("src.core.text_chunk", "chunk_text"),
        ("src.llm.local_llm_config", "LocalLLMConfig"),
        ("src.llm.ollama_api", "call_ollama_api"),
        ("src.evaluation.environment_validator", "validate_environment"),
        ("src.utils.retry_decider", "should_retry"),
    ]
    
    all_success = True
    for module_name, function_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[function_name])
            if function_name:
                getattr(module, function_name)
            print(f"✓ {module_name}.{function_name}")
        except Exception as e:
            print(f"✗ {module_name}.{function_name}: {str(e)}")
            all_success = False
    
    return all_success

def verify_functionality():
    """验证核心功能"""
    print("\n" + "=" * 60)
    print("4. 核心功能验证")
    print("=" * 60)
    
    try:
        # 测试代码生成
        from src.core.code_generator import generate_code
        result = generate_code("测试", "{prompt}")
        if result:
            print("✓ 代码生成功能正常")
        else:
            print("✗ 代码生成功能异常")
            return False
    except Exception as e:
        print(f"✗ 代码生成功能异常: {e}")
        return False
    
    try:
        # 测试输入解析
        from src.core.input_parser import parse_user_input
        result = parse_user_input("test:value")
        if result:
            print("✓ 输入解析功能正常")
        else:
            print("✗ 输入解析功能异常")
            return False
    except Exception as e:
        print(f"✗ 输入解析功能异常: {e}")
        return False
    
    try:
        # 测试文本分块
        from src.core.text_chunk import chunk_text
        result = chunk_text("测试文本", chunk_size=10)
        if result:
            print("✓ 文本分块功能正常")
        else:
            print("✗ 文本分块功能异常")
            return False
    except Exception as e:
        print(f"✗ 文本分块功能异常: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("项目文件整理后功能验证")
    print("=" * 60)
    
    # 执行各项验证
    dir_ok = verify_directory_structure()
    files_ok = verify_files()
    imports_ok = verify_imports()
    func_ok = verify_functionality()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    print(f"目录结构: {'✓ 通过' if dir_ok else '✗ 失败'}")
    print(f"关键文件: {'✓ 通过' if files_ok else '✗ 失败'}")
    print(f"模块导入: {'✓ 通过' if imports_ok else '✗ 失败'}")
    print(f"核心功能: {'✓ 通过' if func_ok else '✗ 失败'}")
    print("=" * 60)
    
    if dir_ok and files_ok and imports_ok and func_ok:
        print("\n✓ 所有验证通过，项目文件整理成功！")
        return 0
    else:
        print("\n✗ 部分验证失败，请检查上述问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
