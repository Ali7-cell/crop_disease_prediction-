"""
Database engine, session factory, and Base for ORM models.

Supports both SQLite (dev) and PostgreSQL/Neon (production)
via the DB_URL environment variable.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# ---------- Engine Setup ----------
# SQLite needs check_same_thread=False for FastAPI's threaded access
connect_args = {}
if settings.DB_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DB_URL,
    connect_args=connect_args,
    echo=False,  # set True for SQL debugging
    pool_pre_ping=True,   # auto-reconnect stale connections (Neon drops idle ones)
    pool_recycle=300,      # recycle connections every 5 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ---------- Dependency ----------
def get_db():
    """FastAPI dependency that yields a SQLAlchemy session and closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
