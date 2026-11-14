import requests

API_KEY = "minha_chave_secreta"
INSTANCE = "bot_frete"
SEU_NUMERO = "5521973049068"


print("🔍 Passo 1: Verificando/criando instância...")
url_create = "http://localhost:8080/instance/create"
headers = {"apikey": API_KEY, "content-type": "application/json"}
payload_create = {
    "instanceName": INSTANCE,
    "qrcode": False,
    "integration": "WHATSAPP-BAILEYS"
}

try:
    r = requests.post(url_create, json=payload_create, headers=headers, timeout=10)
    print(f"Status criação: {r.status_code}")
except Exception as e:
    print(f"Erro ao criar: {e}")

#Gerar Pairing Code
print("\n🔍 Passo 2: Gerando código de pareamento...")
url_connect = f"http://localhost:8080/instance/connect/{INSTANCE}"
payload_connect = {
    "phoneNumber": SEU_NUMERO
}

try:
    r = requests.post(url_connect, json=payload_connect, headers=headers, timeout=10)
    data = r.json()

    print(f"\nResposta completa: {data}")

    if 'pairingCode' in data:
        print(f"\n{'=' * 50}")
        print(f"✅ CÓDIGO DE PAREAMENTO: {data['pairingCode']}")
        print(f"{'=' * 50}")
        print("\n📱 No seu WhatsApp (celular do bot):")
        print("1. Vá em Configurações (⚙️)")
        print("2. Aparelhos conectados")
        print("3. 'Conectar aparelho'")
        print("4. Toque em 'Conectar com número de telefone' (embaixo do QR Code)")
        print(f"5. Digite o código: {data['pairingCode']}")
        print(f"\n⏰ Atenção: O código expira em ~2 minutos!")
    else:
        print("\n⚠️ Não retornou pairingCode. Veja a resposta acima.")
except Exception as e:
    print(f"Erro: {e}")