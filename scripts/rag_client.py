#!/usr/bin/env python3
"""
RAG Client 模块
用于与 RAG 应用 API 进行交互
"""

import os
import time
import json
import logging
from typing import Dict, List, Optional, Any, Generator, Union
import requests
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 自定义异常类
class RAGClientError(Exception):
    """RAG 客户端异常"""
    pass

class RAGClient:
    """RAG 客户端类，用于与 RAG 应用 API 进行交互"""

    def __init__(self, base_url: Optional[str] = None):
        """
        初始化 RAG 客户端

        Args:
            base_url: API 基础地址，若未提供则从环境变量 RAG_APP_API_URL 读取

        Raises:
            RAGClientError: 当未提供 base_url 且环境变量 RAG_APP_API_URL 不存在时
        """
        # 加载环境变量
        load_dotenv('config/env/.env')

        # 优先使用传入的 base_url，否则从环境变量读取
        self.base_url = base_url or os.getenv('RAG_APP_API_URL')
        
        if not self.base_url:
            raise RAGClientError("未提供 base_url 且环境变量 RAG_APP_API_URL 不存在")
        
        # 确保 base_url 以 / 结尾
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        
        # 初始化 session
        self.session = requests.Session()
        self.session.timeout = 30  # 设置默认超时时间
        
        logger.info(f"RAG 客户端初始化成功，API 地址: {self.base_url}")

    def _request_with_retry(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        带重试机制的请求方法

        Args:
            method: HTTP 方法（GET, POST 等）
            endpoint: API 端点
            **kwargs: 请求参数

        Returns:
            requests.Response: 响应对象

        Raises:
            RAGClientError: 当请求失败且重试次数耗尽时
        """
        max_retries = 3
        base_delay = 1  # 基础延迟时间（秒）
        
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}{endpoint}"
                logger.info(f"发送 {method} 请求到 {url}")
                
                response = self.session.request(method, url, **kwargs)
                
                # 检查响应状态码
                if 400 <= response.status_code < 500:
                    # 4xx 错误，不重试
                    response.raise_for_status()
                elif response.status_code >= 500:
                    # 5xx 错误，重试
                    raise RAGClientError(f"服务器错误: {response.status_code}")
                
                return response
                
            except (requests.ConnectionError, requests.Timeout, RAGClientError) as e:
                if attempt < max_retries - 1:
                    # 计算指数退避时间
                    delay = base_delay * (2 ** attempt) + (attempt * 0.1)
                    logger.warning(f"请求失败（{attempt + 1}/{max_retries}）: {str(e)}，等待 {delay:.2f} 秒后重试")
                    time.sleep(delay)
                else:
                    # 重试次数耗尽
                    raise RAGClientError(f"请求失败，重试次数耗尽: {str(e)}") from e
            except Exception as e:
                # 其他异常，不重试
                raise RAGClientError(f"请求失败: {str(e)}") from e

    def health_check(self) -> bool:
        """
        健康检查

        Returns:
            bool: 服务是否正常（200 OK 状态视为正常）
        """
        try:
            response = self._request_with_retry('GET', 'health')
            return response.status_code == 200
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return False

    def ask(self, question: str, k: int = 4, temperature: float = 0.3) -> Dict[str, Union[str, List[Any]]]:
        """
        发送问答请求

        Args:
            question: 问题
            k: 检索的文档数量
            temperature: 生成温度

        Returns:
            Dict[str, Union[str, List[Any]]]: 包含 answer（字符串）和 sources（列表）的字典

        Raises:
            RAGClientError: 当请求失败时
        """
        try:
            # 构建请求数据
            data = {
                'question': question,
                'k': k,
                'temperature': temperature
            }
            
            # 发送请求
            response = self._request_with_retry('POST', 'ask', json=data)
            
            # 解析响应
            result = response.json()
            
            # 验证响应结构
            if 'answer' not in result or 'sources' not in result:
                raise RAGClientError("响应格式错误，缺少 answer 或 sources 字段")
            
            return result
            
        except json.JSONDecodeError as e:
            raise RAGClientError(f"JSON 解析错误: {str(e)}") from e
        except Exception as e:
            raise RAGClientError(f"问答请求失败: {str(e)}") from e

    def ask_stream(self, question: str, k: int = 4, temperature: float = 0.3) -> Generator[str, None, None]:
        """
        流式问答功能

        Args:
            question: 问题
            k: 检索的文档数量
            temperature: 生成温度

        Yields:
            str: 生成的文本块

        Raises:
            RAGClientError: 当请求失败时
        """
        try:
            # 构建请求数据
            data = {
                'question': question,
                'k': k,
                'temperature': temperature
            }
            
            # 发送流式请求
            url = f"{self.base_url}ask/stream"
            logger.info(f"发送流式 POST 请求到 {url}")
            
            with self.session.post(url, json=data, stream=True) as response:
                # 检查响应状态码
                response.raise_for_status()
                
                # 处理流式响应
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        try:
                            # 解析每个块
                            chunk_str = chunk.decode('utf-8')
                            yield chunk_str
                        except UnicodeDecodeError as e:
                            logger.warning(f"解码错误: {str(e)}")
                            continue
                            
        except Exception as e:
            raise RAGClientError(f"流式问答请求失败: {str(e)}") from e

if __name__ == "__main__":
    """使用示例"""
    try:
        # 初始化客户端
        client = RAGClient()
        
        # 健康检查
        print("=== 健康检查 ===")
        is_healthy = client.health_check()
        print(f"服务状态: {'正常' if is_healthy else '异常'}")
        
        if is_healthy:
            # 普通问答
            print("\n=== 普通问答 ===")
            question = "什么是 RAG 技术？"
            result = client.ask(question)
            print(f"问题: {question}")
            print(f"回答: {result['answer']}")
            print(f"来源: {len(result['sources'])} 个文档")
            
            # 流式问答（如果实现）
            print("\n=== 流式问答 ===")
            question = "RAG 技术的应用场景有哪些？"
            print(f"问题: {question}")
            print("回答:", end=" ")
            for chunk in client.ask_stream(question):
                print(chunk, end="", flush=True)
            print()
            
    except RAGClientError as e:
        print(f"错误: {str(e)}")
    except Exception as e:
        print(f"未知错误: {str(e)}")
