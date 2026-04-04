#!/usr/bin/env python3
"""
导入路径验证脚本
用于验证项目文件整理后所有模块的导入路径是否正确
"""

import sys
import importlib
from typing import List, Tuple

def verify_imports() -> List[Tuple[str, bool, str]]:
    """验证所有模块导入"""
    
    imports_to_test = [
        # 核心模块
        ("src.core.code_generator", "generate_code"),
        ("src.core.input_parser", "parse_user_input"),
        ("src.core.text_chunk", "chunk_text"),
        
        # LLM模块
        ("src.llm.local_llm_config", "LocalLLMConfig"),
        ("src.llm.ollama_api", "call_ollama_api"),
        
        # 评估模块
        ("src.evaluation.environment_validator", "validate_environment"),
        
        # 工具模块
        ("src.utils.retry_decider", "should_retry"),
    ]
    
    results = []
    
    for module_name, function_name in imports_to_test:
        try:
            module = importlib.import_module(module_name)
            if function_name:
                getattr(module, function_name)
            results.append((module_name, True, "导入成功"))
        except Exception as e:
            results.append((module_name, False, str(e)))
    
    return results

def main():
    """主函数"""
    print("=" * 60)
    print("项目文件整理后导入路径验证")
    print("=" * 60)
    
    results = verify_imports()
    
    print("\n导入验证结果:")
    print("-" * 60)
    
    success_count = 0
    for module, success, message in results:
        status = "✓" if success else "✗"
        print(f"{status} {module}: {message}")
        if success:
            success_count += 1
    
    print("-" * 60)
    print(f"总计: {success_count}/{len(results)} 成功")
    print("=" * 60)
    
    if success_count < len(results):
        print("\n警告: 部分模块导入失败，请检查文件路径和导入语句")
        sys.exit(1)
    else:
        print("\n成功: 所有模块导入正常")
        sys.exit(0)

if __name__ == "__main__":
    main()
