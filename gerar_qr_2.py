import requests
import base64
from PIL import Image
import io
import webbrowser
import os

API_KEY = "minha_chave_secreta"
INSTANCE = "bot_frete"

url = f"http://localhost:8080/instance/connect/{INSTANCE}"
headers = {"apikey": API_KEY}

print(f"🔍 Gerando QR Code para '{INSTANCE}'...")
try:
    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()

    if 'base64' in data:
        qrcode_base64 = data['base64']
        if ',' in qrcode_base64:
            qrcode_base64 = qrcode_base64.split(',')[1]

        img_data = base64.b64decode(qrcode_base64)
        img = Image.open(io.BytesIO(img_data))
        img.save("qrcode_v2.png")

        print("✅ QR Code salvo como 'qrcode_v2.png'")
        webbrowser.open(os.path.abspath("qrcode_v2.png"))
        print("📱 Escaneie agora!")
    else:
        print(f"Resposta: {data}")
except Exception as e:
    print(f"Erro: {e}")