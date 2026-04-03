#!/usr/bin/env python3
"""
测试本地大模型配置模块

功能：
1. 测试模型调用功能
2. 测试故障转移机制
3. 验证配置参数
"""

from local_llm_config import local_llm_config
import time

def test_model_invoke():
    """测试模型调用功能"""
    print("=== 测试模型调用功能 ===")
    
    # 测试问题
    test_questions = [
        "What is the capital of France?",
        "What is 2 + 2?",
        "Tell me a short story about a cat"
    ]
    
    for question in test_questions:
        print(f"\n问题: {question}")
        start_time = time.time()
        response = local_llm_config.invoke(question)
        end_time = time.time()
        
        print(f"响应: {response}")
        print(f"使用模型: {local_llm_config.get_active_model()}")
        print(f"响应时间: {end_time - start_time:.2f} 秒")

def test_failover_mechanism():
    """测试故障转移机制"""
    print("\n=== 测试故障转移机制 ===")
    
    # 保存原始模型列表
    original_models = local_llm_config.models.copy()
    
    try:
        # 临时修改模型列表，将不存在的模型放在第一位
        local_llm_config.models = [
            {
                "name": "non-existent-model:1.0",
                "priority": 1
            },
            {
                "name": "deepseek-r1:7b",
                "priority": 2
            }
        ]
        
        # 重新初始化模型
        local_llm_config._initialize_models()
        
        # 测试调用
        question = "What is the capital of Germany?"
        print(f"问题: {question}")
        response = local_llm_config.invoke(question)
        print(f"响应: {response}")
        print(f"最终使用的模型: {local_llm_config.get_active_model()}")
        
    finally:
        # 恢复原始模型列表
        local_llm_config.models = original_models
        local_llm_config._initialize_models()

def test_config_parameters():
    """测试配置参数"""
    print("\n=== 测试配置参数 ===")
    
    # 测试获取当前配置
    print(f"当前活跃模型: {local_llm_config.get_active_model()}")
    print(f"模型参数: {local_llm_config.model_params}")
    print(f"重试策略: {local_llm_config.retry_strategy}")
    
    # 测试更新配置
    new_params = {"temperature": 0.5, "max_tokens": 512}
    local_llm_config.set_model_params(new_params)
    
    new_strategy = {"max_retries": 5, "retry_interval": 1}
    local_llm_config.set_retry_strategy(new_strategy)
    
    print(f"更新后模型参数: {local_llm_config.model_params}")
    print(f"更新后重试策略: {local_llm_config.retry_strategy}")

def main():
    """主函数"""
    print("测试本地大模型配置模块")
    print("=" * 60)
    
    test_model_invoke()
    test_failover_mechanism()
    test_config_parameters()
    
    print("\n" + "=" * 60)
    print("测试完成!")

if __name__ == "__main__":
    main()
