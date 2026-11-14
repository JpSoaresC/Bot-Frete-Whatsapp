import datetime
import os
import google.auth.exceptions
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarService:
    def __init__(self, credentials_file="credentials.json", token_file="token.json"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self._autenticar()

    def _autenticar(self):
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except google.auth.exceptions.RefreshError:
                    print("⚠️ Token expirado ou revogado. Iniciando novo processo de autenticação...")
                    if os.path.exists(self.token_file):
                        os.remove(self.token_file)
                    creds = None

            if not creds:
                if os.path.exists(self.credentials_file):
                    print("🌐 Abrindo navegador para autenticação no Google Calendar...")
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                    with open(self.token_file, "w") as token:
                        token.write(creds.to_json())
                    print("✅ Autenticação realizada com sucesso! Novo token salvo.")
                else:
                    print(f"⚠️ Arquivo {self.credentials_file} não encontrado. Operando em modo de simulação.")
                    return None
        return build("calendar", "v3", credentials=creds)

    def verificar_turnos_disponiveis(self, data_str: str) -> dict:
        if not self.service:
            print("⚠️ Serviço do Google Calendar não inicializado. Retornando turnos padrão.")
            return {"manha": True, "tarde": True, "noite": True}

        inicio_dia = f"{data_str}T00:00:00-03:00"
        fim_dia = f"{data_str}T23:59:59-03:00"

        try:
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=inicio_dia,
                    timeMax=fim_dia,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            eventos = events_result.get("items", [])
            print(f"📅 Verificando agenda para {data_str}. Eventos encontrados: {len(eventos)}")

            turnos = {"manha": True, "tarde": True, "noite": True}

            for evento in eventos:
                start = evento["start"].get("dateTime", evento["start"].get("date"))
                if "T" in start:
                    hora = int(start.split("T")[1].split(":")[0])
                    if 8 <= hora < 12:
                        turnos["manha"] = False
                        print(f"  🔒 Turno MANHÃ bloqueado pelo evento: {evento.get('summary')}")
                    elif 13 <= hora < 17:
                        turnos["tarde"] = False
                        print(f"  🔒 Turno TARDE bloqueado pelo evento: {evento.get('summary')}")
                    elif 18 <= hora < 22:
                        turnos["noite"] = False
                        print(f"  🔒 Turno NOITE bloqueado pelo evento: {evento.get('summary')}")

            return turnos
        except Exception as e:
            print(f"❌ Erro ao verificar turnos no Google Calendar: {e}")
            return {"manha": True, "tarde": True, "noite": True}

    def criar_agendamento(self, data_str: str, turno: str, resumo_pedido: str, descricao_detalhada: str) -> str:
        if not self.service:
            print("⚠️ Modo simulação: Evento não criado no Google Calendar.")
            return "SIMULATED_EVENT_ID"

        horarios = {
            "manha": ("08:00:00", "12:00:00"),
            "tarde": ("13:00:00", "17:00:00"),
            "noite": ("18:00:00", "22:00:00"),
        }

        hora_inicio, hora_fim = horarios.get(turno, ("08:00:00", "12:00:00"))

        event = {
            "summary": resumo_pedido,
            "description": descricao_detalhada,
            "start": {
                "dateTime": f"{data_str}T{hora_inicio}-03:00",
                "timeZone": "America/Sao_Paulo",
            },
            "end": {
                "dateTime": f"{data_str}T{hora_fim}-03:00",
                "timeZone": "America/Sao_Paulo",
            },
        }

        try:
            created_event = self.service.events().insert(calendarId="primary", body=event).execute()
            print(f"✅ Evento criado no Google Calendar com ID: {created_event.get('id')}")
            return created_event.get("id")
        except Exception as e:
            print(f"❌ Erro ao criar evento no Google Calendar: {e}")
            return "ERROR_CREATING_EVENT"