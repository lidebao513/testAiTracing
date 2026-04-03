
"""
测试配置文件

包含测试共享配置和夹具
"""

import pytest


@pytest.fixture(scope="session")
def setup_test_environment():
    """测试环境设置"""
    # 这里可以添加测试环境的设置代码
    yield
    # 这里可以添加测试环境的清理代码


@pytest.fixture(scope="function")
def sample_fixture():
    """示例夹具"""
    return "sample_value"
