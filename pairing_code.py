import requests

API_KEY = "minha_chave_secreta"
INSTANCE = "bot_frete"
SEU_NUMERO = "5521973049068"


def gerar_pairing_code():
    url = f"http://localhost:8080/instance/connect/{INSTANCE}"
    headers = {"apikey": API_KEY, "content-type": "application/json"}

    payload = {
        "phoneNumber": SEU_NUMERO
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    data = response.json()

    print(f"Resposta completa: {data}")

    if 'pairingCode' in data:
        print(f"\n✅ CÓDIGO DE PAREAMENTO: {data['pairingCode']}")
        print("\n📱 No seu WhatsApp (celular do bot):")
        print("1. Vá em Configurações (⚙️)")
        print("2. Aparelhos conectados")
        print("3. 'Conectar aparelho'")
        print("4. Toque em 'Conectar com número de telefone' (embaixo do QR Code)")
        print(f"5. Digite: {data['pairingCode']}")
    else:
        print("\n⚠️ Não retornou pairingCode. Veja a resposta acima.")


if __name__ == "__main__":
    gerar_pairing_code()