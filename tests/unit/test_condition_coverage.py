#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 should_retry 函数的条件覆盖率

功能：
1. 使用真值表方法系统设计测试用例
2. 覆盖所有原子条件的true/false组合情况
3. 验证每个原子条件对最终结果的独立影响

真值表设计：

原子条件：
A: error_code in [500, 503]
B: retry_count < 3
C: not timeout

组合情况：
| 测试用例ID | error_code | retry_count | timeout | A | B | C | 预期结果 |
|-----------|------------|-------------|---------|---|---|---|----------|
| TC1       | 500        | 0           | False   | T | T | T | True     |
| TC2       | 500        | 0           | True    | T | T | F | False    |
| TC3       | 500        | 3           | False   | T | F | T | False    |
| TC4       | 500        | 3           | True    | T | F | F | False    |
| TC5       | 404        | 0           | False   | F | T | T | False    |
| TC6       | 404        | 0           | True    | F | T | F | False    |
| TC7       | 404        | 3           | False   | F | F | T | False    |
| TC8       | 404        | 3           | True    | F | F | F | False    |

边界情况：
| 测试用例ID | error_code | retry_count | timeout | 预期结果 |
|-----------|------------|-------------|---------|----------|
| TC9       | 503        | 2           | False   | True     |
| TC10      | 503        | 3           | False   | False    |
| TC11      | 200        | 0           | False   | False    |
| TC12      | 500        | 1           | False   | True     |
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.retry_decider import should_retry


class TestShouldRetry(unittest.TestCase):
    """测试 should_retry 函数的条件覆盖"""
    
    def test_tc1_all_true(self):
        """测试用例1：所有条件都为True"""
        # 输入参数: error_code=500, retry_count=0, timeout=False
        # 原子条件: A=T, B=T, C=T
        # 预期结果: True
        result = should_retry(500, 0, False)
        self.assertTrue(result)
    
    def test_tc2_c_false(self):
        """测试用例2：C条件为False"""
        # 输入参数: error_code=500, retry_count=0, timeout=True
        # 原子条件: A=T, B=T, C=F
        # 预期结果: False
        result = should_retry(500, 0, True)
        self.assertFalse(result)
    
    def test_tc3_b_false(self):
        """测试用例3：B条件为False"""
        # 输入参数: error_code=500, retry_count=3, timeout=False
        # 原子条件: A=T, B=F, C=T
        # 预期结果: False
        result = should_retry(500, 3, False)
        self.assertFalse(result)
    
    def test_tc4_b_c_false(self):
        """测试用例4：B和C条件为False"""
        # 输入参数: error_code=500, retry_count=3, timeout=True
        # 原子条件: A=T, B=F, C=F
        # 预期结果: False
        result = should_retry(500, 3, True)
        self.assertFalse(result)
    
    def test_tc5_a_false(self):
        """测试用例5：A条件为False"""
        # 输入参数: error_code=404, retry_count=0, timeout=False
        # 原子条件: A=F, B=T, C=T
        # 预期结果: False
        result = should_retry(404, 0, False)
        self.assertFalse(result)
    
    def test_tc6_a_c_false(self):
        """测试用例6：A和C条件为False"""
        # 输入参数: error_code=404, retry_count=0, timeout=True
        # 原子条件: A=F, B=T, C=F
        # 预期结果: False
        result = should_retry(404, 0, True)
        self.assertFalse(result)
    
    def test_tc7_a_b_false(self):
        """测试用例7：A和B条件为False"""
        # 输入参数: error_code=404, retry_count=3, timeout=False
        # 原子条件: A=F, B=F, C=T
        # 预期结果: False
        result = should_retry(404, 3, False)
        self.assertFalse(result)
    
    def test_tc8_all_false(self):
        """测试用例8：所有条件都为False"""
        # 输入参数: error_code=404, retry_count=3, timeout=True
        # 原子条件: A=F, B=F, C=F
        # 预期结果: False
        result = should_retry(404, 3, True)
        self.assertFalse(result)
    
    def test_tc9_boundary_retry_count_2(self):
        """测试用例9：边界情况 - retry_count=2"""
        # 输入参数: error_code=503, retry_count=2, timeout=False
        # 预期结果: True
        result = should_retry(503, 2, False)
        self.assertTrue(result)
    
    def test_tc10_boundary_retry_count_3(self):
        """测试用例10：边界情况 - retry_count=3"""
        # 输入参数: error_code=503, retry_count=3, timeout=False
        # 预期结果: False
        result = should_retry(503, 3, False)
        self.assertFalse(result)
    
    def test_tc11_non_retry_error(self):
        """测试用例11：非重试错误码"""
        # 输入参数: error_code=200, retry_count=0, timeout=False
        # 预期结果: False
        result = should_retry(200, 0, False)
        self.assertFalse(result)
    
    def test_tc12_normal_retry(self):
        """测试用例12：正常重试情况"""
        # 输入参数: error_code=500, retry_count=1, timeout=False
        # 预期结果: True
        result = should_retry(500, 1, False)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()