from calendar_service import GoogleCalendarService
from database import DatabaseManager
from handlers import FlowHandler
from messages import BotMessages
from pricing import PricingCalculator


class BotController:
    # NÚMERO DO RESPONSÁVEL (troque pelo seu número real com DDI)
    NUMERO_RESPONSAVEL = "5521973049068"

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.pricing = PricingCalculator()
        self.calendar = GoogleCalendarService()
        self.handler = FlowHandler(self.db, self.pricing, self.calendar)

    def processar_mensagem(self, telefone: str, mensagem: str, nome_contato: str = "Desconhecido") -> str:
        mensagem = mensagem.strip()
        sessao = self.db.abrir_ou_criar_sessao(telefone)
        etapa = sessao["etapa_atual"]
        dados = sessao["dados_temporarios"]

        # Salvar nome do contato nos dados temporários
        if nome_contato and nome_contato != "Desconhecido":
            dados["nome_contato"] = nome_contato

        # Comando de reset universal
        if mensagem.lower() in ["inicio", "início", "menu", "0"]:
            self.db.resetar_sessao(telefone)
            return BotMessages.menu_principal()

        # 1. MENU PRINCIPAL
        if etapa == "MENU_PRINCIPAL":
            if mensagem == "1":
                self.db.atualizar_sessao(telefone, "AGUARDANDO_TIPO_SERVICO", dados)
                return BotMessages.escolher_tipo_servico()
            elif mensagem == "2":
                self.db.atualizar_sessao(telefone, "CONSULTANDO_AGENDAMENTO", dados)
                return "🔍 Digite o número do seu telefone (com DDI) para localizar seu agendamento:"
            elif mensagem == "3":
                return "📸 *Fotos do Caminhão*\n\n[Envio de Fotos]\n\nDigite *MENU* para voltar."
            return f"Opção inválida!\n\n{BotMessages.menu_principal()}"

        # 2. CONSULTAR AGENDAMENTO (NOVO - estava faltando!)
        elif etapa == "CONSULTANDO_AGENDAMENTO":
            pedido = self.db.buscar_pedido_por_telefone(mensagem)

            if not pedido:
                # Se o telefone do usuário for um @lid, explicamos o motivo
                if "@lid" in telefone:
                    return (
                        "❌ *Número não identificado.*\n\n"
                        "Como seu número não está salvo na agenda do bot, o WhatsApp oculta seu número real.\n\n"
                        "📞 *Para consultar:* Entre em contato diretamente pelo telefone *(21) 97304-9068* informando seu nome."
                    )
                return "❌ Nenhum agendamento encontrado para esse número.\n\nDigite *MENU* para voltar ao início."

            # Formata o turno para ficar bonito
            mapa_turno = {"manha": "Manhã", "tarde": "Tarde", "noite": "Noite"}
            turno_formatado = mapa_turno.get(pedido['turno_agendado'], pedido['turno_agendado'].capitalize())
            valor_str = f"R$ {pedido['valor_estimado']:.2f}" if pedido['valor_estimado'] else "A definir"

            resposta = (
                f"📋 *Seu Agendamento*\n\n"
                f"🆔 *ID:* {pedido['id_pedido']}\n"
                f"📅 *Data:* {pedido['data_agendada']}\n"
                f"🕐 *Turno:* {turno_formatado}\n"
                f"📍 *Origem:* {pedido['origem_rua']}, {pedido['origem_bairro']}\n"
                f"🏁 *Destino:* {pedido['destino_rua']}, {pedido['destino_bairro']}\n"
                f"📦 *Carga:* {pedido['descricao_carga']}\n"
                f"💰 *Valor:* {valor_str}\n"
                f"📊 *Status:* {pedido['status']}\n\n"
                "Digite *MENU* para voltar ao início."
            )

            self.db.resetar_sessao(telefone)
            return resposta

        # 3. COLETA DE DADOS PASSO A PASSO
        elif etapa == "AGUARDANDO_TIPO_SERVICO":
            if mensagem in ["1", "2"]:
                dados["tipo_servico"] = "frete_simples" if mensagem == "1" else "mudanca_completa"
                self.db.atualizar_sessao(telefone, "AGUARDANDO_ORIGEM_RUA_BAIRRO", dados)
                return BotMessages.pedir_origem()
            return "Opção inválida. Digite 1 para Frete Simples ou 2 para Mudança."

        elif etapa == "AGUARDANDO_ORIGEM_RUA_BAIRRO":
            dados["origem_endereco"] = mensagem
            self.db.atualizar_sessao(telefone, "AGUARDANDO_DESTINO_RUA_BAIRRO", dados)
            return BotMessages.pedir_destino()

        elif etapa == "AGUARDANDO_DESTINO_RUA_BAIRRO":
            dados["destino_endereco"] = mensagem
            self.db.atualizar_sessao(telefone, "AGUARDANDO_DESCRICAO_CARGA", dados)
            return BotMessages.pedir_carga()

        elif etapa == "AGUARDANDO_DESCRICAO_CARGA":
            return self.handler.tratar_coleta_carga(telefone, mensagem, dados)

        # 4. AGENDAMENTO E FINALIZAÇÃO
        elif etapa == "AGUARDANDO_ACEITE_ORCAMENTO":
            if mensagem == "1":
                self.db.atualizar_sessao(telefone, "AGUARDANDO_DATA_AGENDAMENTO", dados)
                return BotMessages.pedir_data()
            self.db.resetar_sessao(telefone)
            return "Solicitação cancelada. Digite MENU para recomeçar."

        elif etapa == "AGUARDANDO_DATA_AGENDAMENTO":
            return self.handler.tratar_selecao_data(telefone, mensagem, dados)

        elif etapa == "AGUARDANDO_TURNO_SELECAO":
            return self.handler.tratar_finalizacao_agendamento(telefone, mensagem, dados)

        # Fallback: se a etapa não for reconhecida, reseta e mostra menu
        self.db.resetar_sessao(telefone)
        return BotMessages.menu_principal()