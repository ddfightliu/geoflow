"""
FastAPI backend for Geoflow web application.

This module provides the REST API endpoints for the web-based GUI.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from pathlib import Path
import json
from typing import Dict, Any

app = FastAPI(title="Geoflow Web API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

@app.get("/")
async def root():
    """Serve the main frontend page."""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Geoflow Web API", "status": "running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "geoflow-web"}

@app.get("/api/project")
async def get_project_info():
    """Get current project information."""
    # For now, return mock data. In future, integrate with workspace
    return {
        "name": "geoflow-project",
        "path": "/home/ddfightliu/myGitProjs/geoflow",
        "files": ["geoflow/app.py", "geoflow/well_data.py", "run_geoflow.py"]
    }

@app.post("/api/project/load")
async def load_project(project_path: str):
    """Load a project from the given path."""
    path = Path(project_path)
    if not path.exists() or not path.is_dir():
        raise HTTPException(status_code=404, detail="Project path not found")

    # Mock project loading - integrate with actual workspace later
    return {"message": f"Project loaded from {project_path}", "status": "success"}

import os

@app.get("/api/files/{file_path:path}")
async def get_file_content(file_path: str):
    """Get content of a file."""
    try:
        # 安全检查，防止路径遍历
        safe_path = os.path.normpath(file_path)
        if '..' in safe_path or not os.path.isfile(safe_path):
            raise HTTPException(status_code=403, detail="Access denied")
        
        content = Path(safe_path).read_text(encoding='utf-8')
        return {"content": content, "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")

@app.post("/api/files/{file_path:path}")
async def save_file(file_path: str, content: dict):
    """Save content to a file."""
    try:
        # 安全检查，防止路径遍历
        safe_path = os.path.normpath(file_path)
        if '..' in safe_path:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # 确保目录存在
        Path(safe_path).parent.mkdir(parents=True, exist_ok=True)
        Path(safe_path).write_text(content['content'], encoding='utf-8')
        return {"message": "File saved successfully", "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

@app.get("/api/search")
async def search_files(q: str):
    """Search for files and content."""
    # Mock search implementation - integrate with actual file system search later
    results = []
    if q.lower() in "geoflow":
        results.append({
            "file": "geoflow/app.py",
            "line": 1,
            "content": "Main Geoflow application"
        })
    return {"results": results}

@app.get("/api/git-status")
async def get_git_status():
    """Get Git repository status."""
    # Mock git status - integrate with actual git later
    return {
        "changes": [
            {"file": "geoflow/app.py", "type": "M"},
            {"file": "README.md", "type": "M"}
        ]
    }

@app.post("/api/git-commit")
async def commit_changes(message: str):
    """Commit changes to Git."""
    # Mock commit - integrate with actual git later
    return {"message": f"Committed with message: {message}"}

@app.get("/api/problems")
async def get_problems():
    """Get problems/errors in the project."""
    # Mock problems - integrate with actual linting/analysis later
    return {
        "problems": [
            {
                "id": 1,
                "file": "geoflow/app.py",
                "line": 10,
                "severity": "warning",
                "message": "Unused import detected"
            }
        ]
    }

@app.get("/api/settings")
async def get_settings():
    """Get user settings."""
    # Mock settings - integrate with actual settings system later
    return {
        "theme": "vs-dark",
        "fontSize": 14,
        "wordWrap": True
    }

@app.post("/api/settings")
async def save_settings(settings: dict):
    """Save user settings."""
    # Mock save - integrate with actual settings persistence later
    return {"message": "Settings saved"}

@app.get("/api/views")
async def get_views():
    """Get available view types."""
    return {
        "views": [
            {"type": "3d", "name": "3D View"},
            {"type": "map", "name": "Map View"},
            {"type": "well_section", "name": "Well Section View"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)