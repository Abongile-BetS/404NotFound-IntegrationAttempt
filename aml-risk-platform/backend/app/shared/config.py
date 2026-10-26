from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "aml"
    postgres_user: str = "aml"
    postgres_password: str
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    keycloak_issuer: str
    keycloak_jwks_url: str
    keycloak_audience: str
    ai_base_url: str = ""
    ai_api_key: str = "local"
    ai_model_name: str = ""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.frontend_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
