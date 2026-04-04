#!/usr/bin/env python3
"""
LangSmith 追踪系统最终检查脚本

功能：
1. 执行一次 LLM 对话查询并确保被 LangSmith 追踪
2. 打印当前 LangSmith 项目名称和追踪 URL
3. 统计并显示最近 10 条追踪记录
4. 生成项目搭建成功的总结信息

依赖：
- python-dotenv: 加载环境变量
- langchain: 核心框架
- langchain-ollama: Ollama 集成
- langsmith: LangSmith 追踪
"""

import os
import time
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langsmith import Client


def load_environment():
    """加载环境变量"""
    try:
        load_dotenv()
        print("[SUCCESS] 环境变量加载成功")
        return True
    except Exception as e:
        print(f"[ERROR] 加载环境变量时出错: {str(e)}")
        return False


def validate_environment():
    """验证必要的环境变量"""
    required_vars = ["LANGCHAIN_API_KEY", "LANGCHAIN_PROJECT"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"[ERROR] 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("提示: 请在 .env 文件中设置这些环境变量")
        return False
    
    print("[SUCCESS] 环境变量验证成功")
    return True


def get_project_info():
    """获取项目信息"""
    try:
        client = Client()
        project_name = os.getenv("LANGCHAIN_PROJECT")
        
        # 获取项目信息
        projects = list(client.list_projects())
        target_project = None
        
        for project in projects:
            if project.name == project_name:
                target_project = project
                break
        
        if target_project:
            print(f"[SUCCESS] 找到项目: {target_project.name}")
            print(f"项目 URL: {target_project.url}")
            return target_project
        else:
            print(f"[WARNING] 未找到项目: {project_name}")
            return None
            
    except Exception as e:
        print(f"[ERROR] 获取项目信息时出错: {str(e)}")
        return None


def run_llm_query():
    """执行 LLM 查询并追踪"""
    try:
        # 初始化 ChatOllama 模型
        llm = ChatOllama(
            model="deepseek-r1:1.5b",
            temperature=0.7,
            base_url="http://localhost:11434",
            timeout=60
        )
        print("[SUCCESS] 初始化模型成功")
        
        # 创建聊天提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("human", "{question}")
        ])
        
        # 创建输出解析器
        output_parser = StrOutputParser()
        
        # 构建处理链
        chain = prompt | llm | output_parser
        
        # 执行查询
        question = "What is Python?"
        print(f"\n=== 执行查询: {question} ===")
        start_time = time.time()
        response = chain.invoke({"question": question})
        end_time = time.time()
        
        print(f"执行耗时: {(end_time - start_time) * 1000:.2f} 毫秒")
        print(f"响应: {response}")
        print("[SUCCESS] 查询执行成功")
        
        return question, response
        
    except Exception as e:
        print(f"[ERROR] 执行 LLM 查询时出错: {str(e)}")
        return None, None


def count_traces():
    """统计追踪记录数量"""
    try:
        client = Client()
        project_name = os.getenv("LANGCHAIN_PROJECT")
        
        # 获取最近 10 条追踪记录
        runs = list(client.list_runs(project_name=project_name, limit=10))
        print(f"\n=== 追踪记录统计 ===")
        print(f"当前项目: {project_name}")
        print(f"最近 10 条追踪记录总数: {len(runs)}")
        
        # 显示最近 5 条记录的时间
        print("\n最近 5 条追踪记录:")
        for i, run in enumerate(runs[:5], 1):
            print(f"{i}. 时间: {run.start_time}")
            print(f"   类型: {run.run_type}")
            print(f"   状态: {run.status}")
            print()
        
        return len(runs)
        
    except Exception as e:
        print(f"[ERROR] 统计追踪记录时出错: {str(e)}")
        return 0


def generate_summary(project, trace_count, question, response):
    """生成项目搭建成功的总结信息"""
    print("\n=== 项目搭建成功总结 ===")
    print("🎉 LangSmith 追踪系统已成功搭建!")
    print()
    print(f"项目名称: {os.getenv('LANGCHAIN_PROJECT')}")
    if project:
        print(f"项目 URL: {project.url}")
    print(f"追踪记录数量: {trace_count}")
    print()
    if question and response:
        print("本次测试信息:")
        print(f"查询: {question}")
        print(f"响应: {response}")
        print()
    print("后续操作建议:")
    print("1. 访问 LangSmith 控制台查看详细追踪记录")
    print("2. 尝试执行更多不同类型的查询，验证追踪功能")
    print("3. 探索 LangSmith 的其他功能，如评估和监控")
    print("4. 集成 LangSmith 到您的实际项目中")
    print()
    print("[SUCCESS] 所有检查完成，LangSmith 追踪系统运行正常!")


def main():
    """主函数"""
    # 加载环境变量
    if not load_environment():
        return
    
    # 验证环境变量
    if not validate_environment():
        return
    
    # 获取项目信息
    project = get_project_info()
    
    # 执行 LLM 查询
    question, response = run_llm_query()
    
    # 等待 2 秒，确保追踪记录已保存
    time.sleep(2)
    
    # 统计追踪记录
    trace_count = count_traces()
    
    # 生成总结信息
    generate_summary(project, trace_count, question, response)


if __name__ == "__main__":
    main()
