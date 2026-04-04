#!/usr/bin/env python3
"""
增强版 RAGAS 评估测试文件
用于评估 RAG 应用的性能，包含完整的 LangSmith 追踪功能
"""

import os
import sys
import logging
from typing import List, Dict, Any
import datasets
from ragas import evaluate
from ragas.metrics.collections import faithfulness, answer_relevancy, context_precision, context_recall
from langsmith import traceable
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_core.language_models import BaseLanguageModel

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.rag_client import RAGClient

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv('config/env/.env')

# 设置 OpenAI API 密钥（用于 RAGAS 评估）
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'dummy_key')

# 测试数据集
TEST_DATASET = [
    {
        "question": "什么是 RAG 技术？",
        "ground_truth": "RAG（Retrieval-Augmented Generation，检索增强生成）是一种结合信息检索技术与生成式 AI 的方法，通过在生成内容之前检索相关文档来增强模型的生成能力，从而提高生成内容的准确性和可靠性。",
        "contexts": [
            "RAG 技术是一种将检索和生成相结合的方法，旨在通过检索相关数据来增强生成模型的表现。",
            "RAG 可以帮助模型生成更准确、更相关的内容，避免幻觉问题。",
            "RAG 系统通常包括检索器和生成器两个主要组件。"
        ]
    }
    # 以下问题已被注释，仅保留第一个问题进行测试
    # {
    #     "question": "RAG 技术的应用场景有哪些？",
    #     "ground_truth": "RAG 技术广泛应用于问答系统、文档检索、知识密集型任务、个性化推荐、教育辅助等场景，特别适用于需要准确信息和上下文理解的任务。",
    #     "contexts": [
    #         "RAG 技术在问答系统中应用广泛，可以提供更准确的回答。",
    #         "在文档检索领域，RAG 可以帮助用户快速找到相关信息。",
    #         "RAG 还可以用于知识密集型任务，如金融分析、医疗诊断等。"
    #     ]
    # },
    # {
    #     "question": "RAG 系统的主要组件有哪些？",
    #     "ground_truth": "RAG 系统的主要组件包括：1. 检索器（Retriever）：负责从知识库中检索相关文档；2. 生成器（Generator）：基于检索到的文档生成回答；3. 知识库（Knowledge Base）：存储用于检索的文档集合；4. 索引（Index）：用于加速文档检索的结构。",
    #     "contexts": [
    #         "RAG 系统通常由检索器和生成器两个主要组件组成。",
    #         "检索器负责从知识库中找到与查询相关的文档。",
    #         "生成器基于检索到的文档生成最终回答。"
    #     ]
    # }
]

class RAGASEvaluator:
    """RAGAS 评估器类"""

    def __init__(self):
        """初始化评估器"""
        self.client = RAGClient()
        self.evaluation_results = []
        self.ollama_models = ["deepseek-r1:1.5b", "deepseek-r1:7b", "qwen3:4b"]

    def get_ollama_llm(self):
        """
        获取可用的 Ollama 模型
        按顺序尝试调用模型，失败时自动切换到下一个

        Returns:
            可用的 Ollama 模型，如果所有模型都失败则返回 None
        """
        for model_name in self.ollama_models:
            try:
                logger.info(f"尝试连接 Ollama 模型: {model_name}")
                llm = Ollama(model=model_name, timeout=300)
                # 测试模型是否可用
                test_response = llm("Hello, world!")
                logger.info(f"成功连接 Ollama 模型: {model_name}")
                return llm
            except Exception as e:
                logger.error(f"模型 {model_name} 连接失败: {str(e)}")
                continue
        
        logger.error("所有 Ollama 模型都连接失败")
        return None

    @traceable
    def prepare_evaluation_data(self) -> List[Dict[str, Any]]:
        """
        准备评估数据

        Returns:
            List[Dict[str, Any]]: 评估数据集
        """
        evaluation_data = []

        for item in TEST_DATASET:
            try:
                question = item["question"]
                
                logger.info(f"开始处理问题: {question}")
                
                # 调用 RAG 客户端获取回答和检索到的上下文
                result = self.client.ask(question, k=2)
                
                # 提取检索到的文档信息
                sources = result.get("sources", [])
                num_documents = len(sources)
                document_ids = []
                
                # 尝试提取文档 ID（假设 sources 中的每个元素可能包含 id 字段）
                for i, source in enumerate(sources):
                    if isinstance(source, dict) and "id" in source:
                        document_ids.append(source["id"])
                    else:
                        # 如果没有 ID，使用索引作为标识
                        document_ids.append(f"doc_{i+1}")
                
                # 构建评估数据项
                eval_item = {
                    "question": question,
                    "answer": result.get("answer", ""),
                    "contexts": sources,
                    "ground_truth": item["ground_truth"]
                }
                
                evaluation_data.append(eval_item)
                logger.info(f"成功获取问题的回答: {question}")
                
            except Exception as e:
                logger.error(f"处理问题时出错: {item['question']}, 错误: {str(e)}")
                # 构建错误情况下的评估数据项
                eval_item = {
                    "question": item["question"],
                    "answer": "",
                    "contexts": [],
                    "ground_truth": item["ground_truth"]
                }
                evaluation_data.append(eval_item)

        return evaluation_data

    @traceable
    def evaluate(self) -> Dict[str, Any]:
        """
        执行 RAGAS 评估

        Returns:
            Dict[str, Any]: 评估结果
        """
        try:
            # 准备评估数据
            evaluation_data = self.prepare_evaluation_data()

            if not evaluation_data:
                logger.error("没有有效的评估数据")
                return {"error": "没有有效的评估数据"}

            # 转换为 datasets.Dataset
            dataset = datasets.Dataset.from_list(evaluation_data)

            # 强制使用 Ollama 模型，避免 OpenAI API 调用失败
            use_ollama = True

            if use_ollama:
                logger.info("OpenAI API 密钥缺失，尝试使用本地 Ollama 模型")
                # 获取可用的 Ollama 模型
                ollama_llm = self.get_ollama_llm()
                if not ollama_llm:
                    return {"error": "所有 Ollama 模型都连接失败，无法执行评估"}

                # 执行简单的自定义评估
                logger.info("使用 Ollama 模型执行自定义评估...")
                results = self._evaluate_with_ollama(dataset, ollama_llm)
            else:
                # 尝试使用 OpenAI 模型执行标准 RAGAS 评估
                try:
                    logger.info("使用 OpenAI 模型执行 RAGAS 评估...")
                    # 定义评估指标
                    metrics = [
                        faithfulness,
                        answer_relevancy,
                        context_precision,
                        context_recall
                    ]

                    # 执行评估
                    logger.info("开始执行 RAGAS 评估...")
                    results = evaluate(
                        dataset=dataset,
                        metrics=metrics
                    )
                except Exception as e:
                    logger.error(f"OpenAI 模型评估失败: {str(e)}")
                    # 切换到 Ollama 模型
                    logger.info("OpenAI 模型评估失败，尝试使用本地 Ollama 模型")
                    ollama_llm = self.get_ollama_llm()
                    if not ollama_llm:
                        return {"error": "所有 Ollama 模型都连接失败，无法执行评估"}

                    # 执行简单的自定义评估
                    logger.info("使用 Ollama 模型执行自定义评估...")
                    results = self._evaluate_with_ollama(dataset, ollama_llm)

            logger.info("评估完成")
            
            # 评估结果将通过函数返回值自动作为追踪记录的输出内容
            return results

        except Exception as e:
            logger.error(f"评估过程出错: {str(e)}")
            return {"error": str(e)}

    def _extract_score(self, response):
        """
        从模型响应中提取数字分数

        Args:
            response: 模型响应文本

        Returns:
            float: 提取的分数
        """
        import re
        # 查找响应中的数字（包括小数）
        matches = re.findall(r'\b\d+\.?\d*\b', response)
        if matches:
            # 尝试转换为浮点数
            for match in matches:
                try:
                    return float(match)
                except ValueError:
                    continue
        # 如果没有找到有效数字，返回默认值 0.0
        return 0.0

    def _evaluate_with_ollama(self, dataset, ollama_llm):
        """
        使用 Ollama 模型执行评估

        Args:
            dataset: 评估数据集
            ollama_llm: Ollama 模型实例

        Returns:
            Dict[str, Any]: 评估结果
        """
        evaluation_results = []
        total_faithfulness = 0.0
        total_answer_relevancy = 0.0
        total_context_precision = 0.0
        total_context_recall = 0.0

        for item in dataset:
            question = item["question"]
            answer = item["answer"]
            contexts = item["contexts"]
            ground_truth = item["ground_truth"]

            try:
                # 简单的评估逻辑
                # 1. 忠实度评估
                faithfulness_prompt = f"评估以下回答是否忠实于上下文：\n上下文：{contexts}\n回答：{answer}\n请给出 0-1 之间的分数，0 表示完全不忠实，1 表示完全忠实。只返回分数。"
                faithfulness_response = ollama_llm(faithfulness_prompt)
                faithfulness_score = self._extract_score(faithfulness_response)

                # 2. 回答相关性评估
                relevancy_prompt = f"评估以下回答与问题的相关性：\n问题：{question}\n回答：{answer}\n请给出 0-1 之间的分数，0 表示完全不相关，1 表示完全相关。只返回分数。"
                relevancy_response = ollama_llm(relevancy_prompt)
                answer_relevancy_score = self._extract_score(relevancy_response)

                # 3. 上下文精确率评估
                precision_prompt = f"评估以下上下文与问题的相关性：\n问题：{question}\n上下文：{contexts}\n请给出 0-1 之间的分数，0 表示完全不相关，1 表示完全相关。只返回分数。"
                precision_response = ollama_llm(precision_prompt)
                context_precision_score = self._extract_score(precision_response)

                # 4. 上下文召回率评估
                recall_prompt = f"评估以下上下文是否包含回答问题所需的所有信息：\n问题：{question}\n上下文：{contexts}\n请给出 0-1 之间的分数，0 表示完全不包含，1 表示完全包含。只返回分数。"
                recall_response = ollama_llm(recall_prompt)
                context_recall_score = self._extract_score(recall_response)

                # 累加分数
                total_faithfulness += faithfulness_score
                total_answer_relevancy += answer_relevancy_score
                total_context_precision += context_precision_score
                total_context_recall += context_recall_score

                # 保存单个评估结果
                eval_result = item.copy()
                eval_result["faithfulness"] = faithfulness_score
                eval_result["answer_relevancy"] = answer_relevancy_score
                eval_result["context_precision"] = context_precision_score
                eval_result["context_recall"] = context_recall_score
                evaluation_results.append(eval_result)

            except Exception as e:
                logger.error(f"评估问题时出错: {question}, 错误: {str(e)}")
                # 使用默认分数
                default_score = 0.0
                eval_result = item.copy()
                eval_result["faithfulness"] = default_score
                eval_result["answer_relevancy"] = default_score
                eval_result["context_precision"] = default_score
                eval_result["context_recall"] = default_score
                evaluation_results.append(eval_result)

        # 计算平均分数
        num_items = len(evaluation_results)
        if num_items > 0:
            avg_faithfulness = total_faithfulness / num_items
            avg_answer_relevancy = total_answer_relevancy / num_items
            avg_context_precision = total_context_precision / num_items
            avg_context_recall = total_context_recall / num_items
        else:
            avg_faithfulness = 0.0
            avg_answer_relevancy = 0.0
            avg_context_precision = 0.0
            avg_context_recall = 0.0

        # 构建评估结果
        results = {
            "faithfulness": avg_faithfulness,
            "answer_relevancy": avg_answer_relevancy,
            "context_precision": avg_context_precision,
            "context_recall": avg_context_recall,
            "dataset": evaluation_results
        }

        return results

    def print_evaluation_results(self, results: Dict[str, Any]):
        """
        打印评估结果

        Args:
            results: 评估结果
        """

        if "error" in results:
            print(f"评估出错: {results['error']}")
            return

        # 打印总体评估结果
        print("\n=== RAGAS 评估结果 ===")
        print("\n总体评估指标:")
        for metric, score in results.items():
            if metric != "dataset":
                print(f"{metric}: {score:.4f}")

        # 打印每个问题的评估结果
        print("\n每个问题的评估指标:")
        print("-" * 120)
        print(f"{'问题':<50} {'忠实度':<10} {'回答相关性':<12} {'上下文精确率':<12} {'上下文召回率':<12}")
        print("-" * 120)

        # 获取每个问题的评估结果
        dataset = results.get("dataset", None)
        if dataset:
            for i, item in enumerate(dataset):
                question = item["question"]
                faithfulness = item.get("faithfulness", 0.0)
                answer_relevancy = item.get("answer_relevancy", 0.0)
                context_precision = item.get("context_precision", 0.0)
                context_recall = item.get("context_recall", 0.0)

                # 截断问题文本
                truncated_question = question[:45] + "..." if len(question) > 45 else question

                print(f"{truncated_question:<50} {faithfulness:<10.4f} {answer_relevancy:<12.4f} {context_precision:<12.4f} {context_recall:<12.4f}")

        print("-" * 120)

    def get_langsmith_run_link(self) -> str:
        """
        获取 LangSmith 运行链接

        Returns:
            str: LangSmith 运行链接，如果不可用则返回空字符串
        """
        try:
            # 检查是否配置了 LangSmith
            if not os.getenv('LANGCHAIN_TRACING_V2') or os.getenv('LANGCHAIN_TRACING_V2') != 'true':
                return ""
            
            # 获取 LangSmith 项目名称
            project_name = os.getenv('LANGCHAIN_PROJECT', 'test_rag_evaluation')
            
            # 构建 LangSmith 链接
            langsmith_base_url = os.getenv('LANGCHAIN_ENDPOINT', 'https://smith.langchain.com')
            if not langsmith_base_url.endswith('/'):
                langsmith_base_url += '/'
            
            # 由于我们无法直接获取当前运行的 ID，这里返回一个通用的项目链接
            # 在实际运行中，LangSmith 会在日志中输出具体的运行链接
            run_link = f"{langsmith_base_url}projects/{project_name}"
            return run_link
        except Exception as e:
            logger.error(f"获取 LangSmith 链接失败: {str(e)}")
            return ""

def test_ragas_with_tracing():
    """测试 RAGAS 评估与 LangSmith 追踪"""
    try:
        # 初始化评估器
        evaluator = RAGASEvaluator()

        # 执行评估
        results = evaluator.evaluate()

        # 打印评估结果
        evaluator.print_evaluation_results(results)

        # 检查 LangSmith 追踪链接是否可用
        langsmith_link = evaluator.get_langsmith_run_link()
        if langsmith_link:
            print(f"\nLangSmith 运行链接: {langsmith_link}")
        else:
            logger.info("LangSmith 追踪链接不可用")

        # 验证评估结果
        assert "error" not in results, f"评估出错: {results.get('error', '未知错误')}"
        assert isinstance(results, dict), "评估结果应该是字典类型"
        assert "faithfulness" in results, "评估结果缺少忠实度指标"
        assert "answer_relevancy" in results, "评估结果缺少回答相关性指标"
        assert "context_precision" in results, "评估结果缺少上下文精确率指标"
        assert "context_recall" in results, "评估结果缺少上下文召回率指标"

    except Exception as e:
        logger.error(f"测试执行出错: {str(e)}")
        raise

def main():
    """主函数"""
    test_ragas_with_tracing()

if __name__ == "__main__":
    main()
