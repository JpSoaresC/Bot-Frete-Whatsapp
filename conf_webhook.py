import requests
import json

# Configurações
EVOLUTION_API_URL = "http://localhost:8080"
INSTANCE_NAME = "bot_frete"
API_KEY = "minha_chave_secreta"
WEBHOOK_URL = "https://sheep-imprint-womb.ngrok-free.dev/webhook"


def configurar_webhook():
    url = f"{EVOLUTION_API_URL}/webhook/set/{INSTANCE_NAME}"

    headers = {
        "apikey": API_KEY,
        "content-type": "application/json"
    }

    payload = {
        "url": WEBHOOK_URL,
        "events": ["MESSAGES_UPSERT"],
        "enabled": True
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")

        if response.status_code in (200, 201):
            print("✅ Webhook configurado com sucesso!")
        else:
            print("️ Verifique se a instância 'bot_frete' existe e está conectada")

    except Exception as e:
        print(f" Erro: {e}")


if __name__ == "__main__":
    configurar_webhook()