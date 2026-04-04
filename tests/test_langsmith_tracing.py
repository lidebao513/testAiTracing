#!/usr/bin/env python3
"""
LangSmith 追踪功能测试脚本

依赖库：
- python-dotenv>=1.0.0: 用于加载环境变量
- langchain>=0.3.0: 核心框架
- langchain-ollama>=0.2.0: Ollama 集成
- langsmith>=0.1.0: LangSmith 追踪

功能：
1. 加载环境变量
2. 使用 @traceable 装饰器追踪函数执行
3. 集成 Ollama deepseek-r1:1.5b 模型
4. 构建并执行处理链
5. 验证 LangSmith 追踪功能
"""

import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def load_environment():
    """加载环境变量"""
    try:
        load_dotenv()
        print("[SUCCESS] 环境变量加载成功")
        return True
    except Exception as e:
        print(f"[ERROR] 加载环境变量时出错: {str(e)}")
        return False


def run_chain(question: str):
    """执行处理链并返回结果
    
    Args:
        question: 用户问题
        
    Returns:
        str: 模型响应
    """
    try:
        # 初始化 ChatOllama 模型
        llm = ChatOllama(
            model="deepseek-r1:1.5b",
            temperature=0.7,
            base_url="http://localhost:11434"
        )
        print("[SUCCESS] Ollama 模型初始化成功")

        # 创建聊天提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("human", "{question}")
        ])
        print("[SUCCESS] 提示模板创建成功")

        # 创建输出解析器
        output_parser = StrOutputParser()
        print("[SUCCESS] 输出解析器创建成功")

        # 构建处理链
        chain = prompt | llm | output_parser
        print("[SUCCESS] 处理链构建成功")

        # 执行处理链
        print(f"\n=== 执行查询: {question} ===")
        response = chain.invoke({"question": question})
        print("[SUCCESS] 处理链执行成功")

        return response

    except Exception as e:
        print(f"[ERROR] 执行处理链时出错: {str(e)}")
        raise


def main():
    """主函数"""
    # 加载环境变量
    if not load_environment():
        return

    try:
        # 执行处理链
        question = "What is the capital of France?"
        response = run_chain(question)

        # 打印结果
        print("\n=== 响应结果 ===")
        print(f"问题: {question}")
        print(f"回答: {response}")

        print("\n[SUCCESS] LangSmith 追踪测试成功!")
        print("提示: 请登录 LangSmith 控制台查看追踪记录")

    except Exception as e:
        print(f"[ERROR] 主程序执行出错: {str(e)}")
        print("提示: 请确保 Ollama 服务正在运行且 deepseek-r1:1.5b 模型已拉取")


if __name__ == "__main__":
    main()
