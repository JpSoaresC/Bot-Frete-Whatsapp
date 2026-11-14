from calendar_service import GoogleCalendarService
from database import DatabaseManager
from messages import BotMessages
from pricing import PricingCalculator
from datetime import datetime, timedelta


class FlowHandler:
    NUMERO_RESPONSAVEL = "5521973049068"  # SEU NÚMERO AQUI

    def __init__(self, db: DatabaseManager, pricing: PricingCalculator, calendar: GoogleCalendarService):
        self.db = db
        self.pricing = pricing
        self.calendar = calendar

    def tratar_coleta_carga(self, telefone: str, mensagem: str, dados_temp: dict) -> str:
        dados_temp["descricao_carga"] = mensagem

        orcamento = self.pricing.avaliar_orcamento(
            tipo_servico=dados_temp.get("tipo_servico"),
            endereco_origem=dados_temp.get("origem_endereco"),
            endereco_destino=dados_temp.get("destino_endereco"),
        )

        dados_temp["distancia_km"] = orcamento.get("distancia_km")
        dados_temp["valor_estimado"] = orcamento.get("valor_estimado")
        dados_temp["requer_negociacao"] = orcamento.get("requer_negociacao")

        # Escolha de data, agora sem encerrar o fluxo
        self.db.atualizar_sessao(telefone, "AGUARDANDO_ACEITE_ORCAMENTO", dados_temp)

        if orcamento["requer_negociacao"]:
            return (
                f"📊 *Pré-Orçamento*\n\n"
                f"• *Distância:* {dados_temp.get('distancia_km')} km\n"
                f"• *Valor:* A definir (sujeito a avaliação)\n\n"
                "⚠️ *Nota:* Por ser uma mudança ou frete local, o valor final será confirmado pelo responsável.\n\n"
                "Deseja prosseguir para escolher a data do agendamento?\n"
                "1️⃣ - Sim, escolher data\n"
                "2️⃣ - Cancelar"
            )

        return BotMessages.resumo_orcamento_automatico(dados_temp)

    def tratar_selecao_data(self, telefone: str, mensagem: str, dados_temp: dict) -> str:
        data_informada = mensagem.strip()

        # REGRA DAS 24 HORAS
        try:
            data_pedido = datetime.strptime(data_informada, "%Y-%m-%d").date()
            hoje = datetime.now().date()
            amanha = hoje + timedelta(days=1)

            if data_pedido < amanha:
                return (
                    f"❌ *Data inválida.*\n\n"
                    f"O agendamento deve ser feito com pelo menos *24 horas de antecedência*.\n"
                    f"A data mínima permitida é: *{amanha.strftime('%Y-%m-%d')}*\n\n"
                    f"Por favor, digite outra data (AAAA-MM-DD):"
                )
        except ValueError:
            return "❌ Formato de data inválido. Use AAAA-MM-DD (ex: 2026-11-15):"

        # VERIFICAR DISPONIBILIDADE NO GOOGLE CALENDAR
        turnos = self.calendar.verificar_turnos_disponiveis(data_informada)
        turnos_livres = [t for t, livre in turnos.items() if livre]

        if not turnos_livres:
            return (
                f"❌ *Sem disponibilidade* para {data_informada}.\n\n"
                f"Todos os turnos (Manhã, Tarde, Noite) já estão agendados.\n"
                f"Por favor, escolha outra data (AAAA-MM-DD):"
            )

        dados_temp["data_agendada"] = data_informada
        dados_temp["turnos_disponiveis"] = turnos_livres
        self.db.atualizar_sessao(telefone, "AGUARDANDO_TURNO_SELECAO", dados_temp)
        return BotMessages.listar_turnos(turnos_livres)

    def tratar_finalizacao_agendamento(self, telefone: str, mensagem: str, dados_temp: dict) -> str:
        mapa_turnos = {"1": "manha", "2": "tarde", "3": "noite"}
        turno_escolhido = mapa_turnos.get(mensagem)

        if not turno_escolhido or turno_escolhido not in dados_temp.get("turnos_disponiveis", []):
            return "Opção de turno inválida. Por favor, escolha uma das opções válidas."

        dados_temp["turno_agendado"] = turno_escolhido

        # GARANTIA DE VALOR NUMÉRICO
        valor_bruto = dados_temp.get('valor_estimado')
        valor_seguro = float(valor_bruto) if valor_bruto is not None else 0.0

        resumo_cal = f"Frete: {dados_temp.get('tipo_servico', '').replace('_', ' ').title()} (Cliente: {dados_temp.get('nome_contato', telefone)})"
        desc_cal = (
            f"Origem: {dados_temp.get('origem_endereco')}\n"
            f"Destino: {dados_temp.get('destino_endereco')}\n"
            f"Carga: {dados_temp.get('descricao_carga')}\n"
            f"Valor: R$ {valor_seguro:.2f}"
        )

        self.calendar.criar_agendamento(
            data_str=dados_temp.get("data_agendada"),
            turno=turno_escolhido,
            resumo_pedido=resumo_cal,
            descricao_detalhada=desc_cal,
        )

        self.notificar_responsavel(telefone, dados_temp, motivo="Agendamento Finalizado")
        self.db.resetar_sessao(telefone)
        return BotMessages.confirmacao_sucesso(dados_temp, turno_escolhido)

    def notificar_responsavel(self, telefone_cliente: str, dados_temp: dict, motivo: str = "Agendamento finalizado"):
        try:
            from app import enviar_mensagem_whatsapp

            tipo_servico = dados_temp.get('tipo_servico', '').replace('_', ' ').title()
            nome_contato = dados_temp.get('nome_contato', 'Desconhecido')

            # BLINDAGEM DO VALOR
            valor_bruto = dados_temp.get('valor_estimado')
            valor_str = f"R$ {float(valor_bruto):.2f}" if valor_bruto is not None else "A definir (negociação manual)"

            mapa_turno = {"manha": "Manhã", "tarde": "Tarde", "noite": "Noite"}
            turno_formatado = mapa_turno.get(dados_temp.get('turno_agendado', ''),
                                             dados_temp.get('turno_agendado', 'A definir').capitalize())

            mensagem = (
                f"🔔 *{motivo}*\n\n"
                f"👤 *Cliente:* {nome_contato}\n"
                f"🆔 *ID WhatsApp:* {telefone_cliente}\n"
                f"🚚 *Serviço:* {tipo_servico}\n"
                f"📅 *Data:* {dados_temp.get('data_agendada', 'A definir')}\n"
                f"🕐 *Turno:* {turno_formatado}\n"
                f"📍 *Origem:* {dados_temp.get('origem_endereco')}\n"
                f"🏁 *Destino:* {dados_temp.get('destino_endereco')}\n"
                f"📦 *Carga:* {dados_temp.get('descricao_carga')}\n"
                f"📏 *Distância:* {dados_temp.get('distancia_km', 0):.1f}km\n"
                f"💰 *Valor estimado:* {valor_str}\n\n"
                f"⚠️ *Ação:* Entre em contato com o cliente via WhatsApp."
            )

            chat_id = f"{self.NUMERO_RESPONSAVEL}@c.us"
            enviar_mensagem_whatsapp(chat_id, mensagem)
            print(f"✅ Notificação enviada ao responsável ({self.NUMERO_RESPONSAVEL})")

        except Exception as e:
            print(f"❌ Erro ao notificar responsável: {e}")