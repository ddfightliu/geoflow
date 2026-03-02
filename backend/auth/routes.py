"""
Authentication API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

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
from backend.auth.oauth import get_oauth_client, get_available_providers, OAuthError
from backend.auth.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Initialize database on module load
init_db()


@router.get("/providers", response_model=ProviderList)
async def list_providers():
    """
    Get list of available OAuth providers.
    """
    providers = get_available_providers()
    return {"providers": providers}


@router.get("/login/{provider}", response_model=OAuthRedirect)
async def oauth_login(provider: str, state: Optional[str] = Query(None)):
    """
    Redirect to OAuth provider authorization page.
    """
    try:
        client = get_oauth_client(provider)
        auth_url = client.get_authorization_url(state)
        return {"authorization_url": auth_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create authorization URL: {str(e)}")


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str, 
    code: str = Query(...),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback and create/update user.
    """
    try:
        # Get OAuth client and exchange code for token
        client = get_oauth_client(provider)
        token_data = client.get_token(code)
        
        # Get user info from provider
        access_token = token_data.get("access_token")
        user_info = client.get_user_info(access_token)
        
        # Check if user exists
        existing_user = db.query(User).filter(
            User.provider == provider,
            User.provider_id == user_info["id"]
        ).first()
        
        if existing_user:
            # Update existing user
            existing_user.email = user_info.get("email") or existing_user.email
            existing_user.full_name = user_info.get("name") or existing_user.full_name
            existing_user.avatar_url = user_info.get("avatar_url") or existing_user.avatar_url
            db.commit()
            user = existing_user
        else:
            # Create new user
            user = User(
                email=user_info.get("email"),
                username=user_info.get("username") or user_info.get("name") or f"{provider}_{user_info['id']}",
                full_name=user_info.get("name"),
                avatar_url=user_info.get("avatar_url"),
                provider=provider,
                provider_id=user_info["id"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create JWT token
        token_payload = {
            "sub": str(user.id),
            "username": user.username,
            "type": "access"
        }
        
        access_token_jwt = create_access_token(
            data=token_payload,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Redirect to frontend with token
        # In production, you'd redirect to a proper OAuth callback page on frontend
        frontend_url = f"?token={access_token_jwt}&user_id={user.id}"
        
        return RedirectResponse(url=f"/#/login/success{frontend_url}")
        
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.post("/token", response_model=Token)
async def get_token(
    grant_type: str = Query(...),
    code: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Exchange OAuth code for JWT token (alternative endpoint).
    """
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="Invalid grant type")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code required")
    
    # This is a simplified version - in production, you'd determine provider from state
    # For now, return error suggesting to use callback endpoint
    raise HTTPException(
        status_code=400, 
        detail="Please use /api/auth/callback/{provider} endpoint"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    authorization: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """
    Logout user (client-side token removal).
    """
    # JWT tokens are stateless, so logout is handled client-side
    # In production, you might want to implement token blacklist
    return {"message": "Logged out successfully", "success": True}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Refresh JWT token.
    """
    # In production, implement proper refresh token flow
    raise HTTPException(status_code=501, detail="Token refresh not implemented")


# Dependency for protected routes
async def get_current_active_user(
    authorization: str = Query(None),
    db: Session = Depends(get_db)
) -> User:
    """Dependency for getting current active user."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user

