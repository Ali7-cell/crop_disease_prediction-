"""
Pydantic schemas for prediction history endpoints.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class HistoryItem(BaseModel):
    """Single prediction history record."""
    id: int
    type: str
    input_data: Any  # parsed JSON
    result: str
    confidence: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedHistory(BaseModel):
    """Paginated list of prediction history records."""
    items: list[HistoryItem]
    total: int
    page: int
    limit: int
