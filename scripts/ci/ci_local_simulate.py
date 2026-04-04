#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI 本地模拟脚本

模拟 GitHub Actions CI 流程，包括环境检查、依赖安装、测试执行和结果报告

使用方法:
    python ci_local_simulate.py [options]

选项:
    -h, --help          显示帮助信息
    --no-deps           跳过依赖安装步骤
    --test-file FILE     指定测试文件路径 (默认: test_quality_gate.py)
    --verbose           启用详细输出

示例:
    # 运行完整的 CI 模拟流程
    python ci_local_simulate.py
    
    # 跳过依赖安装，直接运行测试
    python ci_local_simulate.py --no-deps
    
    # 使用自定义测试文件
    python ci_local_simulate.py --test-file my_test.py
    
    # 启用详细输出
    python ci_local_simulate.py --verbose
"""

import os
import sys
import subprocess
import argparse
import platform
import time
from datetime import datetime

# 配置日志输出
class Logger:
    def __init__(self, verbose=False):
        self.verbose = verbose
    
    def info(self, message):
        print(f"[INFO] {message}")
    
    def warning(self, message):
        print(f"[WARNING] {message}")
    
    def error(self, message):
        print(f"[ERROR] {message}")
    
    def debug(self, message):
        if self.verbose:
            print(f"[DEBUG] {message}")

logger = None


def check_python_version():
    """检查 Python 版本是否为 3.10 及以上"""
    logger.info("检查 Python 版本...")
    
    version = sys.version_info
    logger.info(f"当前 Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        logger.error(f"Python 版本必须为 3.10 或更高，当前版本为 {version.major}.{version.minor}.{version.micro}")
        return False
    
    logger.info("✅ Python 版本检查通过")
    return True


def install_dependencies():
    """安装项目依赖"""
    logger.info("开始安装依赖...")
    
    # 升级 pip
    try:
        logger.info("升级 pip...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.debug(result.stdout)
        logger.info("✅ pip 升级成功")
    except subprocess.CalledProcessError as e:
        logger.error(f"pip 升级失败: {e.stderr}")
        return False
    
    # 安装项目依赖
    try:
        if os.path.exists("requirements.txt"):
            logger.info("从 requirements.txt 安装依赖...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.debug(result.stdout)
        elif os.path.exists("pyproject.toml"):
            logger.info("从 pyproject.toml 安装依赖...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "."],
                capture_output=True,
                text=True,
                check=True
            )
            logger.debug(result.stdout)
        else:
            logger.error("错误: 未找到 requirements.txt 或 pyproject.toml")
            return False
        
        # 安装测试依赖
        logger.info("安装测试依赖...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pytest", "deepeval"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.debug(result.stdout)
        logger.info("✅ 依赖安装成功")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"依赖安装失败: {e.stderr}")
        return False


def run_tests(test_file):
    """运行测试"""
    logger.info(f"开始运行测试: {test_file}")
    
    # 检查测试文件是否存在
    if not os.path.exists(test_file):
        logger.error(f"测试文件不存在: {test_file}")
        return False, None
    
    # 运行测试
    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v"],
            capture_output=True,
            text=True
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 打印测试输出
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        # 解析测试结果
        test_results = parse_test_results(result.stdout)
        
        # 生成测试报告
        generate_test_report(test_results, execution_time, result.returncode)
        
        # 返回测试结果
        return result.returncode == 0, result.returncode
        
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        return False, 1


def parse_test_results(output):
    """解析测试结果"""
    results = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "total": 0
    }
    
    # 简单解析测试输出
    lines = output.split('\n')
    for line in lines:
        if "PASSED" in line:
            results["passed"] += 1
        elif "FAILED" in line:
            results["failed"] += 1
        elif "SKIPPED" in line:
            results["skipped"] += 1
    
    results["total"] = results["passed"] + results["failed"] + results["skipped"]
    return results


def generate_test_report(results, execution_time, returncode):
    """生成测试报告"""
    print("\n" + "=" * 70)
    print("📊 CI 测试结果报告")
    print("=" * 70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"执行时间: {execution_time:.2f} 秒")
    print(f"总测试用例: {results['total']}")
    print(f"通过: {results['passed']}")
    print(f"失败: {results['failed']}")
    print(f"跳过: {results['skipped']}")
    
    if returncode == 0:
        print("\n✅ 所有测试通过!")
    else:
        print("\n❌ 测试失败!")
    
    print("=" * 70 + "\n")


def main():
    """主函数"""
    global logger
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="CI 本地模拟脚本")
    parser.add_argument("--no-deps", action="store_true", help="跳过依赖安装步骤")
    parser.add_argument("--test-file", default="test_quality_gate.py", help="指定测试文件路径")
    parser.add_argument("--verbose", action="store_true", help="启用详细输出")
    args = parser.parse_args()
    
    # 初始化日志
    logger = Logger(args.verbose)
    
    # 打印欢迎信息
    print("\n" + "=" * 70)
    print("🚀 CI 本地模拟流程启动")
    print("=" * 70)
    
    # 1. 检查 Python 版本
    if not check_python_version():
        return 1
    
    # 2. 安装依赖
    if not args.no_deps:
        if not install_dependencies():
            return 1
    else:
        logger.info("跳过依赖安装步骤")
    
    # 3. 运行测试
    success, returncode = run_tests(args.test_file)
    
    # 4. 返回结果
    if success:
        logger.info("✅ CI 模拟流程成功完成")
        return 0
    else:
        logger.error("❌ CI 模拟流程失败")
        return returncode


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
