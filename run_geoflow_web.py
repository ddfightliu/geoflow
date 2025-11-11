"""
Entry point script for running the Geoflow web application.

This script serves as the main executable to launch the Geoflow web GUI,
allowing it to be run directly from the repository root directory.
"""

import sys
import uvicorn

if __name__ == '__main__':
    # Run the FastAPI application with uvicorn
    uvicorn.run("geoflow.web.backend.main:app", host="0.0.0.0", port=8000, reload=True)
