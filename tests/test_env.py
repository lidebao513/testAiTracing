import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 检查必要的环境变量
required_vars = ['LANGCHAIN_TRACING_V2', 'LANGCHAIN_API_KEY', 'LANGCHAIN_PROJECT']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")

# 打印环境变量信息
print("环境变量加载成功:")
print(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
print(f"LANGCHAIN_API_KEY (前10位): {os.getenv('LANGCHAIN_API_KEY')[:10]}...")
print(f"LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
