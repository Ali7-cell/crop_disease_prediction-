"""
API router for the AI assistant chat endpoint.
"""

import json
import logging
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import google.generativeai as genai

from app.config import settings
from app.db.database import get_db
from app.db.models import User, Prediction, PredictionType
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.auth_utils import get_current_user
from app.utils.model_loader import ml_models

logger = logging.getLogger("agrilux.chat")

router = APIRouter(prefix="/chat", tags=["AI Assistant"])

SYSTEM_INSTRUCTION = (
    "You are Agrilux, a professional AI-powered smart farming assistant. "
    "Your goal is to assist farmers, agricultural consultants, and agronomists "
    "with scientific, practical, and sustainable farming solutions. "
    "Provide clear, actionable recommendations on crop prediction/selection, "
    "fertilizer types, yield maximization, pest control, soil management, "
    "irrigation, and weather adaptation. "
    "Maintain a helpful, encouraging, and informative tone. "
    "If the user asks questions unrelated to agriculture or farming, "
    "politely redirect them back to smart farming topics."
)


async def extract_parameters(message: str) -> dict:
    """Use Gemini to extract ML model parameters from user message in JSON format."""
    prompt = (
        "Analyze the following user query from a farmer:\n"
        f"\"{message}\"\n\n"
        "We want to extract parameters for our smart farming ML models if they are present. "
        "Determine which prediction type the query corresponds to: 'crop', 'fertilizer', 'yield', or 'none'.\n"
        "Only classify as 'crop', 'fertilizer', or 'yield' if the user provides numerical/text values for the parameters.\n"
        "Extract the parameters using the following JSON schema:\n"
        "{\n"
        "  \"prediction_type\": \"crop\" | \"fertilizer\" | \"yield\" | \"none\",\n"
        "  \"crop_params\": {\n"
        "    \"N\": float | null,\n"
        "    \"P\": float | null,\n"
        "    \"K\": float | null,\n"
        "    \"temperature\": float | null,\n"
        "    \"humidity\": float | null,\n"
        "    \"ph\": float | null,\n"
        "    \"rainfall\": float | null\n"
        "  },\n"
        "  \"fertilizer_params\": {\n"
        "    \"temperature\": float | null,\n"
        "    \"humidity\": float | null,\n"
        "    \"moisture\": float | null,\n"
        "    \"soil_type\": \"Black\" | \"Clayey\" | \"Loamy\" | \"Red\" | \"Sandy\" | null,\n"
        "    \"crop_type\": string | null,\n"
        "    \"nitrogen\": float | null,\n"
        "    \"potassium\": float | null,\n"
        "    \"phosphorous\": float | null\n"
        "  },\n"
        "  \"yield_params\": {\n"
        "    \"area\": string | null,\n"
        "    \"item\": string | null,\n"
        "    \"year\": int | null,\n"
        "    \"rainfall\": float | null,\n"
        "    \"pesticides\": float | null,\n"
        "    \"temperature\": float | null\n"
        "  }\n"
        "}\n\n"
        "Respond ONLY with the JSON object. Do not add markdown formatting or wrapper backticks."
    )
    
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL)
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Failed to parse parameters JSON: {str(e)}", exc_info=True)
        return {"prediction_type": "none"}


@router.post("", response_model=ChatResponse)
async def chat_with_assistant(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Interact with the Agrilux AI Farming Assistant.
    
    If parameters are provided, it runs local ML models, sends the prediction
    to Gemini for validation/corrections, and returns the judged answer.
    """
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not configured in environment variables.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Assistant is currently unavailable because the Gemini API Key is not configured."
        )

    try:
        # Extract parameters using Gemini asynchronously
        extracted = await extract_parameters(req.message)
        pred_type = extracted.get("prediction_type", "none")
        
        ml_prediction = None
        ml_type = None
        ml_input_data = None
        ml_result = None
        ml_confidence = None

        if pred_type == "crop":
            c_p = extracted.get("crop_params") or {}
            required = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
            if all(c_p.get(k) is not None for k in required):
                try:
                    df = pd.DataFrame([{
                        "N": float(c_p["N"]),
                        "P": float(c_p["P"]),
                        "K": float(c_p["K"]),
                        "temperature": float(c_p["temperature"]),
                        "humidity": float(c_p["humidity"]),
                        "ph": float(c_p["ph"]),
                        "rainfall": float(c_p["rainfall"]),
                    }])
                    pipeline = ml_models["crop_pipeline"]
                    label_encoder = ml_models["crop_label_encoder"]
                    
                    pred_encoded = pipeline.predict(df)[0]
                    crop_name = label_encoder.inverse_transform([pred_encoded])[0]
                    proba = float(pipeline.predict_proba(df)[0].max())
                    
                    ml_prediction = f"Crop Prediction model predicted: '{crop_name}' with confidence {proba:.4f}."
                    ml_type = PredictionType.crop
                    ml_input_data = json.dumps(c_p)
                    ml_result = str(crop_name)
                    ml_confidence = proba
                except Exception as ml_err:
                    logger.error(f"Error running local Crop model: {str(ml_err)}", exc_info=True)

        elif pred_type == "fertilizer":
            f_p = extracted.get("fertilizer_params") or {}
            required = ["temperature", "humidity", "moisture", "soil_type", "crop_type", "nitrogen", "potassium", "phosphorous"]
            if all(f_p.get(k) is not None for k in required):
                try:
                    df = pd.DataFrame([{
                        "Temparature": float(f_p["temperature"]),
                        "Humidity ": float(f_p["humidity"]),
                        "Moisture": float(f_p["moisture"]),
                        "Soil Type": str(f_p["soil_type"]),
                        "Crop Type": str(f_p["crop_type"]),
                        "Nitrogen": float(f_p["nitrogen"]),
                        "Potassium": float(f_p["potassium"]),
                        "Phosphorous": float(f_p["phosphorous"]),
                    }])
                    pipeline = ml_models["fertilizer_pipeline"]
                    label_encoder = ml_models["fertilizer_label_encoder"]
                    
                    pred_encoded = pipeline.predict(df)[0]
                    fert_name = label_encoder.inverse_transform([pred_encoded])[0]
                    proba = float(pipeline.predict_proba(df)[0].max())
                    
                    ml_prediction = f"Fertilizer Prediction model recommended: '{fert_name}' with confidence {proba:.4f}."
                    ml_type = PredictionType.fertilizer
                    ml_input_data = json.dumps(f_p)
                    ml_result = str(fert_name)
                    ml_confidence = proba
                except Exception as ml_err:
                    logger.error(f"Error running local Fertilizer model: {str(ml_err)}", exc_info=True)

        elif pred_type == "yield":
            y_p = extracted.get("yield_params") or {}
            required = ["area", "item", "year", "rainfall", "pesticides", "temperature"]
            if all(y_p.get(k) is not None for k in required):
                try:
                    df = pd.DataFrame([{
                        "Area": str(y_p["area"]),
                        "Item": str(y_p["item"]),
                        "Year": int(y_p["year"]),
                        "Rainfall": float(y_p["rainfall"]),
                        "Pesticides": float(y_p["pesticides"]),
                        "Temperature": float(y_p["temperature"]),
                    }])
                    pipeline = ml_models["yield_pipeline"]
                    
                    predicted_yield = float(pipeline.predict(df)[0])
                    
                    ml_prediction = f"Yield Prediction model predicted: {predicted_yield:.2f} hg/ha."
                    ml_type = PredictionType.yield_
                    ml_input_data = json.dumps(y_p)
                    ml_result = str(round(predicted_yield, 2))
                    ml_confidence = None
                except Exception as ml_err:
                    logger.error(f"Error running local Yield model: {str(ml_err)}", exc_info=True)

        # Prepare system instruction with dynamic judging info
        judge_instruction = SYSTEM_INSTRUCTION
        if ml_prediction:
            judge_instruction += (
                f"\n\n[CRITICAL INFO] For the user's query, the local ML model was run and returned:\n"
                f"\"{ml_prediction}\"\n"
                f"Inputs: {ml_input_data}\n\n"
                "Please judge this prediction. Validate if it is scientifically sound and correct for the given conditions. "
                "1. If it is correct and suitable, explain why to the farmer in an encouraging, practical tone and confirm this recommendation. "
                "2. If it is incorrect, unsafe, or the model returned an invalid result due to out-of-bounds inputs, correct the recommendation using your own farming knowledge. "
                "State clearly why the local prediction was not optimal and explain your corrected recommendation."
            )
        else:
            judge_instruction += (
                "\n\nNo local ML model was run because this is a general query or some parameters were missing. "
                "Answer the query directly using your own extensive agricultural/farming knowledge."
            )

        # Configure the Gemini client
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Initialize model with dynamic instruction
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=judge_instruction
        )
        
        # Parse history into Gemini's format
        gemini_history = []
        if req.history:
            for msg in req.history:
                role = "model" if msg.role in ["model", "assistant", "system"] else "user"
                gemini_history.append({
                    "role": role,
                    "parts": [msg.content]
                })

        # Start a multi-turn chat session with history
        chat_session = model.start_chat(history=gemini_history)
        
        # Send user message asynchronously
        response = await chat_session.send_message_async(req.message)
        
        # Save successfully run predictions to database history
        if ml_type is not None:
            try:
                prediction = Prediction(
                    user_id=current_user.id,
                    type=ml_type,
                    input_data=ml_input_data,
                    result=ml_result,
                    confidence=ml_confidence,
                )
                db.add(prediction)
                db.commit()
                logger.info(f"Saved chat-triggered prediction of type {ml_type} to DB.")
            except Exception as db_err:
                logger.error(f"Failed to save prediction: {str(db_err)}", exc_info=True)

        return ChatResponse(response=response.text)
        
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI Assistant Error: {str(e)}"
        )

