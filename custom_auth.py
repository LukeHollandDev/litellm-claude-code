from litellm.proxy._types import UserAPIKeyAuth, LitellmUserRoles
from fastapi import Request
import jwt
import os
import traceback

JWT_SECRET = os.getenv("JWT_SECRET")
MASTER_KEY = os.getenv("LITELLM_MASTER_KEY")


def map_role(role_str: str) -> LitellmUserRoles:
    """Map string role from JWT into LitellmUserRoles enum."""
    role_str = (role_str or "").lower()
    if role_str in ("admin", "proxy_admin"):
        return LitellmUserRoles.PROXY_ADMIN
    elif role_str in ("internal", "internal_user"):
        return LitellmUserRoles.INTERNAL_USER
    return LitellmUserRoles.INTERNAL_USER


def extract_jwt_from_request(request: Request) -> tuple[str | None, str | None]:
    """Extract JWT, preferring cookies if available, otherwise Authorization header."""
    path = request.url.path
    auth_header = request.headers.get("authorization")
    cookie_token = request.cookies.get("token")

    if cookie_token:
        print(f"[AUTH] Using cookie token for request path: {path}")
        return cookie_token, "cookie-token"

    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1], "authorization-bearer"
        elif len(parts) == 1 and "." in parts[0]:
            return parts[0], "authorization-plain"

    return None, None


async def user_api_key_auth(request: Request, api_key: str) -> UserAPIKeyAuth:
    """Authenticate user using API key, JWT cookie, or Authorization header."""

    print("[AUTH] Starting user_api_key_auth()")
    print(f"[AUTH] API key prefix: {api_key[:10]}...")
    print(f"[AUTH] Headers: {list(request.headers.keys())}")
    print(f"[AUTH] Cookies: {list(request.cookies.keys())}")

    # 1. Master key direct match
    if api_key == MASTER_KEY:
        print("[AUTH] Master key used directly — granting PROXY_ADMIN access.")
        return UserAPIKeyAuth(
            api_key=api_key,
            user_id="default_user_id",
            user_role=LitellmUserRoles.PROXY_ADMIN,
            user_email="admin@litellm.local",
            metadata={"team": "admin", "validated_with": "MASTER_KEY_RAW"},
            models=["*"],
        )

    # 2. Extract JWT
    jwt_token, token_source = extract_jwt_from_request(request)
    print(f"[AUTH] Extracted JWT: {bool(jwt_token)} (source={token_source})")

    if not jwt_token:
        if api_key.startswith("sk-"):
            print("[AUTH] sk-* key detected, authenticating as service user.")
            return UserAPIKeyAuth(
                api_key=api_key,
                user_id="service_user",
                user_role=LitellmUserRoles.INTERNAL_USER,
                user_email="service@litellm.local",
                metadata={"team": "service", "validated_with": "STATIC_KEY"},
                models=["my-mock-model"],
            )
        raise Exception("Authentication failed: missing JWT (no header or cookie)")

    # 3. Try MASTER_KEY-based JWT
    try:
        decoded = jwt.decode(jwt_token, MASTER_KEY, algorithms=["HS256"])
        print("[AUTH] JWT decoded successfully using MASTER_KEY.")
        return UserAPIKeyAuth(
            api_key=api_key,
            user_id=decoded.get("user_id", "default_user_id"),
            user_email=decoded.get("user_email") or "admin@litellm.local",
            user_role=map_role(decoded.get("user_role")),
            metadata={
                "team": decoded.get("team_id", "admin"),
                "validated_with": "MASTER_KEY_JWT",
                "login_method": decoded.get("login_method"),
                "premium_user": decoded.get("premium_user"),
                "source": token_source,
            },
            models=decoded.get("models", ["*"]),
        )
    except jwt.InvalidTokenError:
        print("[AUTH] JWT did not validate with MASTER_KEY — trying JWT_SECRET.")

    # 4. Try JWT_SECRET-based JWT
    try:
        decoded = jwt.decode(jwt_token, JWT_SECRET, algorithms=["HS256"])
        print("[AUTH] JWT decoded successfully using JWT_SECRET.")
        return UserAPIKeyAuth(
            api_key=api_key,
            user_id=decoded.get("user_id"),
            user_email=decoded.get("user_email"),
            user_role=map_role(decoded.get("user_role")),
            metadata={
                "team": decoded.get("team_id"),
                "validated_with": "JWT_SECRET",
                "source": token_source,
            },
            models=decoded.get("models", ["my-mock-model"]),
        )
    except jwt.ExpiredSignatureError:
        raise Exception("Authentication failed: token expired")
    except jwt.InvalidTokenError as e:
        raise Exception(f"Authentication failed: invalid JWT ({e})")
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Authentication failed: {e}") from e
