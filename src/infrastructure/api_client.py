import requests
from requests.exceptions import RequestException
from src.config.settings import settings
from src.utils.logger import logger


class APIClient:
    def __init__(self):
        self.base_url = settings.API_BASE_URL
        self.username = settings.API_USERNAME
        self.password = settings.API_PASSWORD
        self.token = None
        self.session = requests.Session()
        self.timeout = 10  

    def get_token(self) -> str | None:
        """
        Realiza autenticação na API e armazena o token JWT.
        """
        url = f"{self.base_url}/login"
        payload = {
            "username": self.username,
            "password": self.password
        }

        try:
            logger.info("🔐 Solicitando token JWT...")
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            self.token = data.get("access_token")

            if not self.token:
                logger.error("❌ Token não encontrado na resposta da API.")
                return None

            logger.info("✅ Token JWT obtido com sucesso.")
            return self.token

        except RequestException as e:
            logger.error(f"❌ Erro ao autenticar na API: {e}")
            return None

    def _build_headers(self) -> dict:
        """
        Monta os headers com Authorization.
        """
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def fetch_data(self, endpoint: str, params: dict | None = None):
        """
        Busca dados de um endpoint protegido por JWT.
        Implementa:
        - Renovação automática de token (401)
        - Retry simples (até 3 tentativas)
        """

        if not self.token:
            if not self.get_token():
                logger.error("❌ Não foi possível obter token.")
                return None

        url = f"{self.base_url}/{endpoint}"

        for attempt in range(1, 4): 
            try:
                logger.info(f"📡 Requisição GET -> {endpoint} (tentativa {attempt})")

                response = self.session.get(
                    url,
                    headers=self._build_headers(),
                    params=params,
                    timeout=self.timeout
                )

                # Se token expirou
                if response.status_code == 401:
                    logger.warning("🔄 Token expirado. Renovando...")
                    if not self.get_token():
                        return None
                    continue  

                response.raise_for_status()

                logger.info(f"✅ Dados extraídos com sucesso do endpoint: {endpoint}")
                return response.json()

            except RequestException as e:
                logger.warning(f"⚠️ Tentativa {attempt} falhou: {e}")

        logger.error(f"❌ Falha definitiva ao buscar dados do endpoint: {endpoint}")
        return None

    def close(self):
        """
        Fecha a sessão HTTP (boa prática para encerramento do pipeline).
        """
        self.session.close()
        logger.info("🔌 Sessão HTTP encerrada.")


# Instância global para uso no pipeline
api_client = APIClient()