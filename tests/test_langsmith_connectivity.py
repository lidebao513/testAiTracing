#!/usr/bin/env python3
"""
LangSmith 连接性测试脚本

依赖库：
- python-dotenv: 用于加载环境变量
- langsmith: 用于与 LangSmith 服务交互

功能：
1. 加载环境变量
2. 验证 API 密钥
3. 初始化 LangSmith 客户端
4. 测试函数执行
5. 验证与 LangSmith 服务的连接
"""

import os
from dotenv import load_dotenv
from langsmith import Client


def load_environment():
    """加载环境变量"""
    try:
        load_dotenv()
        print("✅ 环境变量加载成功")
    except Exception as e:
        print(f"❌ 加载环境变量时出错: {str(e)}")
        print("提示: 请确保项目根目录存在 .env 文件")
        return False
    return True


def validate_api_key():
    """验证 API 密钥"""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        print("❌ 未找到 LANGCHAIN_API_KEY 环境变量")
        print("提示: 请在 .env 文件中设置 LANGCHAIN_API_KEY")
        return False
    print("✅ API 密钥验证成功")
    return True


def hello_world():
    """测试函数"""
    return "Hello, LangSmith!"


def main():
    """主函数"""
    # 加载环境变量
    if not load_environment():
        return

    # 验证 API 密钥
    if not validate_api_key():
        return

    try:
        # 初始化 LangSmith 客户端
        client = Client()
        print("✅ LangSmith 客户端初始化成功")

        # 调用测试函数
        result = hello_world()
        print(f"✅ 函数执行结果: {result}")

        # 验证与 LangSmith 服务的连接
        print("\n=== 验证 LangSmith 服务连接 ===")
        projects = list(client.list_projects())
        print(f"✅ 成功获取 {len(projects)} 个项目")
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project.name}")

        print("\n🎉 LangSmith 连接性测试成功!")

    except Exception as e:
        if "authentication" in str(e).lower():
            print("❌ 认证错误: API 密钥无效或已过期")
            print("提示: 请检查 .env 文件中的 LANGCHAIN_API_KEY 是否正确")
        elif "connection" in str(e).lower():
            print("❌ 网络连接错误: 无法连接到 LangSmith 服务")
            print("提示: 请检查网络连接并确保 LangSmith 服务可访问")
        else:
            print(f"❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    main()
