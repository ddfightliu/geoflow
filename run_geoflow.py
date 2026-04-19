#!/usr/bin/env python3
"""
Optimized entry point for GeoFlow: Backend -> Frontend sequential startup.

Starts FastAPI backend first, waits for readiness, then launches Vue dev server.
Supports graceful shutdown with Ctrl+C.

Requirements:
- Backend: uvicorn (from requirements.txt)
- Frontend: bun (Bun lockfile present)
"""

import sys
import os
import signal
import time
import subprocess
import requests
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).parent
FRONTEND_DIR = ROOT_DIR / 'frontend'

def check_backend_ready(host='http://localhost:8000', timeout=30):
    """
    Wait for backend API to be ready (check /docs as health endpoint).
    """
    print("Waiting for backend to be ready...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(host + '/docs', timeout=1)
            if response.status_code == 200:
                print("Backend ready!")
                return True
        except:
            pass
        time.sleep(0.5)
    print("Backend readiness check failed after 30s")
    return False

def signal_handler(sig, frame, processes):
    print("\nShutting down gracefully...")
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
    sys.exit(0)

async def main():
    processes = []
    
    # Global signal handler
    def handler(sig, frame):
        signal_handler(sig, frame, processes)
    
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    
    # Start backend
    print("Starting backend (FastAPI) on http://0.0.0.0:8000")
    print("Open http://localhost:8000/docs for API docs")
    port = 8000
    while True:
        try:
            import socket
            sock = socket.socket()
            sock.bind(('localhost', port))
            sock.close()
        except OSError:
            print(f"Port {port} is occupied. Trying next port...")
            port += 1
            continue
        break
    
    print(f"Backend will start on port {port}")
    backend_proc = subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 'backend.main:app',
        '--reload', '--host', '0.0.0.0', f'--port', str(port)
    ])
    
    processes.append(backend_proc)
    
    # Wait for backend ready (health check /health)
    def check_backend_ready_custom(host=f'http://localhost:{port}'):
        print(f"Waiting for backend on {host}...")
        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                response = requests.get(host + '/docs', timeout=1)
                if response.status_code == 200:
                    print("Backend ready!")
                    return True
            except:
                pass
            time.sleep(0.5)
        return False
    
    if not check_backend_ready_custom():
        print("Backend startup timeout")
        backend_proc.terminate()
        sys.exit(1)

    # Wait for backend ready
    if not check_backend_ready():
        backend_proc.terminate()
        sys.exit(1)
    
    time.sleep(2)  # Brief pause
    
    # Start frontend
    print("Starting frontend dev server (http://localhost:5173)")
    print("Press Ctrl+C to shutdown gracefully.")
    if shutil.which('bun'):
        frontend_proc = subprocess.Popen(['bun', 'dev'], cwd=str(FRONTEND_DIR))
    else:
        frontend_proc = subprocess.Popen(['npm', 'run', 'dev'], cwd=str(FRONTEND_DIR))
    processes.append(frontend_proc)
    
    print("GeoFlow full stack running!")
    print("Frontend: http://localhost:5173")
    print("Backend API: http://localhost:8000/docs")
    
    # Wait for processes
    frontend_proc.wait()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

