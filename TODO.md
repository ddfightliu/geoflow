# Geoflow Virtual Points Platform - Error Fixing TODO

## Current Task: Fix Project Errors

**Completed Steps:**
- [x] Create TODO.md tracking progress

**Remaining Steps:**
1. [x] Fix backend/auth/database.py (wrong collection, ObjectId handling)
2. [x] Remove/replace backend/auth/models.py (SQLAlchemy → MongoDB)
3. [x] Fix backend/auth/routes.py (event decorator, Pydantic v2, imports, types)
4. [x] Fix run_geoflow.py (missing import)
5. [ ] Test API endpoints (uvicorn backend.main:app --reload)
6. [ ] Frontend integration check (if needed)

**Testing Commands:**
```
source venv/bin/activate  # if using venv
uvicorn backend.main:app --reload --port 8000
```
Test: GET /api/auth/providers, POST /api/auth/register, etc.

**Next:** Step 1 - database.py fixes.

