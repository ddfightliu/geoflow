"""
Entry point script for running the GeoFlow application.

This script serves as the main executable to launch the GeoFlow app,
allowing it to be run directly from the repository root directory.
"""

import sys

# Import the main function from the geoflow.app module
# This allows running the application from the repo root
import uvicorn
from backend.main import app

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    # Execute the main application function with command-line arguments
    # and exit with the return code from main()
    sys.exit(main(sys.argv))
