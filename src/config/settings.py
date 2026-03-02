import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.API_USERNAME = self._get_env("API_USERNAME")
        self.API_PASSWORD = self._get_env("API_PASSWORD")
        self.API_BASE_URL = self._get_env("API_BASE_URL")

        self.DB_USER = self._get_env("DB_USER")
        self.DB_PASSWORD = self._get_env("DB_PASSWORD")
        self.DB_HOST = self._get_env("DB_HOST")
        self.DB_PORT = self._get_env("DB_PORT")
        self.DB_NAME = self._get_env("DB_NAME")

    def _get_env(self, key: str):
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Variável de ambiente '{key}' não definida.")
        return value

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

settings = Settings()