from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from pydantic import BaseModel

from backend.models.harimitra.harimitra_inference import predict_disease
from backend.gemini_service import generate_advisory, generate_chat_reply
from backend.weather_service import get_weather
from backend.risk_engine import calculate_risk
from backend.soil_service import build_soil_profile
from backend.crop_recommendation import recommend_crops
from backend.satellite_service import get_satellite_context, initialize_earth_engine

app = FastAPI()


@app.on_event("startup")
def startup_event():
    initialize_earth_engine()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "KrishiMitra AI backend is running"}


def get_irrigation_recommendation(soil_moisture):
    if soil_moisture < 40:
        return "Irrigation Required"
    elif soil_moisture <= 70:
        return "Irrigation Not Required"
    else:
        return "Irrigation Not Required - Soil Moisture High"


@app.post("/analyze")
async def analyze_crop(
    file: UploadFile = File(...),
    soil_moisture: float = Form(62.0),
    latitude: float = Form(24.5854),
    longitude: float = Form(73.7125),
):
    image_path = f"temp_{file.filename}"

    try:
        with open(image_path, "wb") as buffer:
            buffer.write(await file.read())

        result = predict_disease(image_path)
        irrigation = get_irrigation_recommendation(soil_moisture)

        weather = get_weather(latitude, longitude)

        satellite = get_satellite_context(
            latitude,
            longitude,
        )

        soil_profile = build_soil_profile({})

        crop_recommendations = recommend_crops(
            soil_profile=soil_profile,
            soil_moisture=soil_moisture,
            weather=weather,
        )

        risk = calculate_risk(
            disease=result["disease"],
            disease_confidence=result["confidence"],
            soil_moisture=soil_moisture,
            weather=weather,
        )

        farm_context = {
            "crop": "Tomato",
            "growth_stage": "Unknown",
            "latitude": latitude,
            "longitude": longitude,
            "soil_moisture": soil_moisture,
            "soil_profile": soil_profile,
            "weather": weather,
            "satellite": satellite,
            "disease": result["disease"],
            "disease_confidence": result["confidence"],
            "risk": risk,
            "crop_recommendations": crop_recommendations,
        }

        advisory = generate_advisory(farm_context)

        return {
            "filename": file.filename,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "analysis": result["disease"],
            "confidence": result["confidence"],
            "class_index": result["class_index"],
            "soil_moisture": soil_moisture,
            "soil_profile": soil_profile,
            "satellite": satellite,
            "irrigation": irrigation,
            "risk": risk,
            "crop_recommendations": crop_recommendations,
            "advisory": advisory,
        }

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat_with_gemma(request: ChatRequest):
    prompt = f"""
You are KrishiMitra AI, a helpful agriculture assistant for Indian farmers.

Answer the farmer naturally and directly in simple Hindi or easy Hinglish.
Be friendly, practical, and concise.
Stay focused on the farmer's exact question.
Do not mix Bengali, Gujarati, or other languages.
Do not invent facts, disease names, medicines, or treatments.
If you cannot determine the exact cause from the question, say that clearly
and suggest what the farmer should check or ask them to upload a crop/leaf photo.

Farmer's question:
{request.message}
"""

    return {"reply": generate_chat_reply(request.message)}
