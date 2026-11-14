import requests

API_KEY = "minha_chave_secreta"


url_v1 = "http://localhost:8080/message/sendText/bot_frete"
headers_v1 = {"apikey": API_KEY, "content-type": "application/json"}
payload = {
    "number": "5521973049068",
    "textMessage": {"text": "Teste de compatibilidade v2"}
}

print("🔍 Testando endpoint v1 (antigo)...")
try:
    r = requests.post(url_v1, json=payload, headers=headers_v1, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Resposta: {r.text}")
except Exception as e:
    print(f"Erro: {e}")