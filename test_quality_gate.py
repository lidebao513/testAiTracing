#!/usr/bin/env python3
"""
质量门禁测试脚本 - 检测模型幻觉

功能：
1. 测试模型输出是否与上下文信息一致
2. 设置质量门禁，当幻觉得分高于阈值时测试失败
3. 提供详细的错误提示信息

依赖：
- requests: 用于发送 HTTP 请求
- pytest: 测试框架
"""

import pytest
import requests
import re


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


def evaluate_hallucination(actual_output, context):
    """评估回答的幻觉程度
    
    Args:
        actual_output: 模型回答
        context: 上下文信息列表
        
    Returns:
        float: 幻觉程度评分 (0-1)，值越高表示幻觉越严重
    """
    try:
        # 创建幻觉评估提示
        context_text = "\n".join(context)
        prompt = f"""You are an evaluator. Assess how faithful the answer is to the context.

Context: {context_text}

Answer: {actual_output}

Rate the hallucination level on a scale of 0 to 1, where 1 means the answer has severe hallucinations and is completely inconsistent with the context, and 0 means the answer is completely faithful to the context. Only return the numerical score."""
        
        # 调用 Ollama API
        result = call_ollama_api(prompt)
        
        # 解析评分
        if result:
            # 提取数字评分
            score_match = re.search(r'\d+\.?\d*', result)
            if score_match:
                score = float(score_match.group())
                # 确保评分在 0-1 范围内
                return max(0.0, min(1.0, score))
        
        return 0.0
        
    except Exception as e:
        print(f"[ERROR] 评估幻觉程度时出错: {str(e)}")
        return 0.0


def test_hallucination_gate():
    """测试模型幻觉检测的质量门禁
    
    该测试通过比较模型输出与上下文信息的一致性，
    当幻觉得分高于阈值时，测试失败，表明内容存在严重幻觉问题。
    """
    # 定义测试用例
    test_name = "幻觉检测质量门禁测试"
    
    # 上下文信息 - 真实信息
    context = [
        "Paris is the capital city of France.",
        "The Eiffel Tower is located in Paris."
    ]
    
    # 与上下文明显不符的实际输出 - 包含幻觉
    actual_output = "London is the capital city of France, and the Big Ben is located there."
    
    # 预期输出 - 正确的信息
    expected_output = "Paris is the capital city of France, and the Eiffel Tower is located there."
    
    # 执行测试和评估
    print(f"\n=== {test_name} ===")
    print(f"上下文信息: {context}")
    print(f"实际输出: {actual_output}")
    print(f"预期输出: {expected_output}")
    print("开始评估幻觉程度...")
    
    try:
        # 评估幻觉程度
        hallucination_score = evaluate_hallucination(actual_output, context)
        print(f"幻觉得分: {hallucination_score:.4f}")
        
        # 设置阈值
        threshold = 0.5
        
        # 执行质量门禁判断
        if hallucination_score > threshold:
            print(f"❌ 测试失败: 模型输出与上下文不一致，存在严重幻觉问题")
            print(f"质量门禁判断: 幻觉得分 {hallucination_score:.4f} 高于阈值 {threshold}，内容不符合质量要求")
            # 抛出断言错误，确保测试失败
            assert hallucination_score <= threshold, f"幻觉得分 {hallucination_score:.4f} 高于阈值 {threshold}"
        else:
            print("✅ 测试通过: 模型输出与上下文一致，未检测到严重幻觉")
            
    except AssertionError as e:
        # 重新抛出异常，确保测试失败
        raise
    except Exception as e:
        print(f"❌ 测试执行出错: {str(e)}")
        raise


def run_test():
    """运行测试"""
    try:
        test_hallucination_gate()
        print("\n所有测试执行完成！")
    except Exception as e:
        print(f"\n测试执行失败: {str(e)}")


if __name__ == "__main__":
    """主执行入口"""
    run_test()
