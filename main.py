"""
Agrilux API — Root Entry Point for Cloud Deployments
Exposes FastAPI app for platforms running in the repository root directory.
"""

import sys
import os

# Add backend folder to sys.path so app module can be found
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
