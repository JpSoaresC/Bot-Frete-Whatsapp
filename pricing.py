from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import time
import re


class PricingCalculator:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="bot_frete_app", timeout=10)
        self.VALOR_POR_KM = 6.00
        self.RAIO_LOCAL_KM = 30.00

        # Bairros do RJ com coordenadas aproximadas (fallback)
        self.bairros_rj = {
            "copacabana": (-22.9711, -43.1822),
            "ipanema": (-22.9838, -43.2096),
            "leblon": (-22.9844, -43.2233),
            "botafogo": (-22.9519, -43.1822),
            "flamengo": (-22.9322, -43.1781),
            "centro": (-22.9035, -43.1728),
            "tijuca": (-22.9311, -43.2289),
            "barra da tijuca": (-23.0044, -43.3647),
            "recreio": (-23.0186, -43.4589),
            "jacarepaguá": (-22.9667, -43.3667),
            "madureira": (-22.8711, -43.3311),
            "campo grande": (-22.9031, -43.5631),
            "santa cruz": (-22.9231, -43.6831),
            "niterói": (-22.8833, -43.1036),
            "são gonçalo": (-22.8267, -43.0531),
            "duque de caxias": (-22.7856, -43.3117),
            "nova iguaçu": (-22.7592, -43.4511),
            "belém": (-1.4558, -48.5044),
            "são paulo": (-23.5505, -46.6333),
            "rio de janeiro": (-22.9068, -43.1729),
        }

    def normalizar_endereco(self, endereco: str) -> str:
        """Remove caracteres especiais e padroniza."""
        endereco = endereco.lower().strip()
        endereco = re.sub(r'[^\w\s,]', '', endereco)
        return endereco

    def obter_coordenadas(self, endereco: str) -> tuple:
        """Tenta geocodificar com múltiplas estratégias."""
        endereco_norm = self.normalizar_endereco(endereco)

        # Buscar por bairro conhecido do RJ
        for bairro, coords in self.bairros_rj.items():
            if bairro in endereco_norm:
                print(f"📍 Match por bairro: {bairro} → {coords}")
                return coords

        # Geocodificação via Nominatim (com retry)
        tentativas = 3
        for i in range(tentativas):
            try:
                time.sleep(1.5)  # Rate limit do Nominatim
                query = f"{endereco}, Rio de Janeiro, RJ, Brasil"
                print(f"🔍 Tentativa {i + 1}: {query}")

                localizacao = self.geolocator.geocode(
                    query,
                    exactly_one=True,
                    timeout=10
                )

                if localizacao:
                    coords = (localizacao.latitude, localizacao.longitude)
                    print(f"✅ Geocodificado: {coords}")
                    return coords

            except Exception as e:
                print(f"⚠️ Erro geocodificação (tentativa {i + 1}): {e}")
                if i < tentativas - 1:
                    time.sleep(2)

        # Estratégia 3: Fallback - coordenadas do centro do RJ
        print(f"⚠️ Fallback: usando centro do RJ")
        return (-22.9068, -43.1729)

    def calcular_distancia_km(self, endereco_origem: str, endereco_destino: str) -> float:
        coords_origem = self.obter_coordenadas(endereco_origem)
        time.sleep(1)  # Rate limit entre chamadas
        coords_destino = self.obter_coordenadas(endereco_destino)

        print(f"📍 Origem: {endereco_origem} → {coords_origem}")
        print(f"📍 Destino: {endereco_destino} → {coords_destino}")

        if coords_origem and coords_destino:
            distancia_direta = geodesic(coords_origem, coords_destino).km
            distancia_estimada_rua = distancia_direta * 1.3
            print(f"📏 Distância direta: {distancia_direta:.2f}km | Estimada: {distancia_estimada_rua:.2f}km")
            return round(distancia_estimada_rua, 2)

        print(f"❌ Não foi possível calcular distância")
        return 0.0

    def avaliar_orcamento(
            self,
            tipo_servico: str,
            endereco_origem: str,
            endereco_destino: str,
            tem_escada: bool = False
    ) -> dict:
        distancia = self.calcular_distancia_km(endereco_origem, endereco_destino)

        # Se distância for 0, usar valor padrão de 50km para não travar
        if distancia == 0:
            distancia = 50.0
            print(f"⚠️ Distância 0, usando fallback: {distancia}km")

        # Mudança completa ou com escada, sempre negociação manual
        if tipo_servico == "mudanca_completa" or tem_escada:
            return {
                "requer_negociacao": True,
                "motivo": "Mudanças completas ou transporte com escadas exigem orçamento direto com o gerente.",
                "distancia_km": distancia,
                "valor_estimado": None,
            }

        # Frete simples com distância >= 30km, cálculo automático
        if distancia >= self.RAIO_LOCAL_KM:
            valor_calculado = round(distancia * self.VALOR_POR_KM, 2)
            return {
                "requer_negociacao": False,
                "motivo": "Cálculo automático de longa distância.",
                "distancia_km": distancia,
                "valor_estimado": valor_calculado,
            }

        # Frete simples mas distância < 30km, negociação manual
        return {
            "requer_negociacao": True,
            "motivo": f"Serviço na região local ({distancia:.1f}km). Requer avaliação do gerente.",
            "distancia_km": distancia,
            "valor_estimado": None,
        }