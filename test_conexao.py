import requests

API_KEY = "minha_chave_secreta"
INSTANCE = "bot_frete"

url = f"http://localhost:8080/instance/connect/{INSTANCE}"
headers = {"apikey": API_KEY}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
except Exception as e:
    print(f"Erro: {e}")