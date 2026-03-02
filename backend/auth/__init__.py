"""
Authentication module for Geoflow.

This module provides OAuth2-based authentication supporting multiple platforms:
- GitHub
- Microsoft (Azure AD)
- Feishu (飞书)
- WeChat (微信)
- Alipay (支付宝)
- Douyin (抖音)
"""

from backend.auth.config import get_settings, OAUTH_PROVIDERS
from backend.auth.database import get_db, init_db
from backend.auth.models import User
from backend.auth.schemas import (
    UserResponse,
    Token,
    OAuthRedirect,
    MessageResponse,
    ProviderList
)
from backend.auth.token import create_access_token, decode_access_token
from backend.auth.oauth import get_oauth_client, get_available_providers
from backend.auth.routes import router as auth_router

__all__ = [
    "get_settings",
    "OAUTH_PROVIDERS",
    "get_db",
    "init_db",
    "User",
    "UserResponse",
    "Token",
    "OAuthRedirect",
    "MessageResponse",
    "ProviderList",
    "create_access_token",
    "decode_access_token",
    "get_oauth_client",
    "get_available_providers",
    "auth_router"
]

