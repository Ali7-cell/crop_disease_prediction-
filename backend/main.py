"""
Agrilux API — Main Application Entry Point
Exposes FastAPI application instance `app` for uvicorn, fastapi CLI, and Cloud deployments.
"""

import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
