#!/usr/bin/env python3
"""
LangSmith 项目列表查看脚本

功能：
1. 加载环境变量中的 LangSmith API 密钥
2. 使用 LangSmith Client 列出账户下的所有项目
3. 按创建时间排序，显示最近创建的项目
4. 提供清晰的输出格式和错误处理
"""

import os
from dotenv import load_dotenv
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


def validate_api_key():
    """验证 API 密钥"""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        print("[ERROR] 未找到 LANGCHAIN_API_KEY 环境变量")
        print("提示: 请在 .env 文件中设置 LANGCHAIN_API_KEY")
        return False
    print("[SUCCESS] API 密钥验证成功")
    return True


def list_projects():
    """列出 LangSmith 项目"""
    try:
        # 初始化 LangSmith 客户端
        client = Client()
        print("[SUCCESS] LangSmith 客户端初始化成功")

        # 获取所有项目
        projects = list(client.list_projects())
        print(f"[SUCCESS] 成功获取 {len(projects)} 个项目")

        if not projects:
            print("[INFO] 当前账户下没有项目")
            return

        # 按创建时间排序（最新的在前）
        projects.sort(key=lambda p: p.start_time, reverse=True)

        # 显示项目信息
        print("\n=== 最近创建的 LangSmith 项目 ===")
        for i, project in enumerate(projects, 1):
            print(f"{i}. 项目名称: {project.name}")
            print(f"   项目 ID: {project.id}")
            print(f"   创建时间: {project.start_time}")
            print(f"   项目 URL: {project.url}")
            print()

        print("[SUCCESS] 项目列表显示完成")

    except Exception as e:
        print(f"[ERROR] 列出项目时出错: {str(e)}")
        raise


def main():
    """主函数"""
    # 加载环境变量
    if not load_environment():
        return

    # 验证 API 密钥
    if not validate_api_key():
        return

    try:
        # 列出项目
        list_projects()
    except Exception as e:
        print(f"[ERROR] 主程序执行出错: {str(e)}")


if __name__ == "__main__":
    main()
