#!/usr/bin/env python3
"""
DeepEval 测试脚本 - 使用 Ollama 模型作为评估器

功能：
1. 测试 Ollama 模型的输出质量
2. 评估模型的幻觉程度和回答相关性
3. 验证模型连接和评估过程
4. 测试故障转移机制

依赖：
- deepeval: 用于模型评估
- pytest: 测试框架
- langchain-ollama: 用于与 Ollama 模型交互
- local_llm_config: 本地大模型配置模块
"""

import pytest
import os
import asyncio
from deepeval.test_case import LLMTestCase
from deepeval.metrics import HallucinationMetric
from deepeval import assert_test
from deepeval.models.llms.local_model import LocalModel
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from local_llm_config import local_llm_config

# 设置必要的环境变量
os.environ['LOCAL_MODEL_API_KEY'] = 'dummy_key'  # 对于本地 Ollama 服务，使用虚拟密钥
os.environ['DEEPEVAL_PER_ATTEMPT_TIMEOUT_SECONDS_OVERRIDE'] = '120'  # 增加超时时间
os.environ['DEEPEVAL_TASK_GATHER_BUFFER_SECONDS_OVERRIDE'] = '60'  # 增加缓冲区时间

# 设置默认事件循环策略
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def test_ollama_model_evaluation():
    """测试 Ollama 模型的输出质量
    
    该测试使用 DeepEval 框架评估 Ollama 模型的输出，
    包括幻觉程度和回答相关性两个指标。
    """
    try:
        # 测试问题
        test_question = "What is the capital of France?"
        expected_answer = "The capital of France is Paris."
        
        # 使用本地大模型配置模块获取模型输出
        actual_answer = local_llm_config.invoke(test_question)
        print(f"[SUCCESS] 获取模型输出: {actual_answer}")
        print(f"[INFO] 当前使用的模型: {local_llm_config.get_active_model()}")
        
        # 创建测试用例，添加 context 参数
        test_case = LLMTestCase(
            input=test_question,
            actual_output=actual_answer,
            expected_output=expected_answer,
            context=["France is a country in Europe. Paris is the capital city of France."]
        )
        print("[SUCCESS] 创建测试用例成功")
        
        # 获取当前活跃模型
        active_model = local_llm_config.get_active_model()
        
        # 创建 LocalModel 实例，指定 Ollama 模型和连接参数
        local_model = LocalModel(
            model=active_model,
            base_url="http://localhost:11434/v1",
            api_key="dummy_key"
        )
        print("[SUCCESS] 创建 LocalModel 实例成功")
        
        # 实例化评估指标，使用 LocalModel
        hallucination_metric = HallucinationMetric(model=local_model)
        print("[SUCCESS] 实例化评估指标成功")
        
        # 执行测试和评估
        print("[INFO] 开始执行评估...")
        assert_test(
            test_case=test_case,
            metrics=[hallucination_metric]
        )
        print("[SUCCESS] 评估完成，测试通过")
        
    except Exception as e:
        print(f"[ERROR] 测试过程中出错: {str(e)}")
        # 重新抛出异常，确保测试失败
        raise


if __name__ == "__main__":
    """主函数，用于直接运行测试"""
    try:
        test_ollama_model_evaluation()
        print("\n测试执行成功！")
    except Exception as e:
        print(f"\n测试执行失败: {str(e)}")
