"""
Fertilizer prediction router.

Uses fertilizer_pipeline and fertilizer_label_encoder to recommend
the best fertilizer based on soil, crop, and weather conditions.

IMPORTANT: DataFrame column names must match training data EXACTLY,
including the "Temparature" typo and "Humidity " trailing space.
"""

import json

import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Prediction, PredictionType, User
from app.schemas.fertilizer import FertilizerPredictionRequest, FertilizerPredictionResponse
from app.utils.auth_utils import get_current_user
from app.utils.model_loader import ml_models

router = APIRouter(tags=["Fertilizer Prediction"])


@router.post("/predict-fertilizer", response_model=FertilizerPredictionResponse)
def predict_fertilizer(
    body: FertilizerPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Predict the best fertilizer based on soil, crop, and weather conditions."""

    # Build DataFrame with EXACT column names from training data
    # "Temparature" (misspelling) and "Humidity " (trailing space) are intentional
    df = pd.DataFrame([{
        "Temparature": body.temperature,
        "Humidity ": body.humidity,       # trailing space is required — matches training data
        "Moisture": body.moisture,
        "Soil Type": body.soil_type,
        "Crop Type": body.crop_type,
        "Nitrogen": body.nitrogen,
        "Potassium": body.potassium,
        "Phosphorous": body.phosphorous,
    }])

    # Predict
    pipeline = ml_models["fertilizer_pipeline"]
    label_encoder = ml_models["fertilizer_label_encoder"]

    pred_encoded = pipeline.predict(df)[0]
    fert_name = label_encoder.inverse_transform([pred_encoded])[0]
    proba = float(pipeline.predict_proba(df)[0].max())

    # Save prediction to database
    prediction = Prediction(
        user_id=current_user.id,
        type=PredictionType.fertilizer,
        input_data=json.dumps(body.model_dump()),
        result=str(fert_name),
        confidence=proba,
    )
    db.add(prediction)
    db.commit()

    return FertilizerPredictionResponse(fertilizer=str(fert_name), confidence=round(proba, 4))
