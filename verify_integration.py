#!/usr/bin/env python3
"""
集成验证脚本
用于验证 testAiTracing 项目的系统集成状态
"""

import os
import sys
import time
import json
import argparse
import logging
import requests
from typing import Dict, List, Optional, Any, Tuple
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scripts.rag_client import RAGClient
from tests.integration.test_ragas_with_tracing import RAGASEvaluator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegrationVerifier:
    """集成验证类"""

    def __init__(self, verbose: bool = False):
        """
        初始化集成验证器

        Args:
            verbose: 是否启用详细模式
        """
        self.verbose = verbose
        self.results = {}
        self.score = 0
        self.total_tests = 0
        self.passed_tests = 0

    def _log(self, message: str, level: str = "info"):
        """
        日志记录

        Args:
            message: 日志消息
            level: 日志级别
        """
        if self.verbose:
            if level == "info":
                logger.info(message)
            elif level == "error":
                logger.error(message)
            elif level == "warning":
                logger.warning(message)

    def verify_ragapp_api(self) -> Dict[str, Any]:
        """
        验证 RAGApp API 可访问性

        Returns:
            验证结果
        """
        self.total_tests += 1
        result = {
            "status": "❌",
            "message": "",
            "details": {}
        }

        try:
            # 加载环境变量
            load_dotenv('config/env/.env')
            api_url = os.getenv('RAG_APP_API_URL', 'http://localhost:8000')
            health_endpoint = f"{api_url}/health"

            self._log(f"测试 RAGApp API 健康检查: {health_endpoint}")

            # 带重试的健康检查
            max_retries = 3
            timeout = 5
            success = False

            for attempt in range(max_retries):
                try:
                    response = requests.get(health_endpoint, timeout=timeout)
                    self._log(f"尝试 {attempt + 1}/{max_retries}: HTTP {response.status_code}")

                    if response.status_code == 200:
                        # 验证响应内容
                        try:
                            response_json = response.json()
                            if "status" in response_json and response_json["status"] == "healthy":
                                success = True
                                break
                            else:
                                self._log(f"响应内容不符合预期: {response_json}", "warning")
                        except json.JSONDecodeError:
                            self._log(f"响应不是有效的 JSON: {response.text}", "warning")
                except requests.RequestException as e:
                    self._log(f"请求失败: {str(e)}", "warning")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # 等待 1 秒后重试

            if success:
                result["status"] = "✅"
                result["message"] = "RAGApp API 健康检查通过"
                result["details"]["api_url"] = api_url
                result["details"]["response"] = "{status: healthy}"
                self.passed_tests += 1
            else:
                result["message"] = "RAGApp API 健康检查失败"
                result["details"]["api_url"] = api_url
                result["details"]["error"] = "无法连接到 RAGApp 服务或响应不符合预期"

        except Exception as e:
            result["message"] = f"验证过程出错: {str(e)}"
            result["details"]["error"] = str(e)

        self.results["ragapp_api"] = result
        return result

    def verify_ragclient(self) -> Dict[str, Any]:
        """
        验证 RAGClient 模块功能

        Returns:
            验证结果
        """
        self.total_tests += 1
        result = {
            "status": "❌",
            "message": "",
            "details": {}
        }

        try:
            self._log("测试 RAGClient 初始化")
            client = RAGClient()

            # 测试基础查询
            test_question = "什么是 RAG 技术？"
            self._log(f"测试 RAGClient 查询: {test_question}")

            start_time = time.time()
            response = client.ask(test_question, k=2)
            response_time = time.time() - start_time

            # 验证响应格式
            if "answer" in response and "sources" in response:
                result["status"] = "✅"
                result["message"] = "RAGClient 功能验证通过"
                result["details"]["response_time"] = f"{response_time:.2f}s"
                result["details"]["answer_length"] = len(response["answer"])
                result["details"]["sources_count"] = len(response["sources"])

                # 检查响应时间
                if response_time < 2:
                    result["details"]["response_time_status"] = "符合要求 (< 2s)"
                else:
                    result["details"]["response_time_status"] = "警告 (> 2s)"

                self.passed_tests += 1
            else:
                result["message"] = "RAGClient 响应格式错误"
                result["details"]["response"] = response

        except Exception as e:
            result["message"] = f"RAGClient 验证失败: {str(e)}"
            result["details"]["error"] = str(e)

        self.results["ragclient"] = result
        return result

    def verify_ragas_evaluation(self) -> Dict[str, Any]:
        """
        验证 RAGAS 评估脚本执行

        Returns:
            验证结果
        """
        self.total_tests += 1
        result = {
            "status": "❌",
            "message": "",
            "details": {}
        }

        try:
            self._log("测试 RAGAS 评估执行")
            evaluator = RAGASEvaluator()
            evaluation_results = evaluator.evaluate()

            if "error" not in evaluation_results:
                # 验证评估指标
                required_metrics = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
                all_metrics_present = all(metric in evaluation_results for metric in required_metrics)

                if all_metrics_present:
                    result["status"] = "✅"
                    result["message"] = "RAGAS 评估执行成功"
                    result["details"]["metrics"] = {}

                    # 检查指标范围
                    for metric in required_metrics:
                        score = evaluation_results[metric]
                        result["details"]["metrics"][metric] = f"{score:.4f}"

                        # 检查分数是否在合理范围
                        if 0 <= score <= 1:
                            result["details"]["metrics"][f"{metric}_status"] = "正常"
                        else:
                            result["details"]["metrics"][f"{metric}_status"] = "异常"

                    self.passed_tests += 1
                else:
                    result["message"] = "RAGAS 评估结果缺少必要指标"
                    result["details"]["available_metrics"] = list(evaluation_results.keys())
            else:
                result["message"] = f"RAGAS 评估执行失败: {evaluation_results['error']}"
                result["details"]["error"] = evaluation_results['error']

        except Exception as e:
            result["message"] = f"RAGAS 评估验证失败: {str(e)}"
            result["details"]["error"] = str(e)

        self.results["ragas_evaluation"] = result
        return result

    def verify_deepeval_gate(self) -> Dict[str, Any]:
        """
        验证 DeepEval 门禁脚本执行

        Returns:
            验证结果
        """
        self.total_tests += 1
        result = {
            "status": "❌",
            "message": "",
            "details": {}
        }

        try:
            self._log("测试 DeepEval 门禁执行")
            import subprocess
            import tempfile

            # 运行 DeepEval 门禁脚本
            script_path = "tests/integration/test_deepeval_gate_on_ragapp.py"
            timeout = 300  # 5分钟超时

            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
                temp_file_path = temp_file.name

            # 执行脚本并捕获输出
            start_time = time.time()
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # 读取输出
            output = []
            try:
                stdout, _ = process.communicate(timeout=timeout)
                output.append(stdout)
            except subprocess.TimeoutExpired:
                process.kill()
                result["message"] = "DeepEval 门禁执行超时"
                result["details"]["error"] = f"执行时间超过 {timeout} 秒"
                return result

            execution_time = time.time() - start_time

            # 检查返回码
            if process.returncode == 0:
                result["status"] = "✅"
                result["message"] = "DeepEval 门禁执行成功"
                result["details"]["execution_time"] = f"{execution_time:.2f}s"
                self.passed_tests += 1
            else:
                result["message"] = "DeepEval 门禁执行失败"
                result["details"]["returncode"] = process.returncode
                result["details"]["output"] = stdout[:500]  # 只保存前500个字符

        except Exception as e:
            result["message"] = f"DeepEval 门禁验证失败: {str(e)}"
            result["details"]["error"] = str(e)

        self.results["deepeval_gate"] = result
        return result

    def verify_langsmith_config(self) -> Dict[str, Any]:
        """
        验证 LangSmith 环境变量配置

        Returns:
            验证结果
        """
        self.total_tests += 1
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
                self.passed_tests += 1
            else:
                result["message"] = "LangSmith 配置验证失败"
                if missing_vars:
                    result["details"]["missing_vars"] = missing_vars
                if invalid_vars:
                    result["details"]["invalid_vars"] = invalid_vars

        except Exception as e:
            result["message"] = f"LangSmith 配置验证失败: {str(e)}"
            result["details"]["error"] = str(e)

        self.results["langsmith_config"] = result
        return result

    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        生成综合报告

        Args:
            output_path: 报告输出路径

        Returns:
            报告内容
        """
        # 计算健康评分
        if self.total_tests > 0:
            self.score = int((self.passed_tests / self.total_tests) * 100)
        else:
            self.score = 0

        # 生成 Markdown 报告
        report = []
        report.append("# 集成验证报告")
        report.append(f"\n## 执行时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"## 健康评分: {self.score}/100")
        report.append(f"## 测试结果: {self.passed_tests}/{self.total_tests} 通过")

        report.append("\n## 详细验证结果")

        for test_name, test_result in self.results.items():
            test_name_display = test_name.replace('_', ' ').title()
            report.append(f"\n### {test_name_display}")
            report.append(f"- 状态: {test_result['status']}")
            report.append(f"- 消息: {test_result['message']}")

            if test_result.get('details'):
                report.append("- 详情:")
                for key, value in test_result['details'].items():
                    if isinstance(value, dict):
                        report.append(f"  - {key}:")
                        for sub_key, sub_value in value.items():
                            report.append(f"    - {sub_key}: {sub_value}")
                    else:
                        report.append(f"  - {key}: {value}")

        # 生成 JSON 报告
        json_report = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "score": self.score,
            "test_results": {
                "total": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.total_tests - self.passed_tests
            },
            "details": self.results
        }

        # 保存报告
        if output_path:
            # 保存 Markdown 报告
            md_path = output_path
            if not md_path.endswith('.md'):
                md_path += '.md'

            with open(md_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report))

            # 保存 JSON 报告
            json_path = output_path.replace('.md', '.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_report, f, indent=2, ensure_ascii=False)

            self._log(f"报告已保存到: {md_path} 和 {json_path}")

        return '\n'.join(report)

    def run_all_tests(self) -> Dict[str, Any]:
        """
        运行所有验证测试

        Returns:
            验证结果
        """
        self._log("开始集成验证...")

        # 运行所有验证
        self.verify_ragapp_api()
        self.verify_ragclient()
        self.verify_ragas_evaluation()
        self.verify_deepeval_gate()
        self.verify_langsmith_config()

        self._log(f"集成验证完成，得分: {self.score}/100")
        return self.results

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description="集成验证脚本")
    parser.add_argument('--verbose', action='store_true', help='启用详细模式')
    parser.add_argument('--output', type=str, help='报告输出路径')

    args = parser.parse_args()

    # 创建验证器
    verifier = IntegrationVerifier(verbose=args.verbose)

    # 运行所有测试
    results = verifier.run_all_tests()

    # 生成报告
    report = verifier.generate_report(output_path=args.output)

    # 打印报告
    print(report)

if __name__ == "__main__":
    main()
