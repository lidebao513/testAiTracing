#!/usr/bin/env python3
"""
RAGAS 评估脚本 - 使用本地 Ollama 模型

功能：
1. 构建示例评估数据集
2. 配置本地 Ollama 模型作为评估器
3. 评估模型的忠实度和回答相关性
4. 输出评估结果

依赖：
- ragas: 用于 RAG 系统评估
- datasets: 用于数据处理
- langchain-ollama: 用于与本地 Ollama 模型交互
"""

import os
import json
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy
from langchain_ollama import ChatOllama

# 禁用 OpenAI API 调用
os.environ['OPENAI_API_KEY'] = 'dummy_key'  # 设置虚拟密钥，避免 RAGAS 尝试使用 OpenAI
os.environ['RAGAS_VERBOSE'] = 'True'  # 启用详细日志


def create_evaluation_dataset():
    """创建评估数据集
    
    Returns:
        Dataset: 包含问题、回答和上下文的评估数据集
    """
    try:
        # 构建示例数据
        data = {
            "user_input": [
                "What is the capital of France?",
                "Who wrote Romeo and Juliet?",
                "What is the chemical symbol for gold?"
            ],
            "response": [
                "The capital of France is Paris.",
                "William Shakespeare wrote Romeo and Juliet.",
                "The chemical symbol for gold is Au."
            ],
            "contexts": [
                ["France is a country in Europe. Paris is the capital city of France."],
                ["William Shakespeare was an English playwright. He wrote many plays including Romeo and Juliet."],
                ["Gold is a chemical element with the symbol Au. It is a precious metal."]
            ]
        }
        
        # 创建数据集
        dataset = Dataset.from_dict(data)
        print("[SUCCESS] 创建评估数据集成功")
        return dataset
        
    except Exception as e:
        print(f"[ERROR] 创建数据集时出错: {str(e)}")
        raise


def configure_ollama_llm():
    """配置本地 Ollama 模型
    
    Returns:
        ChatOllama: 配置好的 Ollama 模型实例
    """
    try:
        # 初始化 Ollama 模型
        llm = ChatOllama(
            model="deepseek-r1:1.5b",
            temperature=0.7,
            base_url="http://localhost:11434",
            timeout=600
        )
        print("[SUCCESS] 配置 Ollama 模型成功")
        return llm
        
    except Exception as e:
        print(f"[ERROR] 配置 Ollama 模型时出错: {str(e)}")
        raise


def run_ragas_evaluation():
    """运行 RAGAS 评估
    
    Returns:
        dict: 评估结果
    """
    try:
        # 创建评估数据集
        dataset = create_evaluation_dataset()
        
        # 配置 Ollama 模型
        llm = configure_ollama_llm()
        
        # 配置评估指标
        metrics = [
            Faithfulness(llm=llm),
            AnswerRelevancy(llm=llm)
        ]
        print("[SUCCESS] 配置评估指标成功")
        
        # 执行评估
        print("[INFO] 开始执行评估...")
        result = evaluate(
            dataset=dataset,
            metrics=metrics
        )
        print("[SUCCESS] 评估完成")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] 执行评估时出错: {str(e)}")
        raise


def print_evaluation_results(result):
    """打印评估结果
    
    Args:
        result: 评估结果
    """
    try:
        print("\n=== 评估结果 ===")
        
        # 检查结果类型并打印
        if isinstance(result, dict):
            # 如果是字典格式
            for metric_name, value in result.items():
                if isinstance(value, float):
                    print(f"{metric_name}: {value:.4f}")
                else:
                    print(f"{metric_name}: {value}")
        else:
            # 如果是其他格式
            print(f"评估结果: {result}")
        
        print()
        print("指标解释:")
        print("- 忠实度: 评估回答与提供上下文的一致性，值越高表示回答越忠实于上下文")
        print("- 回答相关性: 评估回答与问题的相关程度，值越高表示回答越相关")
        print()
        print("评估完成！")
        
    except Exception as e:
        print(f"[ERROR] 打印评估结果时出错: {str(e)}")
        raise


def main():
    """主函数"""
    try:
        # 运行评估
        result = run_ragas_evaluation()
        
        # 打印评估结果
        print_evaluation_results(result)
        
    except Exception as e:
        print(f"[ERROR] 主程序执行出错: {str(e)}")


if __name__ == "__main__":
    main()
