#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAGAS with LangSmith Integration
兼容 RAGAS 0.2.0+ 版本
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 检查 LangSmith 配置
required_env_vars = ["LANGCHAIN_API_KEY", "LANGCHAIN_PROJECT"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"⚠️ 警告: 缺少环境变量 {missing_vars}")
    print("请确保 .env 文件包含 LANGCHAIN_API_KEY 和 LANGCHAIN_PROJECT")
else:
    print(f"✅ LangSmith 项目: {os.getenv('LANGCHAIN_PROJECT')}")
    print(f"✅ LangSmith API Key: {os.getenv('LANGCHAIN_API_KEY')[:15]}...")

import ragas
print(f"📦 RAGAS 版本: {ragas.__version__}")

from datasets import Dataset
from ragas import evaluate
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from langchain_ollama import ChatOllama

# 尝试导入新版本的指标
try:
    # RAGAS 0.2.0+ 新导入方式
    from ragas.metrics.collections import Faithfulness, AnswerRelevancy
    from ragas.metrics import ContextPrecision, ContextRecall
    print("✅ 使用 RAGAS 0.2.0+ 新 API")
except ImportError:
    try:
        # RAGAS 0.1.x 旧导入方式（兼容）
        from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
        Faithfulness = faithfulness
        AnswerRelevancy = answer_relevancy
        ContextPrecision = context_precision
        ContextRecall = context_recall
        print("✅ 使用 RAGAS 0.1.x 兼容模式")
    except ImportError:
        # 如果都不行，使用基础指标
        from ragas.metrics import faithfulness
        Faithfulness = faithfulness
        AnswerRelevancy = None
        ContextPrecision = None
        ContextRecall = None
        print("⚠️ 使用基础指标模式")

# 初始化本地 LLM（用于评估）
try:
    llm = ChatOllama(
        model="deepseek-r1:7b",
        temperature=0,
        base_url="http://localhost:11434",
    )
    print("✅ 本地 Ollama 模型连接成功")
except Exception as e:
    print(f"⚠️ Ollama 连接失败: {e}")
    llm = None


@traceable(name="ragas_evaluation")
def run_ragas_evaluation():
    """
    运行 RAGAS 评估并发送到 LangSmith
    """
    # 创建示例数据集
    data = {
        "question": [
            "What is the capital of France?",
            "What is the chemical symbol for water?",
            "Who wrote Romeo and Juliet?"
        ],
        "answer": [
            "The capital of France is Paris.",
            "H2O is the chemical symbol for water.",
            "William Shakespeare wrote Romeo and Juliet."
        ],
        "contexts": [
            ["Paris is the capital and most populous city of France."],
            ["Water has the chemical formula H2O, consisting of two hydrogen atoms and one oxygen atom."],
            ["Romeo and Juliet is a tragedy written by William Shakespeare."]
        ],
        "ground_truth": [
            "Paris",
            "H2O",
            "William Shakespeare"
        ]
    }
    
    # 转换为 Dataset 对象
    dataset = Dataset.from_dict(data)
    print(f"📊 数据集大小: {len(dataset)} 条记录")
    
    # 准备要使用的指标
    metrics_to_use = []
    
    if Faithfulness is not None:
        metrics_to_use.append(Faithfulness(llm=llm))
        print("  - Faithfulness (忠实度)")
    
    if AnswerRelevancy is not None:
        metrics_to_use.append(AnswerRelevancy(llm=llm))
        print("  - AnswerRelevancy (答案相关性)")
    
    if ContextPrecision is not None:
        metrics_to_use.append(ContextPrecision(llm=llm))
        print("  - ContextPrecision (上下文精确度)")
    
    if ContextRecall is not None:
        metrics_to_use.append(ContextRecall(llm=llm))
        print("  - ContextRecall (上下文召回率)")
    
    if not metrics_to_use:
        print("❌ 没有可用的评估指标")
        return None
    
    print(f"\n🚀 开始评估，使用 {len(metrics_to_use)} 个指标...")
    
    # 运行评估
    try:
        # 如果有本地 LLM，传递给评估器
        if llm:
            result = evaluate(
                dataset=dataset,
                metrics=metrics_to_use,
                llm=llm,  # 使用本地模型进行评估
            )
        else:
            result = evaluate(
                dataset=dataset,
                metrics=metrics_to_use,
            )
        
        print("\n✅ 评估完成！")
        print("\n📈 评估结果:")
        
        # 转换为 DataFrame 以便查看
        result_df = result.to_pandas()
        print(result_df)
        
        # 计算平均分
        print("\n📊 平均分数:")
        for metric_name in result_df.columns:
            if metric_name not in ['question', 'answer', 'contexts', 'ground_truth']:
                avg_score = result_df[metric_name].mean()
                print(f"  {metric_name}: {avg_score:.4f}")
        
        return result
        
    except Exception as e:
        print(f"❌ 评估失败: {e}")
        import traceback
        traceback.print_exc()
        return None


@traceable(name="simple_rag_test")
def simple_rag_test(question: str, context: str) -> str:
    """
    简单的 RAG 测试函数
    """
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有帮助的助手。请根据以下上下文回答问题：\n{context}"),
        ("human", "{question}")
    ])
    
    if llm:
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"context": context, "question": question})
        return response
    else:
        return "由于 Ollama 未连接，返回模拟回答。"


if __name__ == "__main__":
    print("=" * 60)
    print("RAGAS with LangSmith Integration")
    print("=" * 60)
    
    # 测试简单的 RAG 调用
    print("\n1️⃣ 测试简单 RAG 调用...")
    test_response = simple_rag_test(
        "What is the capital of France?",
        "Paris is the capital of France. It is known for the Eiffel Tower."
    )
    print(f"   响应: {test_response[:100]}...")
    
    # 运行完整的 RAGAS 评估
    print("\n2️⃣ 运行 RAGAS 评估...")
    result = run_ragas_evaluation()
    
    print("\n" + "=" * 60)
    print("✅ 脚本执行完成")
    print(f"📝 请登录 LangSmith 控制台查看追踪记录:")
    print(f"   https://smith.langchain.com/projects/{os.getenv('LANGCHAIN_PROJECT', 'default')}")
    print("=" * 60)