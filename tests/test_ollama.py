import requests
import json

def check_ollama_service():
    """检查 Ollama 服务是否运行"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Ollama 服务返回状态码: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Ollama 服务未运行，请启动 Ollama 服务"
    except Exception as e:
        return False, f"检查 Ollama 服务时出错: {str(e)}"

def check_model_exists(models, model_name):
    """检查指定模型是否存在"""
    for model in models.get('models', []):
        if model.get('name') == model_name:
            return True
    return False

def test_model(model_name, prompt):
    """测试模型响应"""
    try:
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return True, result.get('response', 'No response')
        else:
            return False, f"模型请求返回状态码: {response.status_code}"
    except Exception as e:
        return False, f"测试模型时出错: {str(e)}"

def main():
    print("=== 检查 Ollama 服务 ===")
    service_running, service_message = check_ollama_service()
    
    if not service_running:
        print(f"❌ 错误: {service_message}")
        print("提示: 请先安装并启动 Ollama 服务，可访问 https://ollama.com 下载安装")
        return
    
    print("✅ Ollama 服务运行正常")
    
    models = service_message
    model_name = "deepseek-r1:1.5b"
    
    print(f"\n=== 检查模型 {model_name} ===")
    if check_model_exists(models, model_name):
        print(f"✅ 模型 {model_name} 已存在")
    else:
        print(f"❌ 模型 {model_name} 不存在")
        print(f"提示: 请运行命令 'ollama pull {model_name}' 拉取模型")
        return
    
    print("\n=== 测试模型响应 ===")
    prompt = "Say hello"
    success, response = test_model(model_name, prompt)
    
    if success:
        print("✅ 模型响应成功:")
        print(f"响应: {response}")
    else:
        print(f"❌ 测试模型时出错: {response}")

if __name__ == "__main__":
    main()
