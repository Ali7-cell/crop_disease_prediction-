"""
History router — view past predictions with pagination and filtering.
"""

import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Prediction, PredictionType, User
from app.schemas.history import HistoryItem, PaginatedHistory
from app.utils.auth_utils import get_current_user

router = APIRouter(tags=["Prediction History"])


@router.get("/history", response_model=PaginatedHistory)
def get_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    type: str | None = Query(None, description="Filter by prediction type: crop, fertilizer, yield"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get paginated prediction history for the current user, newest first."""

    # Base query — only current user's predictions
    query = db.query(Prediction).filter(Prediction.user_id == current_user.id)

    # Optional type filter
    if type is not None:
        # Map "yield" string to the enum value "yield_"
        type_map = {"crop": PredictionType.crop, "fertilizer": PredictionType.fertilizer, "yield": PredictionType.yield_}
        pred_type = type_map.get(type)
        if pred_type is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid type filter. Must be one of: crop, fertilizer, yield",
            )
        query = query.filter(Prediction.type == pred_type)

    # Count total before pagination
    total = query.count()

    # Paginate — newest first
    predictions = (
        query
        .order_by(Prediction.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    # Convert to response — parse input_data JSON string back to dict
    items = []
    for p in predictions:
        item = HistoryItem(
            id=p.id,
            type=p.type.value if hasattr(p.type, "value") else p.type,
            input_data=json.loads(p.input_data) if isinstance(p.input_data, str) else p.input_data,
            result=p.result,
            confidence=p.confidence,
            created_at=p.created_at,
        )
        items.append(item)

    return PaginatedHistory(items=items, total=total, page=page, limit=limit)


@router.get("/history/{prediction_id}", response_model=HistoryItem)
def get_history_detail(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single prediction record. Returns 404 if not found or not owned by current user."""

    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()

    if not prediction or prediction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )

    return HistoryItem(
        id=prediction.id,
        type=prediction.type.value if hasattr(prediction.type, "value") else prediction.type,
        input_data=json.loads(prediction.input_data) if isinstance(prediction.input_data, str) else prediction.input_data,
        result=prediction.result,
        confidence=prediction.confidence,
        created_at=prediction.created_at,
    )
