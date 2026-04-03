#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAGAS with LangSmith Integration
RAGAS评估框架与LangSmith跟踪集成脚本

功能说明:
- 使用RAGAS框架评估RAG系统性能
- 集成LangSmith进行全流程跟踪
- 支持本地Ollama模型进行评估
- 包含完整的错误处理和日志记录

作者: AI Assistant
版本: 1.0.0
日期: 2026-04-03
"""

import os
import sys
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ragas_evaluation.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# 1. 环境配置
# =============================================================================

def load_environment() -> bool:
    """
    加载环境变量并验证LangSmith配置
    
    Returns:
        bool: 环境变量加载是否成功
    """
    try:
        from dotenv import load_dotenv
        
        # 加载.env文件
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logger.info(f"✅ 已加载环境变量文件: {env_path}")
        else:
            load_dotenv()  # 尝试从当前目录加载
            logger.info("✅ 已从当前目录加载环境变量")
        
        # 兼容LANGCHAIN_ENDPOINT和LANGSMITH_ENDPOINT
        if os.getenv('LANGSMITH_ENDPOINT') and not os.getenv('LANGCHAIN_ENDPOINT'):
            os.environ['LANGCHAIN_ENDPOINT'] = os.getenv('LANGSMITH_ENDPOINT')
            logger.info("✅ 已兼容LANGSMITH_ENDPOINT到LANGCHAIN_ENDPOINT")
        
        # 设置默认值
        if not os.getenv('LANGCHAIN_ENDPOINT'):
            os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
            logger.info("✅ 已设置默认LANGCHAIN_ENDPOINT")
        
        # 检查必需的LangSmith环境变量
        required_vars = {
            'LANGCHAIN_API_KEY': 'LangSmith API密钥',
            'LANGCHAIN_TRACING_V2': 'LangSmith跟踪开关',
            'LANGCHAIN_PROJECT': 'LangSmith项目名称'
        }
        
        missing_vars = []
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value:
                missing_vars.append(f"{var} ({description})")
            else:
                # 安全地打印部分信息
                if 'API_KEY' in var:
                    logger.info(f"✅ {var}: {value[:10]}...")
                else:
                    logger.info(f"✅ {var}: {value}")
        
        if missing_vars:
            logger.warning(f"⚠️ 缺少以下环境变量:\n" + "\n".join(f"  - {v}" for v in missing_vars))
            logger.info("请确保.env文件包含所有必需的配置")
            return False
        
        # 显示端点信息
        logger.info(f"✅ LANGCHAIN_ENDPOINT: {os.getenv('LANGCHAIN_ENDPOINT')}")
        
        # 设置LangSmith跟踪
        os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        logger.info("✅ LangSmith跟踪已启用")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ 缺少必需的库: {e}")
        logger.info("请安装: pip install python-dotenv")
        return False
    except Exception as e:
        logger.error(f"❌ 加载环境变量时出错: {e}")
        return False


# =============================================================================
# 2. 模块导入
# =============================================================================

def import_modules() -> Dict[str, Any]:
    """
    导入所有必需的模块
    
    Returns:
        Dict[str, Any]: 导入的模块字典
    """
    modules = {}
    
    try:
        # RAGAS相关
        import ragas
        modules['ragas'] = ragas
        logger.info(f"📦 RAGAS版本: {ragas.__version__}")
        
        from datasets import Dataset
        modules['Dataset'] = Dataset
        
        from ragas import evaluate
        modules['evaluate'] = evaluate
        
        # LangSmith相关
        from langsmith import traceable, Client
        modules['traceable'] = traceable
        modules['Client'] = Client
        
        # LangChain相关
        from langchain_ollama import ChatOllama
        modules['ChatOllama'] = ChatOllama
        
        from langchain_core.prompts import ChatPromptTemplate
        modules['ChatPromptTemplate'] = ChatPromptTemplate
        
        from langchain_core.output_parsers import StrOutputParser
        modules['StrOutputParser'] = StrOutputParser
        
        logger.info("✅ 所有模块导入成功")
        return modules
        
    except ImportError as e:
        logger.error(f"❌ 模块导入失败: {e}")
        logger.info("请安装必需的依赖: pip install ragas datasets langsmith langchain-ollama")
        raise


def import_metrics() -> Dict[str, Any]:
    """
    导入RAGAS评估指标
    
    Returns:
        Dict[str, Any]: 指标函数字典
    """
    metrics = {}
    
    try:
        # 尝试RAGAS 0.4.x导入方式 - 这些已经是实例对象
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness
        )
        # 直接存储实例对象
        metrics['answer_relevancy'] = answer_relevancy
        metrics['context_precision'] = context_precision
        metrics['context_recall'] = context_recall
        metrics['faithfulness'] = faithfulness
        logger.info("✅ 使用RAGAS 0.4.x指标导入方式（实例对象）")
        
    except ImportError:
        try:
            # 尝试RAGAS 0.2.0+新导入方式 - 这些是类，需要实例化
            from ragas.metrics.collections import (
                AnswerRelevancy,
                ContextPrecision,
                ContextRecall,
                Faithfulness
            )
            # 存储类，稍后实例化
            metrics['answer_relevancy'] = AnswerRelevancy
            metrics['context_precision'] = ContextPrecision
            metrics['context_recall'] = ContextRecall
            metrics['faithfulness'] = Faithfulness
            logger.info("✅ 使用RAGAS 0.2.0+新指标导入方式（类）")
            
        except ImportError:
            logger.warning("⚠️ 无法导入所有指标，将使用基础指标")
            from ragas.metrics import faithfulness
            metrics['faithfulness'] = faithfulness
    
    return metrics


# =============================================================================
# 3. 评估数据集创建
# =============================================================================

def create_evaluation_dataset() -> Any:
    """
    创建RAGAS评估数据集
    
    创建包含5个样本的评估数据集，每个样本包含:
    - question: 问题
    - contexts: 上下文列表
    - answer: 生成的答案
    - ground_truth: 参考答案
    
    Returns:
        Dataset: RAGAS评估数据集
    """
    logger.info("📊 正在创建评估数据集...")
    
    data = {
        "question": [
            "What is the capital of France?",
            "What is the chemical symbol for water?",
            "Who wrote Romeo and Juliet?",
            "What is the largest planet in our solar system?",
            "In which year did World War II end?"
        ],
        "contexts": [
            ["Paris is the capital and most populous city of France. It is located on the Seine River."],
            ["Water has the chemical formula H2O, consisting of two hydrogen atoms and one oxygen atom."],
            ["Romeo and Juliet is a tragedy written by William Shakespeare early in his career."],
            ["Jupiter is the largest planet in our solar system. It is a gas giant with a mass one-thousandth that of the Sun."],
            ["World War II ended in 1945 with the surrender of Germany in May and Japan in September."]
        ],
        "answer": [
            "The capital of France is Paris.",
            "H2O is the chemical symbol for water.",
            "William Shakespeare wrote Romeo and Juliet.",
            "Jupiter is the largest planet in our solar system.",
            "World War II ended in 1945."
        ],
        "ground_truth": [
            "Paris",
            "H2O",
            "William Shakespeare",
            "Jupiter",
            "1945"
        ]
    }
    
    from datasets import Dataset
    dataset = Dataset.from_dict(data)
    
    logger.info(f"✅ 评估数据集创建成功: {len(dataset)} 条记录")
    logger.info(f"   字段: {list(dataset.features.keys())}")
    
    return dataset


# =============================================================================
# 4. RAGAS评估执行
# =============================================================================

def setup_metrics(metrics_dict: Dict[str, Any]) -> List[Any]:
    """
    配置RAGAS评估指标
    
    Args:
        metrics_dict: 导入的指标函数字典
        
    Returns:
        List[Any]: 配置的指标列表
    """
    logger.info("🔧 正在配置评估指标...")
    
    metrics_to_use = []
    required_metrics = ['answer_relevancy', 'context_precision', 'context_recall']
    
    for metric_name in required_metrics:
        if metric_name in metrics_dict:
            try:
                metric = metrics_dict[metric_name]
                # 如果是类（需要实例化），则调用；如果是实例对象，则直接使用
                if callable(metric) and not hasattr(metric, 'name'):
                    metric = metric()
                metrics_to_use.append(metric)
                logger.info(f"   ✅ {metric_name}")
            except Exception as e:
                logger.warning(f"   ⚠️ {metric_name} 配置失败: {e}")
        else:
            logger.warning(f"   ⚠️ {metric_name} 不可用")
    
    # 添加可选指标
    if 'faithfulness' in metrics_dict:
        try:
            metric = metrics_dict['faithfulness']
            # 如果是类（需要实例化），则调用；如果是实例对象，则直接使用
            if callable(metric) and not hasattr(metric, 'name'):
                metric = metric()
            metrics_to_use.append(metric)
            logger.info(f"   ✅ faithfulness (附加指标)")
        except Exception as e:
            logger.warning(f"   ⚠️ faithfulness 配置失败: {e}")
    
    if not metrics_to_use:
        raise ValueError("没有可用的评估指标，请检查RAGAS安装")
    
    logger.info(f"✅ 成功配置 {len(metrics_to_use)} 个评估指标")
    return metrics_to_use


# =============================================================================
# 5. LangSmith跟踪集成
# =============================================================================

def setup_langsmith_tracking() -> Optional[Any]:
    """
    配置LangSmith跟踪
    
    Returns:
        Optional[Client]: LangSmith客户端实例
    """
    try:
        from langsmith import Client
        
        client = Client()
        project_name = os.getenv('LANGCHAIN_PROJECT', 'ragas-evaluation')
        
        logger.info(f"✅ LangSmith客户端初始化成功")
        logger.info(f"   项目: {project_name}")
        logger.info(f"   端点: {os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')}")
        
        return client
        
    except Exception as e:
        logger.warning(f"⚠️ LangSmith客户端初始化失败: {e}")
        return None


def get_trace_url(client: Any, run_id: str) -> Optional[str]:
    """
    获取LangSmith跟踪链接
    
    Args:
        client: LangSmith客户端
        run_id: 运行ID
        
    Returns:
        Optional[str]: 跟踪链接
    """
    try:
        if client and run_id:
            project = os.getenv('LANGCHAIN_PROJECT', 'default')
            return f"https://smith.langchain.com/projects/{project}/runs/{run_id}"
    except Exception as e:
        logger.warning(f"⚠️ 获取跟踪链接失败: {e}")
    
    return None


# =============================================================================
# 6. 评估执行与结果处理
# =============================================================================

def run_evaluation(
    dataset: Any,
    metrics: List[Any],
    llm: Optional[Any] = None
) -> Optional[Any]:
    """
    执行RAGAS评估
    
    Args:
        dataset: 评估数据集
        metrics: 评估指标列表
        llm: 可选的LLM实例
        
    Returns:
        Optional[Any]: 评估结果
    """
    logger.info("\n🚀 开始执行RAGAS评估...")
    logger.info(f"   数据集大小: {len(dataset)} 条记录")
    logger.info(f"   评估指标数: {len(metrics)} 个")
    
    try:
        from ragas import evaluate
        
        # 执行评估
        start_time = datetime.now()
        
        result = evaluate(
            dataset=dataset,
            metrics=metrics,
            raise_exceptions=False  # 不抛出异常，继续评估
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"✅ 评估完成! 耗时: {duration:.2f}秒")
        return result
        
    except Exception as e:
        logger.error(f"❌ 评估执行失败: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None


def format_results(result: Any) -> Dict[str, float]:
    """
    格式化评估结果
    
    Args:
        result: RAGAS评估结果
        
    Returns:
        Dict[str, float]: 格式化的结果字典
    """
    if result is None:
        return {}
    
    try:
        import pandas as pd
        
        result_df = result.to_pandas()
        formatted_results = {}
        
        logger.info("\n" + "="*60)
        logger.info("📈 详细评估结果")
        logger.info("="*60)
        
        # 打印详细结果
        for idx, row in result_df.iterrows():
            logger.info(f"\n样本 {idx + 1}:")
            logger.info(f"  问题: {row.get('question', 'N/A')}")
            logger.info(f"  答案: {row.get('answer', 'N/A')[:50]}...")
            
            for col in result_df.columns:
                if col not in ['question', 'answer', 'contexts', 'ground_truth']:
                    score = row.get(col)
                    if pd.notna(score):
                        logger.info(f"  {col}: {score:.4f}")
        
        # 计算平均分
        logger.info("\n" + "-"*60)
        logger.info("📊 平均分数:")
        logger.info("-"*60)
        
        for col in result_df.columns:
            if col not in ['question', 'answer', 'contexts', 'ground_truth']:
                avg_score = result_df[col].mean()
                if pd.notna(avg_score):
                    formatted_results[col] = avg_score
                    logger.info(f"  {col:25s}: {avg_score:.4f}")
        
        # 总体评估结论
        if formatted_results:
            overall_score = sum(formatted_results.values()) / len(formatted_results)
            logger.info("-"*60)
            logger.info(f"  {'总体评分':25s}: {overall_score:.4f}")
            
            if overall_score >= 0.8:
                conclusion = "优秀 🌟"
            elif overall_score >= 0.6:
                conclusion = "良好 ✅"
            elif overall_score >= 0.4:
                conclusion = "一般 ⚠️"
            else:
                conclusion = "需要改进 ❌"
            
            logger.info(f"  {'评估结论':25s}: {conclusion}")
        
        logger.info("="*60)
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"❌ 格式化结果时出错: {e}")
        return {}


# =============================================================================
# 主函数
# =============================================================================

def main():
    """
    主函数: 执行完整的RAGAS评估流程
    """
    print("\n" + "="*70)
    print("🚀 RAGAS with LangSmith Integration")
    print("   RAGAS评估框架与LangSmith跟踪集成")
    print("="*70)
    
    try:
        # 1. 加载环境变量
        if not load_environment():
            logger.error("❌ 环境变量加载失败，请检查.env文件配置")
            return 1
        
        # 2. 导入模块
        modules = import_modules()
        metrics_dict = import_metrics()
        
        # 3. 配置LangSmith跟踪
        langsmith_client = setup_langsmith_tracking()
        
        # 4. 创建评估数据集
        dataset = create_evaluation_dataset()
        
        # 5. 配置评估指标
        metrics = setup_metrics(metrics_dict)
        
        # 6. 初始化LLM（可选）
        llm = None
        try:
            llm = modules['ChatOllama'](
                model="deepseek-r1:7b",
                temperature=0,
                base_url="http://localhost:11434"
            )
            logger.info("✅ Ollama LLM初始化成功")
        except Exception as e:
            logger.warning(f"⚠️ Ollama LLM初始化失败: {e}")
            logger.info("   将继续使用默认评估方式")
        
        # 7. 执行评估
        result = run_evaluation(dataset, metrics, llm)
        
        if result is None:
            logger.error("❌ 评估执行失败")
            return 1
        
        # 8. 格式化并输出结果
        formatted_results = format_results(result)
        
        # 9. 输出LangSmith跟踪信息
        print("\n" + "="*70)
        print("🔗 LangSmith跟踪信息")
        print("="*70)
        
        project = os.getenv('LANGCHAIN_PROJECT', 'default')
        base_url = "https://smith.langchain.com"
        
        print(f"\n项目: {project}")
        print(f"控制台: {base_url}/projects/{project}")
        
        # 尝试获取跟踪链接
        if langsmith_client:
            try:
                runs = list(langsmith_client.list_runs(
                    project_name=project,
                    limit=1
                ))
                if runs:
                    run_id = runs[0].id
                    trace_url = f"{base_url}/projects/{project}/runs/{run_id}"
                    print(f"最新跟踪: {trace_url}")
            except Exception as e:
                logger.debug(f"获取最新运行ID失败: {e}")
        
        print("="*70)
        
        # 10. 完成
        print("\n✅ 脚本执行完成!")
        print(f"📁 日志文件: ragas_evaluation.log")
        print(f"📝 请登录LangSmith控制台查看详细的跟踪记录")
        print("="*70 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ 用户中断执行")
        return 130
    except Exception as e:
        logger.error(f"\n❌ 脚本执行出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
