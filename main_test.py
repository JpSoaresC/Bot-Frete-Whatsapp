from bot_logic import BotController
from database import DatabaseManager

db = DatabaseManager("database_frete.sqlite")
bot = BotController(db)

telefone_cliente = "5521999998888"

print("--- INICIANDO SIMULAÇÃO DO BOT ---")

# Simula primeira mensagem do cliente
resp1 = bot.processar_mensagem(telefone_cliente, "Oi")
print(f"Bot:\n{resp1}\n" + "-" * 30)

# Simula escolha da opção 1
resp2 = bot.processar_mensagem(telefone_cliente, "1")
print(f"Bot:\n{resp2}\n" + "-" * 30)

# Simula escolha de Frete Simples (opção 1)
resp3 = bot.processar_mensagem(telefone_cliente, "1")
print(f"Bot:\n{resp3}\n" + "-" * 30)

# Simula digitação da Origem
resp4 = bot.processar_mensagem(
    telefone_cliente, "Rua Felipe Cardoso, 100 - Santa Cruz"
)
print(f"Bot:\n{resp4}\n" + "-" * 30)

# Simula digitação do Destino
resp5 = bot.processar_mensagem(
    telefone_cliente, "Av. Brasil, 5000 - Campo Grande"
)
print(f"Bot:\n{resp5}\n" + "-" * 30)

# Simula digitação da Carga
resp6 = bot.processar_mensagem(
    telefone_cliente, "1 Máquina de lavar e 1 fogão"
)
print(f"Bot:\n{resp6}\n" + "-" * 30)
