from backend.gemini_service import generate_advisory


farm_context = {
    "crop": "Tomato",
    "growth_stage": "Flowering",
    "soil_moisture": 62,
    "weather": "High humidity with rain expected",
    "disease": "Early blight",
    "disease_confidence": 0.91
}


advisory = generate_advisory(farm_context)

print("\n--- KrashiMitra Gemini Advisory ---\n")
print(advisory)