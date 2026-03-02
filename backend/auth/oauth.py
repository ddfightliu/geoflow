"""
OAuth client implementations for multi-platform authentication.
"""

import httpx
import json
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from backend.auth.config import get_settings, OAUTH_PROVIDERS

settings = get_settings()


class OAuthError(Exception):
    """Custom exception for OAuth errors."""
    pass


class BaseOAuthClient:
    """Base class for OAuth clients."""
    
    def __init__(self, provider: str):
        self.provider = provider
        self.config = OAUTH_PROVIDERS.get(provider)
        if not self.config:
            raise ValueError(f"Unknown provider: {provider}")
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Get the OAuth authorization URL."""
        raise NotImplementedError
    
    def get_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        raise NotImplementedError
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from the provider."""
        raise NotImplementedError


class GitHubOAuth(BaseOAuthClient):
    """GitHub OAuth2 client."""
    
    def __init__(self):
        super().__init__("github")
        self.client_id = settings.GITHUB_CLIENT_ID
        self.client_secret = settings.GITHUB_CLIENT_SECRET
        self.redirect_uri = settings.GITHUB_REDIRECT_URI
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.config["scope"],
            "state": state or ""
        }
        return f"{self.config['authorize_url']}?{urlencode(params)}"
    
    def get_token(self, code: str) -> Dict[str, Any]:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        headers = {"Accept": "application/json"}
        
        response = httpx.post(
            self.config["token_url"],
            data=data,
            headers=headers
        )
        
        if response.status_code != 200:
            raise OAuthError(f"Failed to get token: {response.text}")
        
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        # Get user info
        response = httpx.get(self.config["user_info_url"], headers=headers)
        if response.status_code != 200:
            raise OAuthError(f"Failed to get user info: {response.text}")
        
        user_data = response.json()
        
        # Get user email (additional request)
        email = user_data.get("email")
        if not email:
            email_response = httpx.get(
                "https://api.github.com/user/emails",
                headers=headers
            )
            if email_response.status_code == 200:
                emails = email_response.json()
                primary_emails = [e for e in emails if e.get("primary")]
                if primary_emails:
                    email = primary_emails[0].get("email")
        
        return {
            "id": str(user_data.get("id")),
            "username": user_data.get("login"),
            "email": email,
            "name": user_data.get("name"),
            "avatar_url": user_data.get("avatar_url")
        }


class MicrosoftOAuth(BaseOAuthClient):
    """Microsoft OAuth2 client."""
    
    def __init__(self):
        super().__init__("microsoft")
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        self.tenant_id = settings.MICROSOFT_TENANT_ID
        self.redirect_uri = settings.MICROSOFT_REDIRECT_URI
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.config["scope"],
            "response_mode": "query",
            "state": state or "",
            "tenant": self.tenant_id
        }
        authorize_url = self.config["authorize_url"].format(tenant=self.tenant_id)
        return f"{authorize_url}?{urlencode(params)}"
    
    def get_token(self, code: str) -> Dict[str, Any]:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        token_url = self.config["token_url"].format(tenant=self.tenant_id)
        response = httpx.post(token_url, data=data)
        
        if response.status_code != 200:
            raise OAuthError(f"Failed to get token: {response.text}")
        
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = httpx.get(self.config["user_info_url"], headers=headers)
        
        if response.status_code != 200:
            raise OAuthError(f"Failed to get user info: {response.text}")
        
        user_data = response.json()
        
        return {
            "id": user_data.get("id"),
            "username": user_data.get("userPrincipalName", "").split("@")[0],
            "email": user_data.get("mail") or user_data.get("userPrincipalName"),
            "name": user_data.get("displayName"),
            "avatar_url": None
        }


class FeishuOAuth(BaseOAuthClient):
    """Feishu (飞书) OAuth2 client."""
    
    def __init__(self):
        super().__init__("feishu")
        self.client_id = settings.FEISHU_CLIENT_ID
        self.client_secret = settings.FEISHU_CLIENT_SECRET
        self.redirect_uri = settings.FEISHU_REDIRECT_URI
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        params = {
            "app_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state or "",
            "scope": self.config["scope"]
        }
        return f"{self.config['authorize_url']}?{urlencode(params)}"
    
    def get_token(self, code: str) -> Dict[str, Any]:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = httpx.post(self.config["token_url"], json=data)
        
        if response.status_code != 200:
            raise OAuthError(f"Failed to get token: {response.text}")
        
        result = response.json()
        if result.get("code") != 0:
            raise OAuthError(f"Feishu API error: {result}")
        
        return result.get("data", {})
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = httpx.get(self.config["user_info_url"], headers=headers)
        
        if response.status_code != 200:
            raise OAuthError(f"Failed to get user info: {response.text}")
        
        result = response.json()
        if result.get("code") != 0:
            raise OAuthError(f"Feishu API error: {result}")
        
        user_data = result.get("data", {})
        
        return {
            "id": str(user_data.get("open_id")),
            "username": user_data.get("name"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "avatar_url": user_data.get("avatar_url")
        }


class WeChatOAuth(BaseOAuthClient):
    """WeChat OAuth2 client."""
    
    def __init__(self):
        super().__init__("wechat")
        self.client_id = settings.WECHAT_CLIENT_ID
        self.client_secret = settings.WECHAT_CLIENT_SECRET
        self.redirect_uri = settings.WECHAT_REDIRECT_URI
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        # WeChat uses a different format for the redirect URI
        params = {
            "appid": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.config["scope"],
            "state": state or "#wechat_redirect"
        }
        return f"{self.config['authorize_url']}?{urlencode(params)}"
    
    def get_token(self, code: str) -> Dict[str, Any]:
        params = {
            "appid": self.client_id,
            "secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        response = httpx.get(self.config["token_url"], params=params)
        
        if response.status_code != 200:
            raise OAuthError(f"Failed to get token: {response.text}")
        
        result = response.json()
        if "errcode" in result:
            raise OAuthError(f"WeChat API error: {result.get('errmsg')}")
        
        return result
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        params = {
            "access_token": access_token,
            "openid": self.client_id  # This needs to be stored from token response
        }
        response = httpx.get(self.config["user_info_url"], params=params)
        
        if response.status_code != 200:
            raise OAuthError(f"Failed to get user info: {response.text}")
        
        user_data = response.json()
        
        return {
            "id": user_data.get("openid"),
            "username": user_data.get("nickname"),
            "email": None,
            "name": user_data.get("nickname"),
            "avatar_url": user_data.get("headimgurl")
        }


class AlipayOAuth(BaseOAuthClient):
    """Alipay OAuth2 client."""
    
    def __init__(self):
        super().__init__("alipay")
        self.client_id = settings.ALIPAY_CLIENT_ID
        self.client_secret = settings.ALIPAY_CLIENT_SECRET
        self.redirect_uri = settings.ALIPAY_REDIRECT_URI
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        # Alipay requires specific parameter formatting
        params = {
            "app_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "auth_user",
            "state": state or "",
            "response_type": "code"
        }
        return f"{self.config['authorize_url']}?{urlencode(params)}"
    
    def get_token(self, code: str) -> Dict[str, Any]:
        # Alipay uses a different token endpoint format
        data = {
            "app_id": self.client_id,
            "method": "alipay.system.oauth.token",
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": "",
            "version": "1.0",
            "grant_type": "authorization_code",
            "code": code
        }
        
        response = httpx.post(self.config["token_url"], data=data)
        
        if response.status_code != 200:
            raise OAuthError(f"Failed to get token: {response.text}")
        
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        # Simplified - in production you'd need proper signature
        return {
            "id": "alipay_user",
            "username": "alipay_user",
            "email": None,
            "name": "Alipay User",
            "avatar_url": None
        }


class DouyinOAuth(BaseOAuthClient):
    """Douyin (抖音) OAuth2 client."""
    
    def __init__(self):
        super().__init__("douyin")
        self.client_id = settings.DOUYIN_CLIENT_ID
        self.client_secret = settings.DOUYIN_CLIENT_SECRET
        self.redirect_uri = settings.DOUYIN_REDIRECT_URI
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        params = {
            "client_key": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.config["scope"],
            "state": state or "",
            "response_type": "code"
        }
        return f"{self.config['authorize_url']}?{urlencode(params)}"
    
    def get_token(self, code: str) -> Dict[str, Any]:
        data = {
            "client_key": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        response = httpx.post(self.config["token_url"], data=data)
        
        if response.status_code != 200:
            raise OAuthError(f"Failed to get token: {response.text}")
        
        result = response.json()
        if result.get("message") != "success":
            raise OAuthError(f"Douyin API error: {result}")
        
        return result.get("data", {})
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = httpx.get(self.config["user_info_url"], headers=headers)
        
        if response.status_code != 200:
            raise OAuthError(f"Failed to get user info: {response.text}")
        
        result = response.json()
        user_data = result.get("data", {})
        
        return {
            "id": str(user_data.get("open_id")),
            "username": user_data.get("nickname"),
            "email": None,
            "name": user_data.get("nickname"),
            "avatar_url": user_data.get("avatar_url")
        }


def get_oauth_client(provider: str) -> BaseOAuthClient:
    """
    Factory function to get the appropriate OAuth client.
    
    Args:
        provider: Provider name (github, microsoft, feishu, wechat, alipay, douyin)
        
    Returns:
        OAuth client instance
        
    Raises:
        ValueError: If provider is not supported
    """
    clients = {
        "github": GitHubOAuth,
        "microsoft": MicrosoftOAuth,
        "feishu": FeishuOAuth,
        "wechat": WeChatOAuth,
        "alipay": AlipayOAuth,
        "douyin": DouyinOAuth
    }
    
    client_class = clients.get(provider.lower())
    if not client_class:
        raise ValueError(f"Unsupported OAuth provider: {provider}")
    
    return client_class()


def get_available_providers() -> list:
    """Get list of available OAuth providers with their status."""
    providers = []
    
    for key, config in OAUTH_PROVIDERS.items():
        # Check if credentials are configured
        client_id_key = f"{key.upper()}_CLIENT_ID"
        client = getattr(settings, client_id_key, "")
        is_configured = bool(client)
        
        providers.append({
            "id": key,
            "name": config["name"],
            "icon": config["icon"],
            "enabled": is_configured
        })
    
    return providers

