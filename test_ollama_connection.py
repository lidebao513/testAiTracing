#!/usr/bin/env python3
"""
测试 Ollama 连接和模型可用性

功能：
1. 测试 Ollama 服务是否正常运行
2. 测试模型是否可用
3. 测试基本的模型调用
"""

import requests
import json

def test_ollama_connection():
    """测试 Ollama 连接"""
    print("=== 测试 Ollama 连接 ===")
    
    try:
        # 测试 Ollama 服务是否正常运行
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✓ Ollama 服务正常运行")
            print(f"可用模型: {[model['name'] for model in models]}")
            return models
        else:
            print(f"✗ Ollama 服务返回错误: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ 连接 Ollama 服务失败: {str(e)}")
        return []

def test_model_inference(model_name):
    """测试模型推理"""
    print(f"\n=== 测试模型: {model_name} ===")
    
    try:
        # 构建请求数据
        data = {
            "model": model_name,
            "prompt": "What is 2 + 2?",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 100
            }
        }
        
        # 发送请求
        response = requests.post("http://localhost:11434/api/generate", json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 模型调用成功")
            print(f"响应: {result.get('response', 'No response')}")
            return True
        else:
            print(f"✗ 模型调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 模型调用异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("测试 Ollama 连接和模型可用性")
    print("=" * 60)
    
    # 测试 Ollama 连接
    models = test_ollama_connection()
    
    # 测试模型推理
    if models:
        # 测试第一个模型
        test_model_inference(models[0]['name'])
    
    print("\n" + "=" * 60)
    print("测试完成!")

if __name__ == "__main__":
    main()
