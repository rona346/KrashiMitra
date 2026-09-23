"""
KrashiMitra - Crop Recommendation Engine

Deterministic, explainable crop suitability engine.
Uses only available farm data and never invents missing values.
"""

from typing import Any, Dict, List, Optional

# -------------------------------------------------------------------
# Crop baseline profiles
# -------------------------------------------------------------------
# These are broad agronomic suitability ranges used only for
# explainable rule-based scoring. They are NOT live recommendations
# from an external agricultural advisory service.

CROP_PROFILES = {
    "Wheat": {
        "ideal_ph": (6.0, 7.5),
        "moisture": (40, 70),
        "rain_tolerance": "moderate",
        "nutrients": {
            "nitrogen": "high",
            "phosphorus": "medium",
            "potassium": "medium",
        },
    },
    "Rice": {
        "ideal_ph": (5.5, 7.0),
        "moisture": (60, 90),
        "rain_tolerance": "high",
        "nutrients": {
            "nitrogen": "high",
            "phosphorus": "medium",
            "potassium": "medium",
        },
    },
    "Maize": {
        "ideal_ph": (5.8, 7.0),
        "moisture": (45, 70),
        "rain_tolerance": "moderate",
        "nutrients": {
            "nitrogen": "high",
            "phosphorus": "medium",
            "potassium": "medium",
        },
    },
    "Mustard": {
        "ideal_ph": (6.0, 7.5),
        "moisture": (30, 60),
        "rain_tolerance": "low",
        "nutrients": {
            "nitrogen": "medium",
            "phosphorus": "medium",
            "potassium": "medium",
        },
    },
    "Chickpea": {
        "ideal_ph": (6.0, 7.5),
        "moisture": (30, 60),
        "rain_tolerance": "low",
        "nutrients": {
            "nitrogen": "low",
            "phosphorus": "medium",
            "potassium": "medium",
        },
    },
    "Cotton": {
        "ideal_ph": (5.5, 8.0),
        "moisture": (40, 75),
        "rain_tolerance": "moderate",
        "nutrients": {
            "nitrogen": "high",
            "phosphorus": "medium",
            "potassium": "high",
        },
    },
}


def _score_range(
    value: Optional[float],
    ideal_range: tuple,
) -> Optional[int]:
    """
    Score a numeric value against an ideal range.

    Returns:
        100 -> inside ideal range
        60  -> reasonably close to ideal range
        30  -> farther from ideal range
        None -> value unavailable
    """

    if value is None:
        return None

    minimum, maximum = ideal_range

    if minimum <= value <= maximum:
        return 100

    distance = minimum - value if value < minimum else value - maximum

    range_width = maximum - minimum

    if distance <= range_width * 0.25:
        return 60

    return 30


def _score_moisture(
    moisture: Optional[float],
    ideal_range: tuple,
) -> Optional[int]:
    """
    Score current soil moisture against crop moisture suitability.
    """

    if moisture is None:
        return None

    minimum, maximum = ideal_range

    if minimum <= moisture <= maximum:
        return 100

    # Slightly outside ideal range
    if minimum - 10 <= moisture <= maximum + 10:
        return 60

    return 30


def _score_nutrient(
    value: Optional[Any],
    nutrient_requirement: str,
) -> Optional[int]:
    """
    Broad nutrient suitability score.

    Supports both:
    - numeric nutrient values
    - SHC nutrient objects containing a nutrient level

    This is used for crop suitability screening only.
    It is NOT a fertilizer dosage recommendation.
    """

    if value is None:
        return None

    if isinstance(value, dict):
        level = str(value.get("level", "")).strip().lower()

        if not level:
            return None
    else:
        numeric_value = float(value)

        if numeric_value < 20:
            level = "low"
        elif numeric_value < 50:
            level = "medium"
        else:
            level = "high"

    if nutrient_requirement == level:
        return 100

    if nutrient_requirement == "high" and level == "medium":
        return 60

    if nutrient_requirement == "medium" and level in ("low", "high"):
        return 60

    if nutrient_requirement == "low" and level == "medium":
        return 60

    return 30


def score_crop(
    crop_name: str,
    soil_profile: Optional[Dict[str, Any]] = None,
    soil_moisture: Optional[float] = None,
    weather: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calculate an explainable suitability score for one crop.

    Missing information is ignored rather than fabricated.
    """

    soil_profile = soil_profile or {}
    weather = weather or {}

    profile = CROP_PROFILES.get(crop_name)

    if not profile:
        raise ValueError(f"Unknown crop: {crop_name}")

    scores: List[int] = []
    reasons: List[str] = []
    limitations: List[str] = []

    # ---------------------------------------------------------------
    # Soil pH
    # ---------------------------------------------------------------
    ph = soil_profile.get("ph")

    if ph is not None:
        if isinstance(ph, dict):
            ph_level = str(ph.get("level", "")).strip().lower()
        else:
            ph_level = None

        if ph_level == "neutral":
            scores.append(100)
            reasons.append("Soil pH is reported as neutral.")

        elif ph_level == "alkaline":
            scores.append(60)
            reasons.append("Soil pH is reported as alkaline.")

        elif ph_level:
            limitations.append(f"Soil pH category '{ph_level}' is not mapped.")

        else:
            limitations.append("Soil pH category is unavailable.")
    else:
        limitations.append("Soil pH is unavailable.")

    # ---------------------------------------------------------------
    # Soil moisture
    # ---------------------------------------------------------------

    moisture_score = _score_moisture(
        soil_moisture,
        profile["moisture"],
    )

    if moisture_score is not None:
        scores.append(moisture_score)

        if moisture_score == 100:
            reasons.append(
                "Current soil moisture is within the crop's broad suitable range."
            )
        elif moisture_score == 60:
            reasons.append(
                "Current soil moisture is slightly outside the broad suitable range."
            )
        else:
            reasons.append("Current soil moisture is outside the broad suitable range.")
    else:
        limitations.append("Current soil moisture is unavailable.")

    # ---------------------------------------------------------------
    # Weather
    # ---------------------------------------------------------------

    rain_probability = weather.get("rain_probability")

    if rain_probability is not None:
        rain_probability = float(rain_probability)

        rain_tolerance = profile["rain_tolerance"]

        if rain_tolerance == "high":
            weather_score = 100 if rain_probability >= 40 else 60
        elif rain_tolerance == "moderate":
            weather_score = 100 if 20 <= rain_probability <= 70 else 60
        else:
            weather_score = 100 if rain_probability < 40 else 60

        scores.append(weather_score)

        reasons.append(
            f"Available rainfall probability data was considered "
            f"({rain_probability:.0f}%)."
        )
    else:
        limitations.append("Weather data is unavailable.")

    # ---------------------------------------------------------------
    # Soil nutrients: NPK
    # ---------------------------------------------------------------

    nutrient_scores = []

    for nutrient in [
        "nitrogen",
        "phosphorus",
        "potassium",
    ]:
        value = soil_profile.get(nutrient)

        if value is None:
            continue

        requirement = profile["nutrients"][nutrient]

        nutrient_score = _score_nutrient(
            value,
            requirement,
        )

        if nutrient_score is not None:
            nutrient_scores.append(nutrient_score)

    if nutrient_scores:
        scores.extend(nutrient_scores)

        reasons.append(
            "Available soil NPK values were considered " "for crop suitability."
        )
    else:
        limitations.append("Soil NPK values are unavailable.")

    # ---------------------------------------------------------------
    # Final score
    # ---------------------------------------------------------------

    if scores:
        final_score = round(sum(scores) / len(scores))
    else:
        final_score = None

    if final_score is None:
        suitability = "INSUFFICIENT_DATA"
    elif final_score >= 80:
        suitability = "HIGH"
    elif final_score >= 60:
        suitability = "MODERATE"
    else:
        suitability = "LOW"

    return {
        "crop": crop_name,
        "score": final_score,
        "suitability": suitability,
        "reasons": reasons,
        "limitations": limitations,
    }


def recommend_crops(
    soil_profile: Optional[Dict[str, Any]] = None,
    soil_moisture: Optional[float] = None,
    weather: Optional[Dict[str, Any]] = None,
    location: Optional[Dict[str, Any]] = None,
    current_crop: Optional[str] = None,
    disease_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate a ranked crop shortlist.

    Location, current crop and disease context are accepted so the
    architecture can evolve without changing the public interface.

    They are intentionally not used for unsupported assumptions yet.
    """

    recommendations = []

    for crop_name in CROP_PROFILES:
        result = score_crop(
            crop_name=crop_name,
            soil_profile=soil_profile,
            soil_moisture=soil_moisture,
            weather=weather,
        )

        recommendations.append(result)

    # Highest score first.
    # None scores are placed at the end.
    recommendations.sort(
        key=lambda item: (
            item["score"] is not None,
            item["score"] if item["score"] is not None else -1,
        ),
        reverse=True,
    )

    # Keep the shortlist practical.
    recommendations = recommendations[:3]

    data_available = []

    if soil_profile:
        if any(value is not None for value in soil_profile.values()):
            data_available.append("soil_profile")

    if soil_moisture is not None:
        data_available.append("soil_moisture")

    if weather and any(value is not None for value in weather.values()):
        data_available.append("weather")

    if location:
        data_available.append("location")

    if disease_context:
        data_available.append("disease_context")

    if len(data_available) >= 3:
        data_completeness = "GOOD"
    elif len(data_available) >= 1:
        data_completeness = "PARTIAL"
    else:
        data_completeness = "INSUFFICIENT"

    # A recommendation based only on limited field data
    # should not be presented as high-confidence suitability.
    if data_completeness == "PARTIAL":
        for recommendation in recommendations:
            if recommendation["score"] is not None:
                recommendation["suitability"] = "LIMITED"

    limitations = set()

    for recommendation in recommendations:
        limitations.update(recommendation["limitations"])

    return {
        "current_crop": current_crop,
        "recommendations": recommendations,
        "data_completeness": data_completeness,
        "available_data": data_available,
        "limitations": sorted(limitations),
    }
