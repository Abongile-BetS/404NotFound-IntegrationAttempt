from functools import lru_cache

import jwt
from jwt import PyJWKClient

from app.shared.config import get_settings


@lru_cache
def get_jwks_client() -> PyJWKClient:
    return PyJWKClient(get_settings().keycloak_jwks_url)


def decode_access_token(token: str) -> dict[str, object]:
    settings = get_settings()

    signing_key = get_jwks_client().get_signing_key_from_jwt(token)

    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.keycloak_audience,
        issuer=settings.keycloak_issuer,
    )
