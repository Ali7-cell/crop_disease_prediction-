"""
Pydantic schemas for yield prediction endpoint.

area is validated against 98 countries, item against 10 crop types.
"""

from typing import Literal
from pydantic import BaseModel, Field


# 98 countries from training dataset
VALID_AREAS = Literal[
    "Albania", "Algeria", "Angola", "Argentina", "Armenia", "Australia",
    "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Belarus",
    "Belgium", "Botswana", "Brazil", "Bulgaria", "Burkina Faso", "Burundi",
    "Cameroon", "Canada", "Central African Republic", "Chile", "Colombia",
    "Croatia", "Denmark", "Dominican Republic", "Ecuador", "Egypt",
    "El Salvador", "Eritrea", "Estonia", "Finland", "France", "Germany",
    "Ghana", "Greece", "Guatemala", "Guinea", "Guyana", "Haiti", "Honduras",
    "Hungary", "India", "Indonesia", "Iraq", "Ireland", "Italy", "Jamaica",
    "Japan", "Kazakhstan", "Kenya", "Latvia", "Lebanon", "Lesotho", "Libya",
    "Lithuania", "Madagascar", "Malawi", "Malaysia", "Mali", "Mauritania",
    "Mauritius", "Mexico", "Montenegro", "Morocco", "Mozambique", "Namibia",
    "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Norway",
    "Pakistan", "Papua New Guinea", "Peru", "Poland", "Portugal", "Qatar",
    "Romania", "Rwanda", "Saudi Arabia", "Senegal", "Slovenia",
    "South Africa", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden",
    "Switzerland", "Tajikistan", "Thailand", "Tunisia", "Turkey", "Uganda",
    "Ukraine", "United Kingdom", "Uruguay", "Zambia", "Zimbabwe",
]

# 10 crop types from training dataset
VALID_ITEMS = Literal[
    "Cassava", "Maize", "Plantains and others", "Potatoes", "Rice, paddy",
    "Sorghum", "Soybeans", "Sweet potatoes", "Wheat", "Yams",
]


class YieldPredictionRequest(BaseModel):
    """POST /predict-yield request body."""
    area: VALID_AREAS = Field(..., description="Country name")
    item: VALID_ITEMS = Field(..., description="Crop name")
    year: int = Field(..., ge=1900, le=2100, description="Year of prediction")
    rainfall: float = Field(..., description="Annual rainfall in mm")
    pesticides: float = Field(..., description="Pesticides usage in tonnes")
    temperature: float = Field(..., description="Average temperature in °C")


class YieldPredictionResponse(BaseModel):
    """POST /predict-yield response body."""
    predicted_yield: float
    unit: str = "hg/ha"  # TODO: ML engineer to confirm actual unit from training dataset
