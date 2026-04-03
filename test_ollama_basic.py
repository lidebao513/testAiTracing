#!/usr/bin/env python3
"""
基本的 Ollama 模型测试脚本

功能：
1. 测试 Ollama 服务是否正常运行
2. 验证 deepseek-r1:1.5b 模型是否能够正常响应
3. 测试基本的问答功能
"""

import requests
import json


def test_ollama_service():
    """测试 Ollama 服务是否正常运行"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("Ollama 服务运行正常")
            print("可用模型:", [model['name'] for model in models])
            return True
        else:
            print(f"Ollama 服务返回状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"Ollama 服务测试失败: {str(e)}")
        return False


def test_model_response():
    """测试模型是否能够正常响应"""
    try:
        payload = {
            "model": "deepseek-r1:1.5b",
            "prompt": "What is the capital of France?",
            "stream": False,
            "timeout": 180
        }
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=180)
        if response.status_code == 200:
            result = response.json()
            print("模型响应成功:")
            print(f"回答: {result.get('response', 'No response')}")
            return True
        else:
            print(f"模型响应失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"模型响应测试失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("=== 测试 Ollama 服务 ===")
    if test_ollama_service():
        print("\n=== 测试模型响应 ===")
        test_model_response()
    else:
        print("Ollama 服务测试失败，请检查服务是否正在运行")


if __name__ == "__main__":
    main()
