"""
Agrilux API — AI-Powered Smart Farming Assistant

Main application entry point. Sets up:
- CORS middleware
- ML model loading at startup
- Database table creation
- All API routers
- Global exception handler
- Health check endpoint
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.database import Base, engine
from app.routers import auth, crop, fertilizer, history, profile, chat
from app.routers import yield_pred
from app.utils.model_loader import load_models

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("agrilux")


# ---------- Lifespan (startup / shutdown) ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler — runs on startup and shutdown."""
    # STARTUP
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables ready")

    logger.info("Loading ML models into memory...")
    load_models()
    logger.info("✓ All ML models loaded")

    yield  # Application runs here

    # SHUTDOWN
    logger.info("Agrilux shutting down...")


# ---------- App ----------
app = FastAPI(
    title="Agrilux API",
    description="AI-Powered Smart Farming Assistant — Crop, Fertilizer, and Yield Predictions",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------- CORS ----------
raw_cors = getattr(settings, "CORS_ORIGIN", "*")
if isinstance(raw_cors, str):
    cors_origins = [o.strip() for o in raw_cors.split(",") if o.strip()]
else:
    cors_origins = list(raw_cors)

if "*" in cors_origins or not cors_origins:
    allow_origins = ["*"]
else:
    default_origins = [
        "https://agrilux.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    for origin in default_origins:
        if origin not in cors_origins:
            cors_origins.append(origin)
    allow_origins = cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ---------- Global Exception Handler ----------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions — return clean JSON, never raw stack traces."""
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


# ---------- Routers ----------
app.include_router(auth.router)
app.include_router(crop.router)
app.include_router(fertilizer.router)
app.include_router(yield_pred.router)
app.include_router(history.router)
app.include_router(profile.router)
app.include_router(chat.router)



# ---------- Root & Health Check ----------
@app.get("/", tags=["Root"])
def root():
    """Root endpoint welcoming users and providing documentation links."""
    return {
        "message": "Welcome to Agrilux API — AI-Powered Smart Farming Assistant 🌾",
        "docs": "/docs",
        "health": "/health",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Return 204 No Content for favicon requests to prevent 404 logs."""
    from fastapi import Response
    return Response(status_code=204)
