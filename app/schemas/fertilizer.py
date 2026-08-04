"""
Pydantic schemas for fertilizer prediction endpoint.

soil_type and crop_type are validated as Literal enums at the API layer.
"""

from typing import Literal
from pydantic import BaseModel, Field


# Allowed values — must match training data exactly
SOIL_TYPES = Literal["Black", "Clayey", "Loamy", "Red", "Sandy"]
CROP_TYPES = Literal[
    "Barley", "Cotton", "Ground Nuts", "Maize", "Millets",
    "Oil seeds", "Paddy", "Pulses", "Sugarcane", "Tobacco", "Wheat"
]


class FertilizerPredictionRequest(BaseModel):
    """POST /predict-fertilizer request body."""
    temperature: float = Field(..., description="Temperature in °C")
    humidity: float = Field(..., description="Relative humidity in %")
    moisture: float = Field(..., description="Soil moisture level")
    soil_type: SOIL_TYPES = Field(..., description="Type of soil")
    crop_type: CROP_TYPES = Field(..., description="Type of crop being grown")
    nitrogen: float = Field(..., description="Nitrogen content")
    potassium: float = Field(..., description="Potassium content")
    phosphorous: float = Field(..., description="Phosphorous content")


class FertilizerPredictionResponse(BaseModel):
    """POST /predict-fertilizer response body."""
    fertilizer: str
    confidence: float
