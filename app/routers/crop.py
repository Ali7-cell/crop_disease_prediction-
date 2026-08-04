"""
Crop prediction router.

Uses crop_pipeline and crop_label_encoder to predict the best crop
for given soil and weather conditions.
"""

import json

import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Prediction, PredictionType, User
from app.schemas.crop import CropPredictionRequest, CropPredictionResponse
from app.utils.auth_utils import get_current_user
from app.utils.model_loader import ml_models

router = APIRouter(tags=["Crop Prediction"])


@router.post("/predict-crop", response_model=CropPredictionResponse)
def predict_crop(
    body: CropPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Predict the best crop based on soil nutrients and weather conditions."""

    # Build DataFrame with exact column names matching training data
    df = pd.DataFrame([{
        "N": body.N,
        "P": body.P,
        "K": body.K,
        "temperature": body.temperature,
        "humidity": body.humidity,
        "ph": body.ph,
        "rainfall": body.rainfall,
    }])

    # Predict
    pipeline = ml_models["crop_pipeline"]
    label_encoder = ml_models["crop_label_encoder"]

    pred_encoded = pipeline.predict(df)[0]
    crop_name = label_encoder.inverse_transform([pred_encoded])[0]
    proba = float(pipeline.predict_proba(df)[0].max())

    # Save prediction to database
    prediction = Prediction(
        user_id=current_user.id,
        type=PredictionType.crop,
        input_data=json.dumps(body.model_dump()),
        result=str(crop_name),
        confidence=proba,
    )
    db.add(prediction)
    db.commit()

    return CropPredictionResponse(crop=str(crop_name), confidence=round(proba, 4))
