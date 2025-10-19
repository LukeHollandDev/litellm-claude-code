from litellm.proxy._types import UserAPIKeyAuth, LitellmUserRoles
from fastapi import Request
import jwt
import os
import traceback

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
MASTER_KEY = os.getenv("LITELLM_MASTER_KEY", "sk-master-1234")


def map_role(role_str: str) -> LitellmUserRoles:
    """Map string role from JWT into LitellmUserRoles enum."""
    role_str = (role_str or "").lower()
    if role_str in ("admin", "proxy_admin"):
        return LitellmUserRoles.PROXY_ADMIN
    elif role_str in ("internal", "internal_user"):
        return LitellmUserRoles.INTERNAL_USER
    else:
        return LitellmUserRoles.INTERNAL_USER


async def user_api_key_auth(request: Request, api_key: str) -> UserAPIKeyAuth:
    """Authenticate user using either a JWT-based API key or master key."""

    # Master key override
    if api_key == MASTER_KEY:
        return UserAPIKeyAuth(
            api_key=api_key,
            user_id="default_user_id",
            user_role=LitellmUserRoles.PROXY_ADMIN,
            user_email="admin@litellm.local",
            metadata={"team": "admin"},
            models=["*"],  # full access
        )

    # JWT authentication
    try:
        decoded = jwt.decode(api_key, JWT_SECRET, algorithms=["HS256"])

        user_id = decoded.get("user_id")
        user_email = decoded.get("user_email")
        team_id = decoded.get("team_id")
        role = map_role(decoded.get("user_role"))
        models = decoded.get("models", ["my-mock-model"])

        return UserAPIKeyAuth(
            user_id=user_id,
            user_email=user_email,
            user_role=role,
            metadata={"team": team_id},
            models=models,
        )

    except jwt.ExpiredSignatureError:
        raise Exception("Authentication failed: token expired")
    except jwt.InvalidTokenError as e:
        raise Exception(f"Authentication failed: invalid JWT ({e})")
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Authentication failed: {e}") from e
