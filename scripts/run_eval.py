#!/usr/bin/env python3
"""
评估脚本
包含code_scorer函数用于评估代码生成结果
"""

def code_scorer(task, generated):
    """
    评估代码生成结果
    
    Args:
        task (dict): 任务信息，包含type和expected字段
        generated (str): 生成的代码或结果
    
    Returns:
        tuple: (是否通过, 分数)
    """
    task_type = task.get('type')
    expected = task.get('expected')
    
    if task_type == 'factual':
        # 事实型任务：从生成内容中提取结果并与预期比较
        # 简单实现：尝试提取数字或直接比较
        generated_str = generated.strip()
        expected_str = str(expected)
        
        # 检查生成内容是否包含预期值
        passed = expected_str in generated_str
        score = 1.0 if passed else 0.0
        return (passed, score)
    
    elif task_type == 'code':
        # 代码型任务：比较代码是否与预期相同
        passed = generated.strip() == expected
        score = 1.0 if passed else 0.0
        return (passed, score)
    
    elif task_type == 'creative':
        # 创意型任务：需要模型评分
        return (False, 0.0)
    
    else:
        # 未知任务类型
        return (False, 0.0)

def call_llm(prompt):
    """
    调用LLM模型进行评分
    
    Args:
        prompt (str): 评分提示
    
    Returns:
        str: 模型评分结果
    """
    # 实际实现会调用真实的LLM模型
    # 这里返回一个模拟结果
    return "分数：7\n理由：不错"

def model_scorer(task, generated):
    """
    使用模型对生成内容进行评分
    
    Args:
        task (dict): 任务信息，包含type字段
        generated (str): 生成的内容
    
    Returns:
        tuple: (是否通过, 理由)
    """
    task_type = task.get('type')
    
    if task_type == 'creative':
        # 构建评分提示
        prompt = f"请对以下内容进行评分（1-10分），并给出理由：\n{generated}"
        
        # 调用LLM模型获取评分
        result = call_llm(prompt)
        
        # 解析评分结果
        # 假设结果格式为："分数：X\n理由：..."
        lines = result.split('\n')
        score_line = next((line for line in lines if '分数' in line), '')
        reason_line = next((line for line in lines if '理由' in line), '')
        
        # 提取分数
        try:
            score_str = score_line.split('：')[1].strip()
            score = int(score_str)
        except (IndexError, ValueError):
            score = 0
            reason = "无法解析评分结果"
        else:
            # 提取理由
            reason = reason_line.split('：')[1].strip() if reason_line else "无理由"
        
        # 判断是否通过（分数>=7）
        passed = score >= 7
        return (passed, reason)
    
    else:
        # 非创意型任务不使用模型评分
        return (False, "非创意型任务不需要模型评分")

if __name__ == "__main__":
    # 测试code_scorer
    task = {"type": "factual", "expected": "2"}
    assert code_scorer(task, "结果是2")[0] == True
    
    task2 = {"type": "code", "expected": "print('Hello')"}
    assert code_scorer(task2, "print('Hello')")[0] == True
    
    task3 = {"type": "creative", "expected": None}
    assert code_scorer(task3, "any")[0] == False  # 应返回需要模型评分
    
    print("PASS: code_scorer")
    
    # 测试model_scorer
    from unittest.mock import patch
    with patch('__main__.call_llm') as mock:
        mock.return_value = "分数：8\n理由：很好"
        passed, reason = model_scorer({"type": "creative"}, "joke")
        assert passed == True, "Should pass with score>=7"
        
        mock.return_value = "分数：5\n理由：一般"
        passed, reason = model_scorer({"type": "creative"}, "joke")
        assert passed == False
    
    print("PASS: model_scorer")
