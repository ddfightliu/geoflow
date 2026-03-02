# User Management Implementation Plan

## Information Gathered:
- **Current Backend**: FastAPI with basic API endpoints (project management, file operations)
- **Current Frontend**: Vue 3 + Vite with minimal template
- **Dependencies**: FastAPI, uvicorn, Vue 3, vue-router

## Plan:

### Phase 1: Backend Implementation

#### 1.1 Install Required Dependencies
Add to requirements.txt:
- `python-jose[cryptography]` - JWT token handling
- `passlib[bcrypt]` - Password hashing
- `Authlib` - OAuth client for multiple platforms
- `sqlalchemy` - Database ORM
- `pydantic[email]` - Email validation
- `python-multipart` - Form data handling
- `httpx` - HTTP client for OAuth

#### 1.2 Create Backend User Module Structure
```
backend/
├── auth/
│   ├── __init__.py
│   ├── config.py          # OAuth configurations
│   ├── database.py        # SQLAlchemy setup
│   ├── models.py          # User model
│   ├── schemas.py         # Pydantic schemas
│   ├── oauth.py           # OAuth client setup
│   ├── token.py           # JWT token handling
│   └── routes.py          # Auth endpoints
```

#### 1.3 Implement OAuth Providers
Supported platforms:
- GitHub (OAuth2)
- Microsoft (Azure AD OAuth2)
- 飞书/Feishu (OAuth2)
- WeChat (OAuth2) - requires verification
- Alipay (OAuth2) - requires business license
- Douyin/TikTok (OAuth2)

#### 1.4 Add User API Endpoints
- POST `/api/auth/login/{provider}` - OAuth login redirect
- GET `/api/auth/callback/{provider}` - OAuth callback
- POST `/api/auth/token` - Get JWT token
- GET `/api/auth/me` - Get current user info
- POST `/api/auth/logout` - Logout

### Phase 2: Frontend Implementation

#### 2.1 Install Frontend Dependencies
- `axios` - HTTP client
- `pinia` - State management
- `vue-auth3` or implement custom OAuth

#### 2.2 Create Frontend Structure
```
frontend/src/
├── stores/
│   └── auth.js           # Pinia auth store
├── components/
│   └── LoginButton.vue   # OAuth login buttons
├── views/
│   └── Login.vue         # Login page
├── router/
│   └── index.js          # Vue router with auth
```

### Phase 3: Configuration

#### 3.1 OAuth Credentials (Environment Variables)
Each OAuth provider requires credentials. Document required env vars:
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`
- `MICROSOFT_CLIENT_ID` / `MICROSOFT_CLIENT_SECRET`
- `FEISHU_CLIENT_ID` / `FEISHU_CLIENT_SECRET`
- `WECHAT_CLIENT_ID` / `WECHAT_CLIENT_SECRET`
- `ALIPAY_CLIENT_ID` / `ALIPAY_CLIENT_SECRET`
- `DOUYIN_CLIENT_ID` / `DOUYIN_CLIENT_SECRET`
- `JWT_SECRET_KEY` - For token signing

## Dependent Files to be Edited:
1. `requirements.txt` - Add Python dependencies
2. `backend/main.py` - Add auth routes and middleware
3. `frontend/package.json` - Add frontend dependencies
4. `frontend/src/main.js` - Add Pinia and router
5. `frontend/src/App.vue` - Add auth-aware layout
6. Create new files under `backend/auth/` directory

## Followup Steps:
1. Create TODO.md with step-by-step tasks
2. Install all dependencies
3. Implement backend auth module
4. Implement frontend auth UI
5. Test OAuth flows (may need actual credentials)

