#!/usr/bin/env python3
"""
简化版 LangSmith 连接测试脚本
"""

import os
from dotenv import load_dotenv
from langsmith import Client

# 加载环境变量
print("加载环境变量...")
load_dotenv()

# 检查环境变量
api_key = os.getenv("LANGCHAIN_API_KEY")
print(f"API Key: {api_key[:10]}...")
print(f"Project: {os.getenv('LANGCHAIN_PROJECT')}")
print(f"Tracing: {os.getenv('LANGCHAIN_TRACING_V2')}")

# 尝试创建客户端
print("\n尝试连接 LangSmith...")
try:
    client = Client()
    print("✅ LangSmith 客户端创建成功")
    
    # 测试获取项目列表
    projects = list(client.list_projects())
    print(f"✅ 成功获取 {len(projects)} 个项目")
    for project in projects:
        print(f"  - {project.name}")
        
    print("\n🎉 连接测试成功！")
except Exception as e:
    print(f"❌ 连接失败: {str(e)}")
