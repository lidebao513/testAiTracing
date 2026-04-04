#!/usr/bin/env python3
"""
直接使用 Ollama API 进行评估的脚本

功能：
1. 构建示例评估数据集
2. 直接使用 Ollama API 评估回答的质量
3. 输出评估结果

依赖：
- requests: 用于发送 HTTP 请求
"""

import requests
import json


def create_evaluation_dataset():
    """创建评估数据集
    
    Returns:
        list: 包含问题、回答和上下文的评估数据列表
    """
    try:
        # 构建示例数据
        data = [
            {
                "question": "What is the capital of France?",
                "answer": "The capital of France is Paris.",
                "context": "France is a country in Europe. Paris is the capital city of France."
            },
            {
                "question": "Who wrote Romeo and Juliet?",
                "answer": "William Shakespeare wrote Romeo and Juliet.",
                "context": "William Shakespeare was an English playwright. He wrote many plays including Romeo and Juliet."
            },
            {
                "question": "What is the chemical symbol for gold?",
                "answer": "The chemical symbol for gold is Au.",
                "context": "Gold is a chemical element with the symbol Au. It is a precious metal."
            }
        ]
        
        print("[SUCCESS] 创建评估数据集成功")
        return data
        
    except Exception as e:
        print(f"[ERROR] 创建数据集时出错: {str(e)}")
        raise


def call_ollama_api(prompt, model="deepseek-r1:1.5b", timeout=180):
    """直接调用 Ollama API
    
    Args:
        prompt: 提示文本
        model: 模型名称
        timeout: 超时时间（秒）
        
    Returns:
        str: 模型响应
    """
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "timeout": timeout
        }
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json=payload, 
            timeout=timeout
        )
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '')
        else:
            print(f"[ERROR] Ollama API 返回状态码: {response.status_code}")
            return ''
            
    except Exception as e:
        print(f"[ERROR] 调用 Ollama API 时出错: {str(e)}")
        return ''


def evaluate_faithfulness(answer, context):
    """评估回答的忠实度
    
    Args:
        answer: 模型回答
        context: 上下文信息
        
    Returns:
        float: 忠实度评分 (0-1)
    """
    try:
        # 创建忠实度评估提示
        prompt = f"""You are an evaluator. Assess how faithful the answer is to the context.

Context: {context}

Answer: {answer}

Rate the faithfulness on a scale of 0 to 1, where 1 means the answer is completely faithful to the context and 0 means it's not faithful at all. Only return the numerical score."""
        
        # 调用 Ollama API
        result = call_ollama_api(prompt)
        
        # 解析评分
        if result:
            # 提取数字评分
            import re
            score_match = re.search(r'\d+\.?\d*', result)
            if score_match:
                score = float(score_match.group())
                # 确保评分在 0-1 范围内
                return max(0.0, min(1.0, score))
        
        return 0.0
        
    except Exception as e:
        print(f"[ERROR] 评估忠实度时出错: {str(e)}")
        return 0.0


def evaluate_relevancy(question, answer):
    """评估回答的相关性
    
    Args:
        question: 用户问题
        answer: 模型回答
        
    Returns:
        float: 相关性评分 (0-1)
    """
    try:
        # 创建相关性评估提示
        prompt = f"""You are an evaluator. Assess how relevant the answer is to the question.

Question: {question}

Answer: {answer}

Rate the relevance on a scale of 0 to 1, where 1 means the answer is completely relevant to the question and 0 means it's not relevant at all. Only return the numerical score."""
        
        # 调用 Ollama API
        result = call_ollama_api(prompt)
        
        # 解析评分
        if result:
            # 提取数字评分
            import re
            score_match = re.search(r'\d+\.?\d*', result)
            if score_match:
                score = float(score_match.group())
                # 确保评分在 0-1 范围内
                return max(0.0, min(1.0, score))
        
        return 0.0
        
    except Exception as e:
        print(f"[ERROR] 评估相关性时出错: {str(e)}")
        return 0.0


def run_evaluation():
    """运行评估
    
    Returns:
        dict: 评估结果
    """
    try:
        # 创建评估数据集
        dataset = create_evaluation_dataset()
        
        # 初始化评分
        total_faithfulness = 0.0
        total_relevancy = 0.0
        count = len(dataset)
        
        # 评估每个样本
        print("[INFO] 开始执行评估...")
        for i, item in enumerate(dataset, 1):
            print(f"\n评估样本 {i}/{count}:")
            print(f"问题: {item['question']}")
            print(f"回答: {item['answer']}")
            
            # 评估忠实度
            faithfulness = evaluate_faithfulness(item['answer'], item['context'])
            total_faithfulness += faithfulness
            print(f"忠实度评分: {faithfulness:.4f}")
            
            # 评估相关性
            relevancy = evaluate_relevancy(item['question'], item['answer'])
            total_relevancy += relevancy
            print(f"相关性评分: {relevancy:.4f}")
        
        # 计算平均评分
        avg_faithfulness = total_faithfulness / count
        avg_relevancy = total_relevancy / count
        
        print("\n[SUCCESS] 评估完成")
        
        return {
            "faithfulness": avg_faithfulness,
            "answer_relevancy": avg_relevancy
        }
        
    except Exception as e:
        print(f"[ERROR] 执行评估时出错: {str(e)}")
        raise


def print_evaluation_results(result):
    """打印评估结果
    
    Args:
        result: 评估结果字典
    """
    try:
        print("\n=== 评估结果 ===")
        print(f"忠实度 (Faithfulness): {result['faithfulness']:.4f}")
        print(f"回答相关性 (Answer Relevancy): {result['answer_relevancy']:.4f}")
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
        result = run_evaluation()
        
        # 打印评估结果
        print_evaluation_results(result)
        
    except Exception as e:
        print(f"[ERROR] 主程序执行出错: {str(e)}")


if __name__ == "__main__":
    main()
