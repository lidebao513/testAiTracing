import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 打印环境变量
print("环境变量:")
print(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
print(f"LANGCHAIN_API_KEY: {os.getenv('LANGCHAIN_API_KEY')[:10]}...")
print(f"LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
print(f"LANGSMITH_ENDPOINT: {os.getenv('LANGSMITH_ENDPOINT')}")
