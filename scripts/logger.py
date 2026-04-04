#!/usr/bin/env python3
"""
日志记录模块
用于记录评估请求和响应
"""

import os
import time
import json
from pathlib import Path

def log_request(agent_name, prompt, params, response, latency):
    """
    记录评估请求和响应
    
    Args:
        agent_name (str): 代理名称
        prompt (str): 提示词
        params (dict): 参数
        response (str): 响应
        latency (int): 延迟时间（毫秒）
    """
    # 确保logs目录存在
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # 创建日志文件名：logs/eval_YYYYMMDD.log
    log_file = logs_dir / f"eval_{time.strftime('%Y%m%d')}.log"
    
    # 构建日志条目
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "agent_name": agent_name,
        "prompt": prompt,
        "params": params,
        "response": response,
        "latency": latency
    }
    
    # 写入日志文件
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    # 测试代码
    log_request("test_agent", "prompt", {"temp": 0}, "response", 100)
    
    log_file = f"logs/eval_{time.strftime('%Y%m%d')}.log"
    assert os.path.exists(log_file), "Log file not created"
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "test_agent" in content and "prompt" in content
    
    print("PASS: logger")
