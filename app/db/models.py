"""
SQLAlchemy ORM models for Agrilux.

Tables:
  - users: registered farmers / consultants
  - predictions: every ML prediction saved for history
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    Index,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


# ---------- Enums ----------
class PredictionType(str, enum.Enum):
    """The three types of ML predictions Agrilux supports."""
    crop = "crop"
    fertilizer = "fertilizer"
    yield_ = "yield"


# ---------- User ----------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationship
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


# ---------- Prediction ----------
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(PredictionType, values_callable=lambda e: [x.value for x in e]), nullable=False)
    input_data = Column(Text, nullable=False)  # stored as JSON string
    result = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=True)  # null for yield (regressor)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationship
    user = relationship("User", back_populates="predictions")

    # Composite index for common query pattern: user's predictions by type
    __table_args__ = (
        Index("ix_predictions_user_type", "user_id", "type"),
    )

    def __repr__(self) -> str:
        return f"<Prediction id={self.id} type={self.type} result={self.result}>"
