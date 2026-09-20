def calculate_risk(
    disease: str,
    disease_confidence: float,
    soil_moisture: float,
    weather: dict,
) -> dict:

    disease_risk = "LOW"
    water_risk = "LOW"
    weather_risk = "UNKNOWN"

    # Disease risk
    if disease_confidence >= 0.80:
        disease_risk = "HIGH"
    elif disease_confidence >= 0.50:
        disease_risk = "MEDIUM"

    # Water risk
    if soil_moisture < 40:
        water_risk = "HIGH"
    elif soil_moisture >= 70:
        water_risk = "HIGH"
    elif soil_moisture >= 55:
        water_risk = "MEDIUM"

    # Weather risk
    if weather.get("status") == "available":
        rain_probability = weather.get("rain_probability")

        if rain_probability is not None:
            if rain_probability >= 70:
                weather_risk = "HIGH"
            elif rain_probability >= 40:
                weather_risk = "MEDIUM"
            else:
                weather_risk = "LOW"

    # Overall risk
    risks = [disease_risk, water_risk, weather_risk]

    if "HIGH" in risks:
        overall_risk = "HIGH"
    elif "MEDIUM" in risks:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    return {
        "overall_risk": overall_risk,
        "disease_risk": disease_risk,
        "water_risk": water_risk,
        "weather_risk": weather_risk,
    }
