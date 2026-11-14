import requests

API_KEY = "minha_chave_secreta"
INSTANCE = "bot_frete"

url = "http://localhost:8080/instance/create"
headers = {
    "apikey": API_KEY,
    "content-type": "application/json"
}

# Payload completo para v2.3.7
payload = {
    "instanceName": INSTANCE,
    "qrcode": True,
    "integration": "WHATSAPP-BAILEYS"
}

print(f"🔍 Criando instância '{INSTANCE}' com integração WhatsApp-BAILEYS...")
try:
    r = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Resposta: {r.text}")

    if r.status_code in (200, 201):
        print("\n✅ Instância criada com sucesso!")
    else:
        print("\n⚠️ Verifique a resposta acima")
except Exception as e:
    print(f"Erro: {e}")