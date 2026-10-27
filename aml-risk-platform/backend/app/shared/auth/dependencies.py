from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import (
    PyJWKClientConnectionError,
    PyJWKClientError,
    PyJWTError,
)

from app.shared.auth.jwt import decode_access_token
from app.shared.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> dict[str, object]:
    if get_settings().dev_auth_bypass:
        return {
            "sub": "dev-user",
            "preferred_username": "dev",
            "email": "dev@local",
            "realm_access": {"roles": ["admin", "analyst", "manager"]},
        }

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        return decode_access_token(token)

    except PyJWKClientConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable",
        ) from exc
    except (PyJWKClientError, PyJWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


def get_user_roles(user: dict[str, object]) -> list[str]:
    realm_access = user.get("realm_access")
    if not isinstance(realm_access, dict):
        return []
    roles = realm_access.get("roles", [])
    if not isinstance(roles, list):
        return []
    return [role for role in roles if isinstance(role, str)]


def require_role(required_role: str):
    def role_checker(
        user: dict[str, object] = Depends(get_current_user),
    ) -> dict[str, object]:
        roles = get_user_roles(user)

        if required_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required",
            )

        return user

    return role_checker
