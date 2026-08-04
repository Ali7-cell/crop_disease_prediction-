"""
Pydantic schemas for crop prediction endpoint.

Validation ranges match the training dataset bounds.
"""

from pydantic import BaseModel, Field


class CropPredictionRequest(BaseModel):
    """POST /predict-crop request body."""
    N: int = Field(..., ge=0, le=140, description="Nitrogen content in soil")
    P: int = Field(..., ge=0, le=145, description="Phosphorus content in soil")
    K: int = Field(..., ge=0, le=205, description="Potassium content in soil")
    temperature: float = Field(..., ge=-10, le=55, description="Temperature in °C")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity in %")
    ph: float = Field(..., ge=0, le=14, description="Soil pH value")
    rainfall: float = Field(..., ge=0, le=350, description="Rainfall in mm")


class CropPredictionResponse(BaseModel):
    """POST /predict-crop response body."""
    crop: str
    confidence: float
