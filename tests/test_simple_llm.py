#!/usr/bin/env python3
"""
简单测试本地大模型配置模块

功能：
1. 测试基本的模型调用功能
2. 验证模型初始化和配置
"""

from local_llm_config import local_llm_config
import time

def test_basic_functionality():
    """测试基本功能"""
    print("=== 测试基本功能 ===")
    
    # 测试模型初始化
    print(f"当前活跃模型: {local_llm_config.get_active_model()}")
    print(f"模型参数: {local_llm_config.model_params}")
    
    # 测试简单的模型调用
    question = "What is 2 + 2?"
    print(f"\n问题: {question}")
    
    start_time = time.time()
    response = local_llm_config.invoke(question)
    end_time = time.time()
    
    if response:
        print(f"响应: {response}")
        print(f"使用模型: {local_llm_config.get_active_model()}")
        print(f"响应时间: {end_time - start_time:.2f} 秒")
        print("\n✓ 模型调用成功!")
    else:
        print("\n✗ 模型调用失败!")

def test_failover_basic():
    """测试基本的故障转移功能"""
    print("\n=== 测试故障转移功能 ===")
    
    # 保存原始模型
    original_model = local_llm_config.active_model
    
    try:
        # 临时设置一个不存在的模型
        local_llm_config.active_model = "non-existent-model:1.0"
        print(f"临时设置模型为: {local_llm_config.active_model}")
        
        # 测试调用
        question = "What is the capital of Germany?"
        print(f"问题: {question}")
        
        start_time = time.time()
        response = local_llm_config.invoke(question)
        end_time = time.time()
        
        if response:
            print(f"响应: {response}")
            print(f"最终使用的模型: {local_llm_config.get_active_model()}")
            print(f"响应时间: {end_time - start_time:.2f} 秒")
            print("\n✓ 故障转移成功!")
        else:
            print("\n✗ 故障转移失败!")
            
    finally:
        # 恢复原始模型
        local_llm_config.active_model = original_model
        print(f"恢复原始模型: {local_llm_config.active_model}")

def main():
    """主函数"""
    print("简单测试本地大模型配置模块")
    print("=" * 60)
    
    test_basic_functionality()
    test_failover_basic()
    
    print("\n" + "=" * 60)
    print("测试完成!")

if __name__ == "__main__":
    main()
