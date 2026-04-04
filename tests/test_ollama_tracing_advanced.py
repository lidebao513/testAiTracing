#!/usr/bin/env python3
"""
Ollama 追踪功能高级测试脚本

依赖库：
- python-dotenv>=1.0.0: 用于加载环境变量
- langchain>=0.3.0: 核心框架
- langchain-ollama>=0.2.0: Ollama 集成
- langsmith>=0.1.0: LangSmith 追踪

功能：
1. 实现 OllamaTracingTest 类
2. 测试简单查询、批量查询和错误处理
3. 使用 LangSmith 追踪功能
4. 记录执行耗时和结果
"""

import os
import time
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


class OllamaTracingTest:
    """Ollama 追踪测试类"""
    
    def __init__(self, model_name):
        """初始化方法
        
        Args:
            model_name: 模型名称
        """
        try:
            self.llm = ChatOllama(
                model=model_name,
                temperature=0.7,
                base_url="http://localhost:11434",
                timeout=60,
                num_predict=256
            )
            self.model_name = model_name
            print(f"[SUCCESS] 初始化 {model_name} 模型成功")
        except Exception as e:
            print(f"[ERROR] 初始化模型时出错: {str(e)}")
            raise
    
    def simple_query(self, question):
        """简单查询方法
        
        Args:
            question: 问题字符串
            
        Returns:
            str: 模型响应
        """
        try:
            # 创建聊天提示模板
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant."),
                ("human", "{question}")
            ])
            
            # 创建输出解析器
            output_parser = StrOutputParser()
            
            # 构建处理链
            chain = prompt | self.llm | output_parser
            
            # 执行查询
            response = chain.invoke({"question": question})
            return response
        except Exception as e:
            print(f"[ERROR] 执行简单查询时出错: {str(e)}")
            raise
    
    def batch_query(self, questions):
        """批量查询方法
        
        Args:
            questions: 问题列表
            
        Returns:
            dict: 每个问题的查询结果
        """
        results = {}
        for i, question in enumerate(questions, 1):
            try:
                start_time = time.time()
                result = self.simple_query(question)
                end_time = time.time()
                results[question] = {
                    "status": "success",
                    "result": result,
                    "time": end_time - start_time
                }
                print(f"[SUCCESS] 批量查询 {i}/{len(questions)} 成功")
            except Exception as e:
                results[question] = {
                    "status": "failed",
                    "error": str(e)
                }
                print(f"[ERROR] 批量查询 {i}/{len(questions)} 失败: {str(e)}")
        return results
    
    def test_error_handling(self):
        """错误处理测试方法
        
        Returns:
            dict: 测试结果
        """
        try:
            # 创建不存在的模型实例
            error_llm = ChatOllama(
                model="non-existent-model",
                temperature=0.7,
                base_url="http://localhost:11434",
                timeout=60
            )
            
            # 创建提示模板和解析器
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant."),
                ("human", "What is 2+2?")
            ])
            output_parser = StrOutputParser()
            
            # 构建处理链
            chain = prompt | error_llm | output_parser
            
            # 执行查询
            response = chain.invoke({"question": "What is 2+2?"})
            return {"status": "success", "result": response}
        except Exception as e:
            print(f"[ERROR] 错误处理测试捕获到异常: {str(e)}")
            return {"status": "failed", "error": str(e)}


def run_test_scenario(scenario_name, test_func, *args, **kwargs):
    """运行测试场景
    
    Args:
        scenario_name: 场景名称
        test_func: 测试函数
        *args: 位置参数
        **kwargs: 关键字参数
    """
    print(f"\n=== 测试场景: {scenario_name} ===")
    start_time = time.time()
    
    try:
        result = test_func(*args, **kwargs)
        end_time = time.time()
        elapsed = (end_time - start_time) * 1000  # 转换为毫秒
        
        print(f"[SUCCESS] 场景执行成功")
        print(f"执行耗时: {elapsed:.2f} 毫秒")
        print(f"查询结果: {result}")
        print(f"执行状态: 成功")
        
        return {"status": "success", "result": result, "time": elapsed}
        
    except Exception as e:
        end_time = time.time()
        elapsed = (end_time - start_time) * 1000  # 转换为毫秒
        
        print(f"[ERROR] 场景执行失败: {str(e)}")
        print(f"执行耗时: {elapsed:.2f} 毫秒")
        print(f"错误信息: {str(e)}")
        print(f"执行状态: 失败")
        
        return {"status": "failed", "error": str(e), "time": elapsed}


def main():
    """主函数"""
    # 加载环境变量
    if not load_environment():
        return
    
    try:
        # 初始化测试类
        test = OllamaTracingTest("deepseek-r1:1.5b")
        
        # 场景1：简单查询
        run_test_scenario(
            "简单查询测试",
            test.simple_query,
            "What is 2+2?"
        )
        
        # 场景2：批量查询
        run_test_scenario(
            "批量查询测试",
            test.batch_query,
            [
                "What is capital of Japan?",
                "Chemical symbol for gold?",
                "Who wrote Romeo and Juliet?"
            ]
        )
        
        # 场景3：错误处理测试
        run_test_scenario(
            "错误处理测试",
            test.test_error_handling
        )
        
        print("\n[SUCCESS] 所有测试场景执行完成")
        print("提示: 请登录 LangSmith 控制台查看追踪记录")
        
    except Exception as e:
        print(f"[ERROR] 主程序执行出错: {str(e)}")


if __name__ == "__main__":
    main()
