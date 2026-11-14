import os
import traceback
import requests
from bot_logic import BotController
from database import DatabaseManager
from flask import Flask, jsonify, request

app = Flask(__name__)

# Inicializa o banco e o controlador
db = DatabaseManager("database_frete.sqlite")
bot = BotController(db)

# CONFIGURAÇÃO DO WAHA
WAHA_URL = "http://localhost:3000/api/sendText"
WAHA_API_KEY = "23d377a3ef754b429b8702ab1d2da4cd"
WAHA_SESSION = "default"


def enviar_mensagem_whatsapp(chat_id: str, texto: str) -> bool:
    """Envia mensagem via WAHA API."""
    headers = {
        "X-Api-Key": WAHA_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "session": WAHA_SESSION,
        "chatId": chat_id,
        "text": texto,
    }
    try:
        resp = requests.post(WAHA_URL, json=payload, headers=headers, timeout=10)
        print(f"📤 Envio para {chat_id}: {resp.status_code} {resp.text[:200]}")
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    print(f"\n{'=' * 60}")
    print(f"🔍 WEBHOOK RECEBIDO!")
    print(f"📦 Evento: {data.get('event', 'desconhecido')}")
    print(f"{'=' * 60}\n")

    try:
        event = data.get("event", "")

        if event not in ["message", "messages.upsert"]:
            print(f"⚠️ Evento ignorado: {event}")
            return jsonify({"status": "ignorado_evento"}), 200

        payload = data.get("payload", {})

        from_me = payload.get("fromMe", False)
        from_id = payload.get("from", "")
        to_id = payload.get("to", "")
        texto = payload.get("body", "")

        # Extrair nome do contato (se disponível)
        nome_contato = payload.get("_data", {}).get("notifyName", "")
        if not nome_contato:
            nome_contato = payload.get("_data", {}).get("notifyName", "Desconhecido")

        # FILTRO 1: Ignorar grupos
        if "@g.us" in from_id:
            print(f"⚠️ Ignorado: mensagem de grupo ({from_id})")
            return jsonify({"status": "ignorado_grupo"}), 200

        # FILTRO 2: Só processar mensagens para o bot
        NUMERO_BOT = "5521973049068"
        if to_id != f"{NUMERO_BOT}@c.us":
            print(f"⚠️ Ignorado: mensagem não é para o bot (to: {to_id})")
            return jsonify({"status": "ignorado_nao_bot"}), 200

        if not from_id or not texto:
            print(f"⚠️ Sem from_id ou texto")
            return jsonify({"status": "no_content"}), 200

        if from_me:
            return jsonify({"status": "ignorado_self"}), 200

        chat_id = from_id
        numero = from_id.split("@")[0]

        print(f"\n📩 {numero} ({nome_contato}): '{texto}'")

        resposta = bot.processar_mensagem(numero, texto, nome_contato)
        print(f"🤖 Resposta: '{resposta}'")

        if resposta:
            enviar_mensagem_whatsapp(chat_id, str(resposta))

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"⚠️ Erro: {e}")
        traceback.print_exc()
        return jsonify({"status": "erro"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)