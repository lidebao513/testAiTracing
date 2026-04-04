import requests

try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    print('Ollama service is running')
    models = response.json().get('models', [])
    print('Models available:', [model['name'] for model in models])
except Exception as e:
    print('Ollama service is not running:', str(e))
