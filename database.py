import json
import sqlite3


class DatabaseManager:

    def __init__(self, db_path="database_frete.sqlite"):
        self.db_path = db_path
        self.criar_tabelas()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def criar_tabelas(self):
        """Garante que todas as tabelas existam no arquivo .sqlite."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(
                """
                CREATE TABLE IF NOT EXISTS cliente (
                    telefone_cliente VARCHAR(20) PRIMARY KEY,
                    nome VARCHAR(100),
                    data_primeiro_contato TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS agenda (
                    id_slot INTEGER PRIMARY KEY AUTOINCREMENT,
                    data VARCHAR(10) NOT NULL,
                    turno VARCHAR(10) NOT NULL,
                    disponivel BOOLEAN DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS pedido (
                    id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
                    telefone_cliente VARCHAR(20) NOT NULL,
                    id_slot INTEGER,
                    origem_cep VARCHAR(9),
                    origem_bairro VARCHAR(100),
                    origem_rua VARCHAR(150),
                    origem_numero VARCHAR(20),
                    origem_complemento VARCHAR(50),
                    origem_ponto_ref VARCHAR(150),
                    origem_tipo_imovel VARCHAR(30),
                    origem_tem_elevador BOOLEAN DEFAULT 0,
                    origem_andar INTEGER DEFAULT 0,
                    destino_cep VARCHAR(9),
                    destino_bairro VARCHAR(100),
                    destino_rua VARCHAR(150),
                    destino_numero VARCHAR(20),
                    destino_complemento VARCHAR(50),
                    destino_ponto_ref VARCHAR(150),
                    destino_tipo_imovel VARCHAR(30),
                    destino_tem_elevador BOOLEAN DEFAULT 0,
                    destino_andar INTEGER DEFAULT 0,
                    tipo_servico VARCHAR(35) NOT NULL,
                    descricao_carga TEXT,
                    distancia_km REAL,
                    grau_dificuldade VARCHAR(20),
                    data_agendada VARCHAR(10) NOT NULL,
                    turno_agendado VARCHAR(10) NOT NULL,
                    valor_estimado REAL,
                    requer_negociacao_manual BOOLEAN DEFAULT 0,
                    status VARCHAR(30) DEFAULT 'AGENDADO',
                    google_event_id VARCHAR(100),
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (telefone_cliente) REFERENCES cliente(telefone_cliente) ON DELETE CASCADE,
                    FOREIGN KEY (id_slot) REFERENCES agenda(id_slot) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS midias_caminhao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo VARCHAR(50),
                    url_ou_caminho VARCHAR(255) NOT NULL,
                    tipo_midia VARCHAR(10) DEFAULT 'image'
                );

                CREATE TABLE IF NOT EXISTS sessao_bot (
                    telefone_cliente VARCHAR(20) PRIMARY KEY,
                    etapa_atual VARCHAR(50) NOT NULL DEFAULT 'MENU_PRINCIPAL',
                    dados_temporarios TEXT,
                    ultima_interacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (telefone_cliente) REFERENCES cliente(telefone_cliente) ON DELETE CASCADE
                );
            """
            )
            conn.commit()

    def abrir_ou_criar_sessao(self, telefone: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Garante inserção na tabela cliente
            cursor.execute(
                """
                INSERT INTO cliente (telefone_cliente)
                VALUES (?)
                ON CONFLICT(telefone_cliente) DO NOTHING;
            """,
                (telefone,),
            )

            # 2. Busca a sessão do bot
            cursor.execute(
                "SELECT * FROM sessao_bot WHERE telefone_cliente = ?;",
                (telefone,),
            )
            sessao = cursor.fetchone()

            # 3. Se não existir, insere na tabela sessao_bot (CORRIGIDO)
            if not sessao:
                cursor.execute(
                    """
                    INSERT INTO sessao_bot (telefone_cliente, etapa_atual, dados_temporarios)
                    VALUES (?, 'MENU_PRINCIPAL', '{}');
                """,
                    (telefone,),
                )
                conn.commit()
                return {"etapa_atual": "MENU_PRINCIPAL", "dados_temporarios": {}}

            dados_temp = (
                json.loads(sessao["dados_temporarios"])
                if sessao["dados_temporarios"]
                else {}
            )
            return {
                "etapa_atual": sessao["etapa_atual"],
                "dados_temporarios": dados_temp,
            }

    def atualizar_sessao(self, telefone: str, nova_etapa: str, novos_dados: dict):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            dados_json = json.dumps(novos_dados, ensure_ascii=False)
            cursor.execute(
                """
                UPDATE sessao_bot 
                SET etapa_atual = ?, dados_temporarios = ?, ultima_interacao = CURRENT_TIMESTAMP
                WHERE telefone_cliente = ?;
            """,
                (nova_etapa, dados_json, telefone),
            )
            conn.commit()

    def resetar_sessao(self, telefone: str):
        self.atualizar_sessao(telefone, "MENU_PRINCIPAL", {})

    def buscar_pedido_por_telefone(self, telefone: str):
        """Busca o último pedido do cliente pelo telefone."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM pedido 
                WHERE telefone_cliente = ? 
                ORDER BY criado_em DESC 
                LIMIT 1;
                """,
                (telefone,),
            )
            return cursor.fetchone()