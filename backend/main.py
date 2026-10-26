import os
import sys
import time
import uuid

# *# Configure line buffering so stdout logs flush immediately in Docker/Cloud Run*

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import requests
from starlette.concurrency import run_in_threadpool

from backend.models.harimitra.harimitra_inference import predict_disease
from backend.gemini_service import (
    generate_advisory,
    generate_chat_reply,
    get_service_unavailable_advisory,
    AdvisoryResult,
    split_bilingual_advisory,
)
from backend.weather_service import get_weather
from backend.risk_engine import calculate_risk
from backend.soil_service import build_soil_profile, get_soil_nutrients
from backend.crop_recommendation import recommend_crops
from backend.satellite_service import get_satellite_context, initialize_earth_engine
from backend.mock_agristack import MOCK_FARMER

app = FastAPI()


@app.on_event("startup")
def startup_event():
    initialize_earth_engine()


@app.get("/mock-agristack/farmer")
def get_mock_farmer():
    return MOCK_FARMER


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


def _process_analyze_sync(
    contents: bytes,
    filename: str,
    soil_moisture: float,
    latitude: float,
    longitude: float,
    language: str,
) -> dict:
    start_time = time.perf_counter()
    unique_id = uuid.uuid4().hex[:8]
    safe_filename = os.path.basename(filename or "upload.jpg")
    image_path = f"temp_{unique_id}_{safe_filename}"

    try:
        with open(image_path, "wb") as buffer:
            buffer.write(contents)

        disease_start = time.perf_counter()
        result = predict_disease(image_path)
        print(f"[PERF] Disease AI: {time.perf_counter() - disease_start:.2f}s")
        irrigation = get_irrigation_recommendation(soil_moisture)

        weather = get_weather(latitude, longitude)

        satellite_start = time.perf_counter()
        satellite = get_satellite_context(
            latitude,
            longitude,
        )
        print(f"[PERF] Satellite: {time.perf_counter() - satellite_start:.2f}s")

        agristack_context = MOCK_FARMER

        soil_start = time.perf_counter()
        soil_data = get_soil_nutrients(
            state=MOCK_FARMER["state"],
            district=MOCK_FARMER["district"],
        )
        soil_profile = build_soil_profile(soil_data)
        print(f"[PERF] SHC Soil: {time.perf_counter() - soil_start:.2f}s")

        crop_recommendations = recommend_crops(
            soil_profile=soil_profile,
            soil_moisture=soil_moisture,
            weather=weather,
            current_crop="Tomato",
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
        advisory_start = time.perf_counter()
        try:
            advisory = generate_advisory(farm_context, language=language)
        except Exception as advisory_err:
            print(f"[ERROR] generate_advisory unexpected exception: {advisory_err}")
            fallback_text = get_service_unavailable_advisory(
                result.get("disease", "Crop Condition").replace("___", " ")
            )
            en_adv, hi_adv = split_bilingual_advisory(fallback_text)
            sel_adv = hi_adv if language != "english" else en_adv
            advisory = AdvisoryResult(sel_adv, advisory_en=en_adv, advisory_hi=hi_adv)

        print(f"[PERF] AI Advisory: {time.perf_counter() - advisory_start:.2f}s")

        return {
            "filename": filename,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "analysis": result["disease"],
            "confidence": result["confidence"],
            "class_index": result["class_index"],
            "soil_moisture": soil_moisture,
            "soil_profile": soil_profile,
            "weather": weather,
            "satellite": satellite,
            "irrigation": irrigation,
            "risk": risk,
            "crop_recommendations": crop_recommendations,
            "agristack": agristack_context,
            "advisory": advisory,
            "advisory_en": getattr(advisory, "advisory_en", str(advisory)),
            "advisory_hi": getattr(advisory, "advisory_hi", str(advisory)),
        }

    finally:
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass

        print(f"[PERF] TOTAL /analyze: {time.perf_counter() - start_time:.2f}s")


@app.post("/analyze")
async def analyze_crop(
    file: UploadFile = File(...),
    soil_moisture: float = Form(62.0),
    latitude: float = Form(24.5854),
    longitude: float = Form(73.7125),
    language: str = Form("hinglish"),
):
    contents = await file.read()
    return await run_in_threadpool(
        _process_analyze_sync,
        contents=contents,
        filename=file.filename,
        soil_moisture=soil_moisture,
        latitude=latitude,
        longitude=longitude,
        language=language,
    )


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Farmer's chat question message",
    )
    language: str = "hinglish"

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Message cannot be empty or whitespace only.")
        if len(clean) > 1000:
            raise ValueError(
                "Message exceeds the maximum allowed length of 1000 characters."
            )
        return clean


@app.post("/chat")
async def chat_with_gemma(request: ChatRequest):
    reply = await run_in_threadpool(
        generate_chat_reply,
        request.message,
        request.language,
    )
    return {"reply": reply}
