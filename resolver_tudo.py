import requests
import base64
from PIL import Image
import io
import webbrowser
import os

API_KEY = "minha_chave_secreta"
INSTANCE = "bot_frete"
HEADERS = {"apikey": API_KEY, "content-type": "application/json"}


def passo1_criar_instancia():
    print("=" * 50)
    print("PASSO 1: Criando instância 'bot_frete'...")
    print("=" * 50)

    url = "http://localhost:8080/instance/create"
    payload = {"instanceName": INSTANCE, "qrcode": True}

    response = requests.post(url, json=payload, headers=HEADERS, timeout=10)

    if response.status_code in (200, 201):
        print("✅ Instância criada com sucesso!")
        return True
    elif response.status_code == 403:
        print("⚠️ Instância já existe. Vamos usar a existente.")
        return True
    else:
        print(f"❌ Erro: {response.text}")
        return False


def passo2_gerar_qrcode():
    print("\n" + "=" * 50)
    print("PASSO 2: Gerando QR Code...")
    print("=" * 50)

    url = f"http://localhost:8080/instance/connect/{INSTANCE}"

    response = requests.get(url, headers=HEADERS, timeout=10)
    data = response.json()

    if 'base64' in data:
        qrcode_base64 = data['base64']
        if ',' in qrcode_base64:
            qrcode_base64 = qrcode_base64.split(',')[1]

        img_data = base64.b64decode(qrcode_base64)
        img = Image.open(io.BytesIO(img_data))
        img.save("qrcode.png")

        print("✅ QR Code salvo como 'qrcode.png'")
        print("📱 Abrindo a imagem... ESCANEIE AGORA!")

        # Abre a imagem automaticamente
        webbrowser.open(os.path.abspath("qrcode.png"))
        return True
    else:
        print(f"❌ Erro: {data}")
        return False


if __name__ == "__main__":
    if passo1_criar_instancia():
        if passo2_gerar_qrcode():
            print("\n" + "=" * 50)
            print("🎯 AGORA:")
            print("1. Abra o WhatsApp no seu celular")
            print("2. Configurações → Aparelhos conectados")
            print("3. Conectar aparelho")
            print("4. Escaneie o QR Code que abriu na tela")
            print("=" * 50)
        else:
            print("\n❌ Falhou ao gerar QR Code")
    else:
        print("\n❌ Falhou ao criar instância")