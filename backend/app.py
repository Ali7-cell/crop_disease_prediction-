"""
Agrilux — AI-Powered Smart Farming Assistant
Hugging Face Space Entry Point (Gradio + FastAPI)
"""

import os
import pandas as pd
import gradio as gr

try:
    import spaces
except ImportError:
    class spaces:
        @staticmethod
        def GPU(func):
            return func

from app.main import app
from app.utils.model_loader import ml_models, load_models

# Ensure models are loaded at module load time
if not ml_models:
    load_models()


@spaces.GPU
def gradio_predict_crop(N, P, K, temp, humidity, ph, rainfall):
    try:
        df = pd.DataFrame([{
            "N": float(N),
            "P": float(P),
            "K": float(K),
            "temperature": float(temp),
            "humidity": float(humidity),
            "ph": float(ph),
            "rainfall": float(rainfall),
        }])
        pipeline = ml_models["crop_pipeline"]
        label_encoder = ml_models["crop_label_encoder"]
        pred_encoded = pipeline.predict(df)[0]
        crop_name = label_encoder.inverse_transform([pred_encoded])[0]
        proba = float(pipeline.predict_proba(df)[0].max())
        return f"🌾 **Recommended Crop**: **{str(crop_name).capitalize()}**\n\n📊 **Confidence Score**: `{proba * 100:.2f}%`"
    except Exception as e:
        return f"❌ **Error**: {str(e)}"


@spaces.GPU
def gradio_predict_fertilizer(temp, humidity, moisture, soil_type, crop_type, N, K, P):

    try:
        df = pd.DataFrame([{
            "Temparature": float(temp),
            "Humidity ": float(humidity),  # trailing space matches model training features
            "Moisture": float(moisture),
            "Soil Type": str(soil_type),
            "Crop Type": str(crop_type),
            "Nitrogen": float(N),
            "Potassium": float(K),
            "Phosphorous": float(P),
        }])
        pipeline = ml_models["fertilizer_pipeline"]
        label_encoder = ml_models["fertilizer_label_encoder"]
        pred_encoded = pipeline.predict(df)[0]
        fert_name = label_encoder.inverse_transform([pred_encoded])[0]
        proba = float(pipeline.predict_proba(df)[0].max())
        return f"🧪 **Recommended Fertilizer**: **{fert_name}**\n\n📊 **Confidence Score**: `{proba * 100:.2f}%`"
    except Exception as e:
        return f"❌ **Error**: {str(e)}"


@spaces.GPU
def gradio_predict_yield(area, item, year, rainfall, pesticides, temp):

    try:
        df = pd.DataFrame([{
            "Area": str(area),
            "Item": str(item),
            "Year": int(year),
            "Rainfall": float(rainfall),
            "Pesticides": float(pesticides),
            "Temperature": float(temp),
        }])
        pipeline = ml_models["yield_pipeline"]
        predicted_yield = float(pipeline.predict(df)[0])
        return f"📈 **Estimated Crop Yield**: **{predicted_yield:.2f} hg/ha**"
    except Exception as e:
        return f"❌ **Error**: {str(e)}"


with gr.Blocks(title="Agrilux — AI-Powered Smart Farming Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🌾 Agrilux — AI-Powered Smart Farming Assistant")
    gr.Markdown(
        "Welcome to **Agrilux**! This Space hosts an interactive web dashboard and FastAPI REST endpoints for Crop, Fertilizer, and Yield Predictions."
    )

    with gr.Tabs():
        with gr.TabItem("🌾 Crop Recommendation"):
            gr.Markdown("### Predict the best crop for your soil and weather conditions")
            with gr.Row():
                with gr.Column():
                    N = gr.Number(label="Nitrogen (N)", value=90)
                    P = gr.Number(label="Phosphorus (P)", value=42)
                    K = gr.Number(label="Potassium (K)", value=43)
                    temp = gr.Number(label="Temperature (°C)", value=20.8)
                with gr.Column():
                    humidity = gr.Number(label="Humidity (%)", value=82.0)
                    ph = gr.Number(label="pH Value", value=6.5)
                    rainfall = gr.Number(label="Rainfall (mm)", value=202.9)
                    crop_btn = gr.Button("Recommend Crop", variant="primary")
            crop_output = gr.Markdown()
            crop_btn.click(
                gradio_predict_crop,
                inputs=[N, P, K, temp, humidity, ph, rainfall],
                outputs=crop_output,
            )

        with gr.TabItem("🧪 Fertilizer Recommendation"):
            gr.Markdown("### Recommend optimal fertilizer based on soil and crop parameters")
            with gr.Row():
                with gr.Column():
                    f_temp = gr.Number(label="Temperature (°C)", value=26)
                    f_humidity = gr.Number(label="Humidity (%)", value=52)
                    f_moisture = gr.Number(label="Moisture", value=38)
                    f_soil = gr.Dropdown(
                        label="Soil Type",
                        choices=["Sandy", "Loamy", "Black", "Red", "Clayey"],
                        value="Loamy",
                    )
                with gr.Column():
                    f_crop = gr.Dropdown(
                        label="Crop Type",
                        choices=["Maize", "Sugarcane", "Cotton", "Tobacco", "Paddy", "Barley", "Wheat", "Millets", "Oil seeds", "Pulses", "Ground Nuts"],
                        value="Maize",
                    )
                    f_N = gr.Number(label="Nitrogen", value=37)
                    f_K = gr.Number(label="Potassium", value=0)
                    f_P = gr.Number(label="Phosphorous", value=0)
                    fert_btn = gr.Button("Recommend Fertilizer", variant="primary")
            fert_output = gr.Markdown()
            fert_btn.click(
                gradio_predict_fertilizer,
                inputs=[f_temp, f_humidity, f_moisture, f_soil, f_crop, f_N, f_K, f_P],
                outputs=fert_output,
            )

        with gr.TabItem("📈 Yield Prediction"):
            gr.Markdown("### Estimate crop yield based on regional data and weather parameters")
            with gr.Row():
                with gr.Column():
                    y_area = gr.Textbox(label="Area / Country", value="Pakistan")
                    y_item = gr.Textbox(label="Item / Crop", value="Maize")
                    y_year = gr.Number(label="Year", value=2023, precision=0)
                with gr.Column():
                    y_rainfall = gr.Number(label="Average Rainfall (mm/year)", value=1200.0)
                    y_pesticides = gr.Number(label="Pesticides (tonnes)", value=150.0)
                    y_temp = gr.Number(label="Average Temperature (°C)", value=21.5)
                    yield_btn = gr.Button("Predict Yield", variant="primary")
            yield_output = gr.Markdown()
            yield_btn.click(
                gradio_predict_yield,
                inputs=[y_area, y_item, y_year, y_rainfall, y_pesticides, y_temp],
                outputs=yield_output,
            )

        with gr.TabItem("📄 REST API & Docs"):
            gr.Markdown("""
            ### FastAPI REST Endpoints
            This Hugging Face Space runs a full FastAPI backend alongside Gradio.
            
            - 📖 **Interactive OpenAPI (Swagger) Documentation**: Access [`/docs`](/docs)
            - 🔍 **Health Check Endpoint**: Access [`/health`](/health)
            """)

# Mount FastAPI app onto Gradio interface
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

