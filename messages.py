class BotMessages:

    @staticmethod
    def menu_principal() -> str:
        return (
            "👋 *Olá! Bem-vindo ao Serviço de Fretes e Mudanças.*\n\n"
            "Como posso te ajudar hoje? Digite o número da opção desejada:\n\n"
            "1️⃣ - Cotar e Agendar Frete/Mudança\n"
            "2️⃣ - Ver / Cancelar meu Agendamento\n"
            "3️⃣ - Ver Fotos e Espaço do Caminhão"
        )

    @staticmethod
    def escolher_tipo_servico() -> str:
        return (
            "🚚 *Cotar e Agendar Frete/Mudança*\n\n"
            "Por favor, escolha o tipo de serviço:\n"
            "1️⃣ - Frete Simples (poucos itens / carga rápida)\n"
            "2️⃣ - Mudança Completa"
        )

    @staticmethod
    def pedir_origem() -> str:
        return "📍 *Endereço de ORIGEM*\n\nPor favor, digite a Rua, Número e Bairro de onde sairá a carga:"

    @staticmethod
    def pedir_destino() -> str:
        return "🏁 *Endereço de DESTINO*\n\nAgora, digite a Rua, Número e Bairro para onde vai a carga:"

    @staticmethod
    def pedir_carga() -> str:
        return "📦 *Descrição da Carga*\n\nO que será transportado? (Ex: 1 geladeira, 1 sofá, 3 caixas)"

    @staticmethod
    def resumo_negociacao_manual(dados: dict) -> str:
        return (
            "✅ *Solicitação Recebida!*\n\n"
            f"• *Serviço:* {dados.get('tipo_servico', '').replace('_', ' ').title()}\n"
            f"• *Origem:* {dados.get('origem_endereco')}\n"
            f"• *Destino:* {dados.get('destino_endereco')}\n"
            f"• *Distância Estimada:* {dados.get('distancia_km')} km\n"
            f"• *Carga:* {dados.get('descricao_carga')}\n\n"
            "ℹ️ *Nota:* Por ser um frete local ou mudança, o orçamento inclui a avaliação da mão de obra.\n\n"
            "O responsável analisará a solicitação e entrará em contato em instantes!"
        )

    @staticmethod
    def resumo_orcamento_automatico(dados: dict) -> str:
        return (
            "📊 *Orçamento Estimado*\n\n"
            f"• *Distância:* {dados.get('distancia_km')} km\n"
            f"• *Valor Estimado:* R$ {dados.get('valor_estimado', 0):.2f}\n\n"
            "Deseja prosseguir para escolher a data do agendamento?\n"
            "1️⃣ - Sim, escolher data\n"
            "2️⃣ - Cancelar"
        )

    @staticmethod
    def pedir_data() -> str:
        return (
            "📅 *Escolha a Data do Frete*\n\n"
            "Por favor, digite a data desejada no formato *AAAA-MM-DD* (Ex: `2026-11-15`):\n"
            "⚠️ *Atenção:* O agendamento deve ser feito com pelo menos 24h de antecedência."
        )

    @staticmethod
    def listar_turnos(turnos_livres: list) -> str:
        opcoes = "🕒 *Turnos Disponíveis para esta data:*\n\n"
        if "manha" in turnos_livres:
            opcoes += "1️⃣ - Manhã (08h às 12h)\n"
        if "tarde" in turnos_livres:
            opcoes += "2️⃣ - Tarde (13h às 17h)\n"
        if "noite" in turnos_livres:
            opcoes += "3️⃣ - Noite (18h às 22h)\n"
        opcoes += "\nDigite o número da opção desejada:"
        return opcoes

    @staticmethod
    @staticmethod
    def confirmacao_sucesso(dados: dict, turno: str) -> str:
        mapa_turno = {"manha": "Manhã", "tarde": "Tarde", "noite": "Noite"}
        turno_formatado = mapa_turno.get(turno, turno.capitalize())

        # BLINDAGEM DO VALOR NA MENSAGEM DE CONFIRMAÇÃO
        valor_bruto = dados.get('valor_estimado')
        valor_str = f"R$ {float(valor_bruto):.2f}" if valor_bruto is not None else "A definir (negociação manual)"

        return (
            "🎉 *Agendamento Confirmado com Sucesso!*\n\n"
            f"• *Data:* {dados.get('data_agendada')}\n"
            f"• *Turno:* {turno_formatado}\n"
            f"• *Origem:* {dados.get('origem_endereco')}\n"
            f"• *Destino:* {dados.get('destino_endereco')}\n"
            f"• *Valor Estimado:* {valor_str}\n\n"
            "Seu frete já está registrado na nossa agenda. Obrigado pela preferência!"
        )