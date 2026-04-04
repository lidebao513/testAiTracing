#!/usr/bin/env python3
"""
LangSmith 配置验证脚本
用于验证 LangSmith 环境变量配置
"""

import os
import sys
import time
import json
from dotenv import load_dotenv

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_langsmith_config() -> dict:
    """
    验证 LangSmith 环境变量配置

    Returns:
        验证结果
    """
    result = {
        "status": "❌",
        "message": "",
        "details": {}
    }

    try:
        load_dotenv('config/env/.env')

        # 检查关键环境变量
        required_vars = ["LANGCHAIN_API_KEY", "LANGCHAIN_PROJECT"]
        missing_vars = []
        invalid_vars = []

        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            elif var == "LANGCHAIN_API_KEY":
                # 验证 API Key 格式
                if len(value) < 20:
                    invalid_vars.append(f"{var} (长度不足)")

        if not missing_vars and not invalid_vars:
            result["status"] = "✅"
            result["message"] = "LangSmith 配置验证通过"
            result["details"]["api_key_set"] = "是"
            result["details"]["project_name"] = os.getenv("LANGCHAIN_PROJECT")
        else:
            result["message"] = "LangSmith 配置验证失败"
            if missing_vars:
                result["details"]["missing_vars"] = missing_vars
            if invalid_vars:
                result["details"]["invalid_vars"] = invalid_vars

    except Exception as e:
        result["message"] = f"LangSmith 配置验证失败: {str(e)}"
        result["details"]["error"] = str(e)

    return result

def main():
    """
    主函数
    """
    print("=== LangSmith 配置验证 ===")
    print(f"执行时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    result = verify_langsmith_config()
    
    print(f"\n状态: {result['status']}")
    print(f"消息: {result['message']}")
    
    if result.get('details'):
        print("\n详情:")
        for key, value in result['details'].items():
            if isinstance(value, list):
                print(f"  - {key}: {', '.join(value)}")
            else:
                print(f"  - {key}: {value}")
    
    # 生成 JSON 报告
    json_report = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "result": result
    }
    
    with open('langsmith_config_verification.json', 'w', encoding='utf-8') as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)
    
    print("\n验证报告已保存到: langsmith_config_verification.json")

if __name__ == "__main__":
    main()
