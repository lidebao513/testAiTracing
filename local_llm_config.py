#!/usr/bin/env python3
"""
本地大模型调用配置模块

功能：
1. 基于Ollama接口的本地大模型调用系统
2. 实现自动故障转移机制
3. 配置完整的模型调用参数
4. 多层次错误检测和重试策略
5. 详细日志记录
"""

import logging
import time
from typing import Optional, Dict, Any, List
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LocalLLMConfig:
    """本地大模型配置类"""
    
    def __init__(self):
        """初始化本地大模型配置"""
        # 模型列表，按优先级排序
        self.models = [
            {
                "name": "deepseek-r1:1.5b",
                "priority": 1
            },
            {
                "name": "deepseek-r1:7b",
                "priority": 2
            }
        ]
        
        # 模型调用参数
        self.model_params = {
            "temperature": 0.7,
            "base_url": "http://localhost:11434",
            "timeout": 30,
            "max_tokens": 512
        }
        
        # 重试策略
        self.retry_strategy = {
            "max_retries": 1,
            "retry_interval": 1  # 秒
        }
        
        # 当前活跃模型
        self.active_model = None
        
        # 初始化模型连接
        self._initialize_models()
    
    def _initialize_models(self):
        """初始化模型连接"""
        logger.info("初始化本地大模型配置")
        # 检测可用模型
        available_models = self._get_available_models()
        logger.info(f"可用模型: {available_models}")
        
        # 选择优先级最高的可用模型
        for model in sorted(self.models, key=lambda x: x["priority"]):
            if model["name"] in available_models:
                self.active_model = model["name"]
                logger.info(f"选择模型: {self.active_model}")
                break
        
        if not self.active_model:
            logger.warning("没有可用的模型")
    
    def _get_available_models(self) -> List[str]:
        """获取可用的Ollama模型"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
        except Exception as e:
            logger.error(f"获取可用模型失败: {str(e)}")
        return []
    
    def _call_model(self, model_name: str, question: str) -> Optional[str]:
        """直接调用模型API"""
        try:
            # 构建请求数据
            data = {
                "model": model_name,
                "prompt": question,
                "stream": False,
                "options": {
                    "temperature": self.model_params["temperature"],
                    "max_tokens": self.model_params["max_tokens"]
                }
            }
            
            # 发送请求
            response = requests.post(
                f"{self.model_params['base_url']}/api/generate",
                json=data,
                timeout=self.model_params["timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', None)
            else:
                logger.error(f"模型 {model_name} 调用失败: {response.status_code}")
                logger.error(f"错误信息: {response.text}")
                return None
        except Exception as e:
            logger.error(f"模型 {model_name} 调用异常: {str(e)}")
            return None
    
    def _switch_model(self) -> Optional[str]:
        """切换到下一个可用模型"""
        available_models = self._get_available_models()
        
        # 找到当前模型的优先级
        current_priority = None
        for model in self.models:
            if model["name"] == self.active_model:
                current_priority = model["priority"]
                break
        
        # 选择优先级更高的可用模型
        for model in sorted(self.models, key=lambda x: x["priority"]):
            if model["name"] in available_models and (
                current_priority is None or model["priority"] > current_priority
            ):
                logger.info(f"切换模型: {self.active_model} -> {model['name']}")
                self.active_model = model["name"]
                return self.active_model
        
        logger.error("没有可用的模型可以切换")
        return None
    
    def invoke(self, question: str) -> Optional[str]:
        """调用模型并处理故障转移"""
        if not self.active_model:
            logger.error("没有可用的模型")
            return None
        
        retries = 0
        max_retries = self.retry_strategy["max_retries"]
        retry_interval = self.retry_strategy["retry_interval"]
        
        while retries <= max_retries:
            try:
                logger.info(f"使用模型 {self.active_model} 处理请求")
                response = self._call_model(self.active_model, question)
                if response:
                    logger.info(f"模型 {self.active_model} 响应成功")
                    return response
                else:
                    logger.error(f"模型 {self.active_model} 没有返回响应")
                    retries += 1
            except Exception as e:
                logger.error(f"模型 {self.active_model} 调用失败: {str(e)}")
                retries += 1
            
            if retries <= max_retries:
                logger.info(f"第 {retries} 次重试...")
                time.sleep(retry_interval)
            else:
                # 尝试切换模型
                if self._switch_model():
                    logger.info("切换模型后重试")
                    retries = 0
                else:
                    logger.error("所有模型都不可用")
                    return None
    
    def get_active_model(self) -> Optional[str]:
        """获取当前活跃模型"""
        return self.active_model
    
    def set_model_params(self, params: Dict[str, Any]):
        """设置模型参数"""
        self.model_params.update(params)
        logger.info(f"更新模型参数: {params}")
    
    def set_retry_strategy(self, strategy: Dict[str, int]):
        """设置重试策略"""
        self.retry_strategy.update(strategy)
        logger.info(f"更新重试策略: {strategy}")

# 全局实例
local_llm_config = LocalLLMConfig()
