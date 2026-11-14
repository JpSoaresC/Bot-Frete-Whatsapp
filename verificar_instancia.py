import requests

EVOLUTION_API_URL = "http://localhost:8080"
API_KEY = "minha_chave_secreta"


def verificar():
    # Lista todas as instâncias
    url = f"{EVOLUTION_API_URL}/instance/list"
    headers = {"apikey": API_KEY}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Instâncias encontradas: {response.json()}")
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    verificar()