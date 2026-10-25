from functools import lru_cache

import jwt
from jwt import PyJWKClient
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    keycloak_issuer: str
    keycloak_jwks_url: str
    keycloak_audience: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_jwks_client() -> PyJWKClient:
    return PyJWKClient(get_settings().keycloak_jwks_url)


def decode_access_token(token: str) -> dict:
    settings = get_settings()

    signing_key = get_jwks_client().get_signing_key_from_jwt(token)

    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.keycloak_audience,
        issuer=settings.keycloak_issuer,
    )
