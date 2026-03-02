"""
FastAPI backend for Geoflow (top-level copy).

This file is a relocated copy of the original FastAPI app that lived under
`geoflow/web/backend/main.py`. Paths are adjusted so that the backend can be
run from the repository root and will serve the frontend files from
`<repo-root>/frontend/dist` if present.

Keep this file minimal and self-contained. Any future shared logic should be
moved into a common Python package under `geoflow/` and imported here.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from pathlib import Path
import os

from backend.auth.routes import router as auth_router

app = FastAPI(title="Geoflow Web API", version="0.1.0")

# Include authentication routes
app.include_router(auth_router)

# Add CORS middleware for development. In production restrict origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Serve the frontend `index.html` if a build exists, otherwise a health JSON."""
    # Expect frontend build at <repo-root>/frontend/dist
    frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Geoflow Web API", "status": "running"}


# Mount static files (assets) from frontend build when available
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists():
    assets_dir = frontend_path / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
else:
    print(f"Warning: Frontend dist directory not found at {frontend_path}")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "geoflow-web"}


@app.get("/api/project")
async def get_project_info():
    return {
        "name": "geoflow-project",
        "path": str(Path.cwd()),
        "files": ["geoflow/app.py", "geoflow/well_data.py", "run_geoflow.py"],
    }


@app.post("/api/project/load")
async def load_project(project_path: str):
    path = Path(project_path)
    if not path.exists() or not path.is_dir():
        raise HTTPException(status_code=404, detail="Project path not found")
    return {"message": f"Project loaded from {project_path}", "status": "success"}


@app.post("/api/project/create")
async def create_project(project_data: dict):
    project_name = project_data.get("name")
    if not project_name:
        raise HTTPException(status_code=400, detail="Project name is required")

    project_path = Path(f"./projects/{project_name}")
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "README.md").write_text(f"# {project_name}\n\nA new Geoflow project.")
    (project_path / "main.py").write_text("# Main application file\n\nprint('Hello, Geoflow!')")

    return {"message": f"Project '{project_name}' created successfully", "path": str(project_path)}


@app.get("/api/files/{file_path:path}")
async def get_file_content(file_path: str):
    try:
        safe_path = os.path.normpath(file_path)
        if '..' in safe_path:
            raise HTTPException(status_code=403, detail="Access denied")

        if not os.path.isfile(safe_path):
            raise HTTPException(status_code=404, detail="File not found")

        content = Path(safe_path).read_text(encoding='utf-8')
        return {"content": content, "path": file_path}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@app.post("/api/files/{file_path:path}")
async def save_file(file_path: str, content: dict):
    try:
        safe_path = os.path.normpath(file_path)
        if '..' in safe_path:
            raise HTTPException(status_code=403, detail="Access denied")

        Path(safe_path).parent.mkdir(parents=True, exist_ok=True)
        Path(safe_path).write_text(content['content'], encoding='utf-8')
        return {"message": "File saved successfully", "path": file_path}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


@app.get("/api/search")
async def search_files(q: str):
    results = []
    if q.lower() in "geoflow":
        results.append({
            "file": "geoflow/app.py",
            "line": 1,
            "content": "Main Geoflow application",
        })
    return {"results": results}


@app.get("/api/git-status")
async def get_git_status():
    return {"changes": [{"file": "geoflow/app.py", "type": "M"}, {"file": "README.md", "type": "M"}]}


@app.post("/api/git-commit")
async def commit_changes(message: str):
    return {"message": f"Committed with message: {message}"}


@app.get("/api/problems")
async def get_problems():
    return {
        "problems": [
            {
                "id": 1,
                "file": "geoflow/app.py",
                "line": 10,
                "severity": "warning",
                "message": "Unused import detected",
            }
        ]
    }


@app.get("/api/settings")
async def get_settings():
    return {"theme": "vs-dark", "fontSize": 14, "wordWrap": True}


@app.post("/api/settings")
async def save_settings(settings: dict):
    return {"message": "Settings saved"}


@app.get("/api/views")
async def get_views():
    return {"views": [{"type": "3d", "name": "3D View"}, {"type": "map", "name": "Map View"}, {"type": "well_section", "name": "Well Section View"}]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
