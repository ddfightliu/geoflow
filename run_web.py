#!/usr/bin/env python3
"""
Run both the FastAPI backend and the Bun/Vite frontend for development.

This script starts the Python backend (uvicorn) and the frontend dev server
(using Bun to run the npm scripts) concurrently and forwards their output.

Usage: python run_web.py

Requirements:
- Python packages from `requirements.txt` (fastapi, uvicorn)
- Bun installed and available on PATH for frontend dependencies (see README)
"""
import asyncio
import os
import signal
import sys
from pathlib import Path


ROOT = Path(__file__).parent.resolve()
# Prefer top-level `frontend/` if present; fall back to `geoflow/web/frontend` for compatibility.
if (ROOT / "frontend").exists():
    FRONTEND_DIR = ROOT / "frontend"
else:
    FRONTEND_DIR = ROOT / "geoflow" / "web" / "frontend"


async def stream_proc(cmd, cwd=None, name=None):
    env = os.environ.copy()
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        cwd=str(cwd) if cwd else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    async for line in proc.stdout:
        sys.stdout.buffer.write(f"[{name}] ".encode())
        sys.stdout.buffer.write(line)
        await asyncio.sleep(0)

    return await proc.wait()


async def main():
    # Backend command: run uvicorn via the current Python interpreter
    # Use top-level backend if available for clearer separation.
    backend_target = "backend.main:app" if (ROOT / "backend").exists() else "geoflow.web.backend.main:app"
    backend_cmd = [sys.executable, "-m", "uvicorn", backend_target, "--reload", "--host", "127.0.0.1", "--port", "8000"]
    print(f"Backend command: {' '.join(backend_cmd)} cwd={ROOT}")

    # Frontend command: use bun to run the `dev` script from package.json
    frontend_cmd = ["bun", "run", "dev"]
    if os.name == 'nt':  # Windows
        frontend_cmd = ['cmd', '/c'] + frontend_cmd
        print(f"Frontend command: {' '.join(frontend_cmd)} cwd={FRONTEND_DIR}")

        # Ensure frontend dir exists
        if not FRONTEND_DIR.exists():
            print(f"Frontend directory not found: {FRONTEND_DIR}")
            return 1

        print("Starting backend and frontend (use Ctrl-C to stop)...")

        tasks = [
            asyncio.create_task(stream_proc(backend_cmd, cwd=ROOT, name="backend")),
            asyncio.create_task(stream_proc(frontend_cmd, cwd=FRONTEND_DIR, name="frontend")),
        ]

        # Handle SIGINT/SIGTERM
        loop = asyncio.get_running_loop()
        stop = asyncio.Event()

        def _stop(*_):
            stop.set()

        try:
            loop.add_signal_handler(signal.SIGINT, _stop)
            loop.add_signal_handler(signal.SIGTERM, _stop)
        except NotImplementedError:
            pass  # Windows fallback

        try:
            await stop.wait()
        except KeyboardInterrupt:
            stop.set()

        for t in tasks:
            t.cancel()

        # Give subprocesses a moment to terminate
        await asyncio.sleep(0.2)

        return 0


if __name__ == "__main__":
    try:
        raise_code = asyncio.run(main())
        sys.exit(raise_code or 0)
    except KeyboardInterrupt:
        print("Shutting down")
        sys.exit(0)
