#!/usr/bin/env python3
"""
本地大模型调用配置模块

功能：
1. 基于Ollama接口的本地大模型调用系统
2. 实现三级模型自动故障转移机制（deepseek-r1:1.5b -> deepseek-r1:7b -> qwen3:4b）
3. 配置完整的模型调用参数
4. 多层次错误检测和重试策略
5. 详细日志记录
6. 统一设置5分钟超时时间
"""

import logging
import time
from typing import Optional, Dict, Any, List, Tuple
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelConnectionError(Exception):
    """模型连接错误"""
    pass


class LocalLLMConfig:
    """本地大模型配置类"""
    
    # 统一超时时间：5分钟 = 300秒
    CONNECTION_TIMEOUT = 300
    
    def __init__(self):
        """初始化本地大模型配置"""
        # 模型列表，按优先级排序
        self.models = [
            {
                "name": "deepseek-r1:1.5b",
                "priority": 1,
                "description": "首选模型 - 轻量级"
            },
            {
                "name": "deepseek-r1:7b",
                "priority": 2,
                "description": "备用模型 - 标准版"
            },
            {
                "name": "qwen3:4b",
                "priority": 3,
                "description": "备选模型 - 最终备用"
            }
        ]
        
        # 模型调用参数
        self.model_params = {
            "temperature": 0.7,
            "base_url": "http://localhost:11434",
            "timeout": self.CONNECTION_TIMEOUT,  # 统一使用5分钟超时
            "max_tokens": 512
        }
        
        # 重试策略
        self.retry_strategy = {
            "max_retries": 1,
            "retry_interval": 1  # 秒
        }
        
        # 当前活跃模型
        self.active_model = None
        
        # 连接状态记录
        self.connection_status = {}
        
        # 初始化模型连接
        self._initialize_models()
    
    def _initialize_models(self):
        """初始化模型连接"""
        logger.info("=" * 60)
        logger.info("初始化本地大模型配置")
        logger.info("=" * 60)
        
        # 尝试依次连接模型
        for model in sorted(self.models, key=lambda x: x["priority"]):
            model_name = model["name"]
            logger.info(f"\n尝试连接模型: {model_name} ({model['description']})")
            
            if self._test_model_connection(model_name):
                self.active_model = model_name
                self.connection_status[model_name] = {
                    "status": "connected",
                    "timestamp": time.time(),
                    "error": None
                }
                logger.info(f"✓ 模型 {model_name} 连接成功，设为活跃模型")
                break
            else:
                self.connection_status[model_name] = {
                    "status": "failed",
                    "timestamp": time.time(),
                    "error": "连接失败"
                }
                logger.warning(f"✗ 模型 {model_name} 连接失败")
        
        if not self.active_model:
            logger.error("\n" + "=" * 60)
            logger.error("错误：所有模型均连接失败")
            logger.error("=" * 60)
            for model_name, status in self.connection_status.items():
                logger.error(f"  - {model_name}: {status['error']}")
        else:
            logger.info("\n" + "=" * 60)
            logger.info(f"当前活跃模型: {self.active_model}")
            logger.info("=" * 60)
    
    def _test_model_connection(self, model_name: str) -> bool:
        """测试模型连接"""
        try:
            # 测试模型是否可用
            response = requests.get(
                f"{self.model_params['base_url']}/api/tags",
                timeout=self.CONNECTION_TIMEOUT
            )
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [m['name'] for m in models]
                
                if model_name in available_models:
                    # 测试模型是否可以生成
                    test_response = requests.post(
                        f"{self.model_params['base_url']}/api/generate",
                        json={
                            "model": model_name,
                            "prompt": "test",
                            "stream": False,
                            "options": {"max_tokens": 10}
                        },
                        timeout=self.CONNECTION_TIMEOUT
                    )
                    return test_response.status_code == 200
                else:
                    logger.warning(f"模型 {model_name} 未在Ollama中安装")
                    return False
            else:
                logger.error(f"Ollama服务返回错误: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"模型 {model_name} 连接超时（超过{self.CONNECTION_TIMEOUT}秒）")
            self.connection_status[model_name] = {
                "status": "failed",
                "timestamp": time.time(),
                "error": f"连接超时（超过{self.CONNECTION_TIMEOUT}秒）"
            }
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"模型 {model_name} 连接被拒绝: {str(e)}")
            self.connection_status[model_name] = {
                "status": "failed",
                "timestamp": time.time(),
                "error": f"连接被拒绝: {str(e)}"
            }
            return False
        except Exception as e:
            logger.error(f"模型 {model_name} 连接异常: {str(e)}")
            self.connection_status[model_name] = {
                "status": "failed",
                "timestamp": time.time(),
                "error": f"连接异常: {str(e)}"
            }
            return False
    
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
            
            logger.info(f"调用模型 {model_name}，超时时间: {self.CONNECTION_TIMEOUT}秒")
            
            # 发送请求，使用统一超时时间
            response = requests.post(
                f"{self.model_params['base_url']}/api/generate",
                json=data,
                timeout=self.CONNECTION_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                self.connection_status[model_name] = {
                    "status": "connected",
                    "timestamp": time.time(),
                    "error": None
                }
                return result.get('response', None)
            else:
                error_msg = f"模型 {model_name} 调用失败: HTTP {response.status_code}"
                logger.error(error_msg)
                self.connection_status[model_name] = {
                    "status": "failed",
                    "timestamp": time.time(),
                    "error": error_msg
                }
                return None
                
        except requests.exceptions.Timeout:
            error_msg = f"模型 {model_name} 调用超时（超过{self.CONNECTION_TIMEOUT}秒）"
            logger.error(error_msg)
            self.connection_status[model_name] = {
                "status": "failed",
                "timestamp": time.time(),
                "error": error_msg
            }
            return None
        except requests.exceptions.ConnectionError as e:
            error_msg = f"模型 {model_name} 连接被拒绝: {str(e)}"
            logger.error(error_msg)
            self.connection_status[model_name] = {
                "status": "failed",
                "timestamp": time.time(),
                "error": error_msg
            }
            return None
        except Exception as e:
            error_msg = f"模型 {model_name} 调用异常: {str(e)}"
            logger.error(error_msg)
            self.connection_status[model_name] = {
                "status": "failed",
                "timestamp": time.time(),
                "error": error_msg
            }
            return None
    
    def _switch_model(self) -> Optional[str]:
        """切换到下一个可用模型"""
        logger.info("尝试切换到下一个可用模型")
        
        # 按优先级排序模型
        sorted_models = sorted(self.models, key=lambda x: x["priority"])
        
        # 找到当前模型的索引
        current_index = -1
        for i, model in enumerate(sorted_models):
            if model["name"] == self.active_model:
                current_index = i
                break
        
        # 从当前模型之后开始尝试
        start_index = current_index + 1 if current_index >= 0 else 0
        
        for i in range(start_index, len(sorted_models)):
            model = sorted_models[i]
            model_name = model["name"]
            logger.info(f"尝试连接备用模型: {model_name} ({model['description']})")
            
            if self._test_model_connection(model_name):
                logger.info(f"✓ 模型 {model_name} 连接成功，切换为活跃模型")
                self.active_model = model_name
                return model_name
        
        # 尝试所有模型都失败
        logger.error("所有模型均连接失败，无法切换")
        return None
    
    def invoke(self, question: str) -> Optional[str]:
        """调用模型并处理故障转移"""
        if not self.active_model:
            logger.error("没有可用的模型")
            # 尝试初始化模型
            self._initialize_models()
            if not self.active_model:
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
    
    def get_connection_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有模型的连接状态"""
        return self.connection_status
    
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
