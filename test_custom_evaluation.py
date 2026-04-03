#!/usr/bin/env python3
"""
自定义 RAG 评估脚本 - 使用本地 Ollama 模型

功能：
1. 构建示例评估数据集
2. 配置本地 Ollama 模型
3. 直接使用模型评估回答的质量
4. 输出评估结果

依赖：
- langchain-ollama: 用于与本地 Ollama 模型交互
- langchain-core: 用于构建处理链
"""

import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


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


def evaluate_faithfulness(llm, answer, context):
    """评估回答的忠实度
    
    Args:
        llm: 语言模型实例
        answer: 模型回答
        context: 上下文信息
        
    Returns:
        float: 忠实度评分 (0-1)
    """
    try:
        # 创建忠实度评估提示
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an evaluator. Assess how faithful the answer is to the context."),
            ("human", "Context: {context}\n\nAnswer: {answer}\n\nRate the faithfulness on a scale of 0 to 1, where 1 means the answer is completely faithful to the context and 0 means it's not faithful at all. Only return the numerical score.")
        ])
        
        # 创建输出解析器
        output_parser = StrOutputParser()
        
        # 构建处理链
        chain = prompt | llm | output_parser
        
        # 执行评估
        result = chain.invoke({"context": context, "answer": answer})
        
        # 解析评分
        score = float(result.strip())
        return score
        
    except Exception as e:
        print(f"[ERROR] 评估忠实度时出错: {str(e)}")
        return 0.0


def evaluate_relevancy(llm, question, answer):
    """评估回答的相关性
    
    Args:
        llm: 语言模型实例
        question: 用户问题
        answer: 模型回答
        
    Returns:
        float: 相关性评分 (0-1)
    """
    try:
        # 创建相关性评估提示
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an evaluator. Assess how relevant the answer is to the question."),
            ("human", "Question: {question}\n\nAnswer: {answer}\n\nRate the relevance on a scale of 0 to 1, where 1 means the answer is completely relevant to the question and 0 means it's not relevant at all. Only return the numerical score.")
        ])
        
        # 创建输出解析器
        output_parser = StrOutputParser()
        
        # 构建处理链
        chain = prompt | llm | output_parser
        
        # 执行评估
        result = chain.invoke({"question": question, "answer": answer})
        
        # 解析评分
        score = float(result.strip())
        return score
        
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
        
        # 配置 Ollama 模型
        llm = configure_ollama_llm()
        
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
            faithfulness = evaluate_faithfulness(llm, item['answer'], item['context'])
            total_faithfulness += faithfulness
            print(f"忠实度评分: {faithfulness:.4f}")
            
            # 评估相关性
            relevancy = evaluate_relevancy(llm, item['question'], item['answer'])
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
