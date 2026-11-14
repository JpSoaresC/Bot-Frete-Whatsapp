# 🚚 Bot WhatsApp para Fretes e Mudanças

Chatbot automatizado para cotação e agendamento de fretes via WhatsApp.

## 🛠️ Tecnologias
- Python 3.14 + Flask
- WAHA (WhatsApp HTTP API)
- Google Calendar API
- SQLite
- ngrok (túnel HTTPS)
- Geopy (geolocalização)

## 📦 Instalação
1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure o WAHA via Docker
4. Adicione suas credenciais do Google Calendar em `credentials.json`
5. Execute: `python app.py`

## 🤖 Funcionalidades
- Cotação automática de fretes por distância
- Agendamento com validação de 24h de antecedência
- Integração com Google Calendar
- Notificação automática ao responsável
- Consulta de agendamentos
- Filtro de mensagens (responde apenas em PV)

## 🔒 Segurança
- Arquivos sensíveis (.env, credentials.json, token.json) estão no .gitignore
- Webhook filtra mensagens de grupos e números não autorizados