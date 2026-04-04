#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAGAS 简单评估脚本
兼容 RAGAS 0.4.3 版本
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
else:
    print(f"✅ LangSmith 项目: {os.getenv('LANGCHAIN_PROJECT')}")

import ragas
print(f"📦 RAGAS 版本: {ragas.__version__}")

from datasets import Dataset
from ragas import evaluate

# 尝试导入新版本的指标
try:
    # RAGAS 0.4.x 新导入方式
    from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
    print("✅ 使用 RAGAS 0.4.x API")
except ImportError as e:
    print(f"❌ 导入指标失败: {e}")
    raise

# 创建示例数据集
data = {
    "question": [
        "What is the capital of France?",
        "What is the chemical symbol for water?",
    ],
    "answer": [
        "The capital of France is Paris.",
        "H2O is the chemical symbol for water.",
    ],
    "contexts": [
        ["Paris is the capital and most populous city of France."],
        ["Water has the chemical formula H2O, consisting of two hydrogen atoms and one oxygen atom."],
    ],
    "ground_truth": [
        "Paris",
        "H2O",
    ]
}

# 转换为 Dataset 对象
dataset = Dataset.from_dict(data)
print(f"📊 数据集大小: {len(dataset)} 条记录")

# 准备要使用的指标
metrics_to_use = [
    Faithfulness(),
    AnswerRelevancy(),
    ContextPrecision(),
    ContextRecall(),
]

print(f"\n🚀 开始评估，使用 {len(metrics_to_use)} 个指标...")

# 运行评估
try:
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
    
except Exception as e:
    print(f"❌ 评估失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ 脚本执行完成")
print("=" * 60)
