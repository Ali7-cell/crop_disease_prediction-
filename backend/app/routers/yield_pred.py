"""
Yield prediction router.

Uses yield_pipeline (a regressor) to predict crop yield.
No label encoder or confidence score for this model.
"""

import json

import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Prediction, PredictionType, User
from app.schemas.yield_pred import YieldPredictionRequest, YieldPredictionResponse
from app.utils.auth_utils import get_current_user
from app.utils.model_loader import ml_models

router = APIRouter(tags=["Yield Prediction"])


@router.post("/predict-yield", response_model=YieldPredictionResponse)
def predict_yield(
    body: YieldPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Predict crop yield for a given country, crop, year, and conditions."""

    # Build DataFrame with exact column names matching training data
    df = pd.DataFrame([{
        "Area": body.area,
        "Item": body.item,
        "Year": body.year,
        "Rainfall": body.rainfall,
        "Pesticides": body.pesticides,
        "Temperature": body.temperature,
    }])

    # Predict — this is a regressor, no proba or label decoding
    pipeline = ml_models["yield_pipeline"]
    predicted_yield = float(pipeline.predict(df)[0])

    # Save prediction to database (confidence is null for regressor)
    prediction = Prediction(
        user_id=current_user.id,
        type=PredictionType.yield_,
        input_data=json.dumps(body.model_dump()),
        result=str(round(predicted_yield, 2)),
        confidence=None,
    )
    db.add(prediction)
    db.commit()

    return YieldPredictionResponse(
        predicted_yield=round(predicted_yield, 2),
        unit="hg/ha",  # TODO: ML engineer to confirm actual unit from training dataset
    )
