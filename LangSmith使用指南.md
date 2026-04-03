# LangSmith 使用指南

## 1. 模块概述

### 1.1 核心功能

LangSmith 是一个专为 LLM 应用设计的追踪、评估和监控平台，提供以下核心功能：

- **执行追踪**：详细记录 LLM 应用的每个组件执行情况，包括提示词、响应、执行时间等
- **性能评估**：对 LLM 模型的输出质量、速度、成本等进行评估
- **监控与分析**：实时监控应用性能，识别问题并提供优化建议
- **数据集管理**：管理和版本控制测试数据集
- **团队协作**：支持多用户协作，共享和分析追踪数据

### 1.2 价值定位

LangSmith 为 LLM 应用开发提供了以下价值：

- **可观测性**：提供完整的执行链路追踪，帮助开发者理解模型行为
- **质量保证**：通过评估框架确保模型输出质量
- **成本优化**：监控 token 使用和成本，帮助优化应用性能
- **开发效率**：加速调试和迭代过程，减少开发时间
- **合规性**：提供完整的审计 trail，满足合规要求

### 1.3 适用场景

LangSmith 适用于以下场景：

- **LLM 应用开发**：追踪和调试复杂的 LLM 应用
- **模型评估**：比较不同模型的性能和输出质量
- **生产环境监控**：监控部署的 LLM 应用性能
- **团队协作**：多人团队共同开发和维护 LLM 应用
- **教育和研究**：分析模型行为和性能

## 2. 环境要求与安装指南

### 2.1 支持的编程语言版本

- **Python**：3.8 或更高版本
- **Node.js**：16.0 或更高版本（如果使用 JavaScript/TypeScript SDK）

### 2.2 依赖包

#### Python 依赖

```
langsmith>=0.1.0
langchain>=0.3.0  # 可选，用于 LangChain 集成
python-dotenv>=1.0.0  # 用于加载环境变量
```

#### JavaScript/TypeScript 依赖

```
npm install langsmith
```

### 2.3 安装命令

#### Python 安装

```bash
# 安装 LangSmith
pip install langsmith

# 安装 LangChain 集成（可选）
pip install langchain

# 安装环境变量加载工具（推荐）
pip install python-dotenv
```

#### JavaScript/TypeScript 安装

```bash
npm install langsmith
```

## 3. 配置说明

### 3.1 API 密钥获取与设置方法

1. **访问 LangSmith 控制台**：打开 [https://smith.langchain.com](https://smith.langchain.com)
2. **注册或登录**：使用您的账户登录
3. **创建项目**：点击 "New Project" 创建一个新项目
4. **获取 API Key**：
   - 点击右上角的用户头像，选择 "Settings"
   - 在 "API Keys" 部分，点击 "Create API Key"
   - 复制生成的 API Key

### 3.2 环境变量配置

创建 `.env` 文件，添加以下环境变量：

```env
# LangSmith 配置
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_api_key_here
LANGCHAIN_PROJECT=your_project_name
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

其中：
- `LANGCHAIN_API_KEY`：您从 LangSmith 控制台获取的 API Key
- `LANGCHAIN_PROJECT`：您创建的项目名称
- `LANGCHAIN_TRACING_V2`：设置为 `true` 启用 LangSmith 追踪
- `LANGSMITH_ENDPOINT`：LangSmith API 端点，默认为 `https://api.smith.langchain.com`

### 3.3 验证配置

创建一个简单的验证脚本 `test_env.py`：

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 打印环境变量
print("环境变量配置：")
print(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
print(f"LANGCHAIN_API_KEY: {os.getenv('LANGCHAIN_API_KEY')[:10]}...")
print(f"LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
print(f"LANGSMITH_ENDPOINT: {os.getenv('LANGSMITH_ENDPOINT')}")

# 验证 API Key 是否设置
if not os.getenv('LANGCHAIN_API_KEY'):
    print("错误：未设置 LANGCHAIN_API_KEY")
else:
    print("配置验证成功！")
```

运行脚本验证配置是否正确：

```bash
python test_env.py
```

## 4. 核心功能使用教程

### 4.1 基本追踪

#### Python 示例

```python
from langsmith import Client
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 初始化 LangSmith 客户端
client = Client()

# 初始化模型
llm = ChatOllama(
    model="deepseek-r1:1.5b",
    temperature=0.7,
    base_url="http://localhost:11434"
)

# 创建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}")
])

# 创建输出解析器
output_parser = StrOutputParser()

# 构建处理链
chain = prompt | llm | output_parser

# 执行查询
response = chain.invoke({"question": "What is LangSmith?"})
print(f"响应: {response}")

# 查看追踪记录
print("\n追踪记录已保存到 LangSmith 控制台")
```

#### JavaScript/TypeScript 示例

```javascript
import { Client } from "langsmith";

// 初始化 LangSmith 客户端
const client = new Client();

// 记录追踪
async function runWithTracing() {
  const run = await client.createRun({
    projectName: "my-project",
    name: "test-query",
    runType: "chain",
  });
  
  // 执行你的 LLM 调用
  // ...
  
  // 结束追踪
  await client.updateRun(run.id, {
    status: "success",
    output: { answer: "LangSmith is a tracing and evaluation platform for LLM applications." },
  });
}

runWithTracing();
```

### 4.2 批量追踪

```python
from langsmith import Client
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 初始化模型和处理链
llm = ChatOllama(
    model="deepseek-r1:1.5b",
    temperature=0.7,
    base_url="http://localhost:11434"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}")
])

output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# 批量处理问题
questions = [
    "What is Python?",
    "What is LangChain?",
    "What is LangSmith?"
]

results = []
for question in questions:
    try:
        response = chain.invoke({"question": question})
        results.append({"question": question, "response": response, "status": "success"})
        print(f"处理问题: {question} - 成功")
    except Exception as e:
        results.append({"question": question, "error": str(e), "status": "failed"})
        print(f"处理问题: {question} - 失败: {str(e)}")

print("\n批量处理完成，所有追踪记录已保存到 LangSmith 控制台")
```

### 4.3 自定义追踪

```python
from langsmith import Client
from langsmith.tracing import traceable

client = Client()

@traceable

def custom_function(input_text):
    """自定义函数，将被 LangSmith 追踪"""
    # 执行一些操作
    result = input_text.upper()
    return result

# 调用自定义函数
result = custom_function("hello, langsmith!")
print(f"结果: {result}")
print("自定义函数执行已被追踪")
```

### 4.4 查看追踪记录

1. **访问 LangSmith 控制台**：打开 [https://smith.langchain.com](https://smith.langchain.com)
2. **选择项目**：在左侧导航栏中选择您的项目
3. **查看追踪记录**：点击 "Traces" 选项卡
4. **筛选和搜索**：使用筛选器和搜索功能找到特定的追踪记录
5. **查看详情**：点击任何追踪记录查看详细信息

## 5. 常见问题排查与解决方案

### 5.1 API Key 错误

**问题**：`AuthenticationError: Invalid API key`

**解决方案**：
- 检查 `.env` 文件中的 `LANGCHAIN_API_KEY` 是否正确
- 确保 API Key 没有过期
- 尝试重新生成 API Key 并更新配置

### 5.2 连接错误

**问题**：`ConnectionError: Could not connect to LangSmith API`

**解决方案**：
- 检查网络连接是否正常
- 确保 `LANGSMITH_ENDPOINT` 配置正确
- 检查防火墙设置是否阻止了连接

### 5.3 追踪记录未显示

**问题**：执行了 LLM 查询，但在 LangSmith 控制台中未看到追踪记录

**解决方案**：
- 检查 `LANGCHAIN_TRACING_V2` 是否设置为 `true`
- 确保 `LANGCHAIN_PROJECT` 名称正确
- 等待几秒钟，追踪记录可能需要时间同步
- 检查 API Key 权限是否正确

### 5.4 模型加载错误

**问题**：`ModelNotFoundError: Model not found`

**解决方案**：
- 确保 Ollama 服务正在运行
- 检查模型名称是否正确
- 运行 `ollama pull model-name` 拉取模型

### 5.5 超时错误

**问题**：`TimeoutError: Request timed out`

**解决方案**：
- 增加模型的 timeout 参数
- 检查网络连接速度
- 尝试使用更轻量级的模型

## 6. 最佳实践建议

### 6.1 项目管理

- **创建专门的项目**：为不同的应用或功能创建单独的项目，便于管理和分析
- **使用有意义的项目名称**：选择清晰、描述性的项目名称，便于识别
- **设置项目描述**：为每个项目添加描述，说明其用途和目标

### 6.2 追踪管理

- **添加标签**：为重要的追踪记录添加标签，便于分类和搜索
- **设置元数据**：为追踪记录添加元数据，包含额外的上下文信息
- **定期清理**：定期清理不需要的追踪记录，保持项目整洁

### 6.3 性能优化

- **批量处理**：对于多个相似的查询，使用批量处理减少 API 调用次数
- **合理设置超时**：根据模型和网络情况设置适当的超时时间
- **监控 token 使用**：跟踪 token 使用情况，优化提示词以减少成本

### 6.4 团队协作

- **设置项目权限**：根据团队成员的角色设置适当的权限
- **使用共享数据集**：创建和共享测试数据集，确保团队使用一致的评估标准
- **定期回顾**：定期回顾追踪记录和评估结果，持续改进模型和应用

### 6.5 安全性

- **保护 API Key**：不要在代码中硬编码 API Key，使用环境变量或安全的密钥管理系统
- **限制访问**：只向需要的团队成员授予项目访问权限
- **监控异常**：设置异常监控，及时发现和处理安全问题

## 7. 高级功能

### 7.1 评估框架

LangSmith 提供了强大的评估框架，可以评估模型的输出质量：

```python
from langsmith.evaluation import evaluate

# 定义评估数据集
dataset = [
    {"input": "What is Python?", "expected_output": "Python is a programming language"},
    {"input": "What is LangChain?", "expected_output": "LangChain is a framework for building LLM applications"},
]

# 评估模型
evaluate(
    dataset=dataset,
    llm=llm,
    metrics=["accuracy", "completeness"],
    project_name="my-evaluation-project"
)
```

### 7.2 自定义评估指标

```python
from langsmith.evaluation import EvaluationResult

def custom_metric(output, expected_output):
    """自定义评估指标"""
    score = 1.0 if expected_output in output else 0.0
    return EvaluationResult(
        score=score,
        reasoning=f"Output contains expected text: {expected_output in output}"
    )

# 使用自定义指标
evaluate(
    dataset=dataset,
    llm=llm,
    metrics=[custom_metric],
    project_name="my-evaluation-project"
)
```

### 7.3 监控仪表板

LangSmith 提供了实时监控仪表板，可以：
- 查看模型性能指标
- 监控 token 使用和成本
- 识别异常和问题
- 生成定期报告

## 8. 总结

LangSmith 是一个强大的 LLM 应用开发工具，通过提供全面的追踪、评估和监控功能，帮助开发者构建更高质量、更可靠的 LLM 应用。通过本指南的学习，您应该能够：

- 正确安装和配置 LangSmith
- 使用 LangSmith 追踪 LLM 应用的执行情况
- 分析和优化模型性能
- 与团队成员协作开发和维护 LLM 应用

随着 LLM 技术的不断发展，LangSmith 也在持续更新和改进，为开发者提供更多强大的功能和工具。建议定期访问 LangSmith 官方文档，了解最新的功能和最佳实践。

## 9. 参考资源

- **LangSmith 官方文档**：[https://docs.smith.langchain.com](https://docs.smith.langchain.com)
- **LangSmith 控制台**：[https://smith.langchain.com](https://smith.langchain.com)
- **LangChain 文档**：[https://docs.langchain.com](https://docs.langchain.com)
- **Ollama 文档**：[https://ollama.com/docs](https://ollama.com/docs)
