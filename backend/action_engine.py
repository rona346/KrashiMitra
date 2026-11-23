"""
KrashiMitra - Farm Action Agent Engine
---------------------------------------
Generates grounded, prioritized, non-hallucinatory farm actions from verified
multi-modal farm telemetry (computer vision pathology screening, Open-Meteo
meteorological data, user-provided soil moisture, National Soil Health Card
benchmark records, and Sentinel-2 satellite NDVI).

Design & Safety Constraints:
- Zero Agronomic Guesswork: No universal soil moisture cutoffs (<40%, >70%)
  and no fixed depth instructions (10-15 cm). Moisture is reported as a
  user-provided value requiring in-situ field verification.
- Zero Chemical Prescriptions: No chemical spray orders, no invented spray
  windows, and no fertilizer dosage/quantity claims.
- Zero Destructive Interventions: Disease model screening advises in-field
  multi-plant verification and KVK consultation, never leaf removal or rogueing.
- Precautionary Weather Guidance: Rain probability >=60% is an application-defined
  alert heuristic (not an agronomic standard). It requires a valid finite probability
  between 0 and 100% and advises label rainfast checks without inferring rain timing
  or prescribing spray delays.
- AgriStack Demo Isolation: Synthetic mock farmer data is strictly ignored.
- Grounded Evidence: Returns only actions supported by verified telemetry. If
  telemetry is missing, invalid, or unverified, returns an empty list ([]).
"""

import math
from typing import Any, Dict, List, Optional


def _is_finite_number(val: Any) -> bool:
    """
    Validate that val is a finite real number.
    Rejects None, booleans (which inherit from int), NaN, and infinities.
    """
    if val is None or isinstance(val, bool):
        return False
    if not isinstance(val, (int, float)):
        return False
    try:
        return math.isfinite(float(val))
    except (ValueError, TypeError, OverflowError):
        return False


def generate_farm_actions(farm_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Evaluate available farm telemetry and return prioritized, grounded actions.

    Returns an empty list ([]) if no trustworthy telemetry evidence is available.
    """
    if not farm_context or not isinstance(farm_context, dict):
        return []

    actions: List[Dict[str, Any]] = []

    # Extract telemetry components with safe defaults
    disease = farm_context.get("disease")
    disease_confidence = farm_context.get("disease_confidence")
    soil_moisture = farm_context.get("soil_moisture")
    weather = farm_context.get("weather") if isinstance(farm_context.get("weather"), dict) else {}
    soil_profile = farm_context.get("soil_profile") if isinstance(farm_context.get("soil_profile"), dict) else {}
    satellite = farm_context.get("satellite") if isinstance(farm_context.get("satellite"), dict) else {}
    location = farm_context.get("location") if isinstance(farm_context.get("location"), dict) else {}

    # Reliable district extraction: do not invent or claim a district when absent
    raw_district = location.get("district") or farm_context.get("district")
    has_reliable_district = bool(
        raw_district
        and isinstance(raw_district, str)
        and raw_district.strip()
        and raw_district.strip().lower() not in ("your district", "unknown", "none", "")
    )
    district_name = raw_district.strip() if has_reliable_district else None

    # -------------------------------------------------------------------------
    # Rule 1: Pathology Screening Verification (Not a Confirmed Diagnosis)
    # -------------------------------------------------------------------------
    if disease and isinstance(disease, str) and disease.strip():
        disease_clean = disease.strip()
        if "healthy" in disease_clean.lower():
            actions.append({
                "id": "ACTION_FOLIAR_HEALTHY_OBSERVATION",
                "priority": 2,
                "timeframe": "NEXT_FIELD_VISIT",
                "category": "PATHOLOGY_VERIFICATION",
                "title": "Continue Routine Foliar Observation",
                "action": (
                    "Foliar image screening indicates a healthy leaf condition. "
                    "Continue routine visual field walks to monitor for emerging "
                    "pest or disease symptoms."
                ),
                "rationale": (
                    "Visual screening detected no foliar disease symptoms on the "
                    "analyzed sample. Regular monitoring maintains early detection."
                ),
                "evidence": f"Pathology screening: {disease_clean}",
                "data_source": "Harimitra Disease AI",
            })
        elif _is_finite_number(disease_confidence):
            confidence_val = float(disease_confidence)
            if confidence_val >= 0.50:
                display_name = disease_clean.replace("___", " ").replace("_", " ")
                conf_str = f"{confidence_val * 100:.1f}%" if confidence_val <= 1.0 else f"{confidence_val:.1f}%"
                actions.append({
                    "id": "ACTION_PATHOLOGY_FIELD_VERIFICATION",
                    "priority": 1,
                    "timeframe": "NEXT_FIELD_VISIT",
                    "category": "PATHOLOGY_VERIFICATION",
                    "title": f"Physically Verify Suspected {display_name}",
                    "action": (
                        f"Model screening identified suspected {display_name} "
                        f"(confidence: {conf_str}). Conduct a physical walk through the "
                        "plot to inspect multiple plants and verify whether visible "
                        "foliar symptoms match this condition. Check leaf undersides. "
                        "Consult your local Krishi Vigyan Kendra (KVK) or agricultural "
                        "extension specialist for positive identification before taking "
                        "chemical or cultural measures."
                    ),
                    "rationale": (
                        "Single-leaf computer vision is an indicative screening aid, "
                        "not a certified field diagnosis. Field verification across multiple "
                        "plants prevents unnecessary chemical intervention or misdiagnosis."
                    ),
                    "evidence": f"Screening detection: {disease_clean} ({conf_str} confidence)",
                    "data_source": "Harimitra Disease AI",
                })

    # -------------------------------------------------------------------------
    # Rule 2: Rainfast Label Precaution (Application Alert Heuristic)
    # -------------------------------------------------------------------------
    # Note: rain_probability >= 60 is an application-defined alert threshold,
    # NOT an agronomic standard. Requires a finite percentage between 0 and 100.
    # The action does not infer rain timing or prescribe a spray delay.
    if weather.get("status") == "available":
        rain_prob = weather.get("rain_probability")
        if _is_finite_number(rain_prob):
            rain_prob_val = float(rain_prob)
            if 0.0 <= rain_prob_val <= 100.0 and rain_prob_val >= 60.0:
                actions.append({
                    "id": "ACTION_WEATHER_RAINFAST_CHECK",
                    "priority": 1,
                    "timeframe": "BEFORE_APPLICATION",
                    "category": "WEATHER_PRECAUTION",
                    "title": "Check Product Label Rainfast Period",
                    "action": (
                        f"Forecast indicates an elevated precipitation probability of "
                        f"{rain_prob_val:.0f}%. If planning any foliar or crop-protection "
                        "applications, consult the chemical manufacturer's container "
                        "label for the certified rainfast duration and monitor local "
                        "weather conditions before spraying."
                    ),
                    "rationale": (
                        f"Forecast indicates an elevated precipitation probability ({rain_prob_val:.0f}%). "
                        "Rainfall occurring before a foliar product has reached its certified "
                        "rainfast period can wash off active ingredients, leading to wasted expenditure."
                    ),
                    "evidence": f"Forecasted precipitation probability: {rain_prob_val:.0f}%",
                    "data_source": "Open-Meteo",
                })

    # -------------------------------------------------------------------------
    # Rule 3: Soil Moisture Recorded Value (No Universal Thresholds)
    # -------------------------------------------------------------------------
    # Moisture comes from user-provided form input, not verified sensor telemetry.
    # No universal thresholds (<40%, >70%) or fixed depths (10-15 cm) are assumed.
    if _is_finite_number(soil_moisture):
        moist_val = float(soil_moisture)
        actions.append({
            "id": "ACTION_SOIL_MOISTURE_IN_SITU_CHECK",
            "priority": 2,
            "timeframe": "NEXT_FIELD_VISIT",
            "category": "WATER_OBSERVATION",
            "title": "Perform In-Situ Root-Zone Moisture Check",
            "action": (
                f"A soil moisture value of {moist_val:.1f}% was recorded. "
                "Because moisture requirements vary significantly based on crop growth "
                "stage, soil texture, and weather, perform an in-situ physical soil "
                "moisture check in the root zone before making any adjustments to your "
                "irrigation schedule."
            ),
            "rationale": (
                "User-provided surface values alone cannot determine water requirement. "
                "In-field root-zone verification prevents over-irrigation and moisture deficit stress."
            ),
            "evidence": f"Recorded soil moisture: {moist_val:.1f}%",
            "data_source": "User-Provided Soil Moisture",
        })

    # -------------------------------------------------------------------------
    # Rule 4: Ambient Humidity Precaution (No Proof of Fungal Infection)
    # -------------------------------------------------------------------------
    # 2m weather station data differs from canopy microclimate; this warrants
    # routine visual scouting without asserting active fungal germination.
    if weather.get("status") == "available":
        humidity = weather.get("humidity")
        temperature = weather.get("temperature")
        if _is_finite_number(humidity) and _is_finite_number(temperature):
            hum_val = float(humidity)
            temp_val = float(temperature)
            if hum_val >= 80.0 and temp_val >= 20.0:
                actions.append({
                    "id": "ACTION_WEATHER_HUMIDITY_SCOUTING",
                    "priority": 2,
                    "timeframe": "NEXT_FIELD_VISIT",
                    "category": "WEATHER_PRECAUTION",
                    "title": "Precautionary Scouting for Dense Foliage",
                    "action": (
                        f"High ambient relative humidity ({hum_val:.0f}%) recorded at 2 meters. "
                        "While canopy microclimate differs from weather station data, humid "
                        "weather warrants routine visual inspection of dense lower foliage "
                        "during regular field rounds."
                    ),
                    "rationale": (
                        "Sustained ambient humidity can contribute to prolonged leaf wetness "
                        "in dense stands. Routine scouting enables early detection without "
                        "assuming disease presence."
                    ),
                    "evidence": f"Ambient humidity: {hum_val:.0f}%, temperature: {temp_val:.1f}°C",
                    "data_source": "Open-Meteo",
                })

    # -------------------------------------------------------------------------
    # Rule 5: Soil Health Card Benchmark Guidance (Zero Dosage Invention)
    # -------------------------------------------------------------------------
    # If a reliable district is known, cite it; otherwise use clearly non-district-specific
    # official SHC wording without inventing a district claim.
    if soil_profile and isinstance(soil_profile, dict):
        deficient_nutrients: List[str] = []
        for param_key, param_data in soil_profile.items():
            if isinstance(param_data, dict):
                level = str(param_data.get("level") or "").strip().lower()
                if level in ("low", "deficient"):
                    deficient_nutrients.append((param_key.replace("_", " ").title(), level.title()))

        if deficient_nutrients:
            nutrient_name, nutrient_level = deficient_nutrients[0]
            district_context = f"for {district_name} " if district_name else ""
            actions.append({
                "id": "ACTION_SOIL_SHC_BENCHMARK_REVIEW",
                "priority": 3,
                "timeframe": "THIS_SEASON",
                "category": "SOIL_BENCHMARK",
                "title": f"Review Soil Health Card Benchmark for {nutrient_name}",
                "action": (
                    f"Soil Health Card benchmark data {district_context}indicates {nutrient_name} "
                    f"is in the '{nutrient_level}' category. Refer to your farm's official "
                    "Soil Health Card dosage schedule or consult an agricultural extension "
                    "officer for crop-specific nutrient recommendations (do not apply unverified "
                    "chemical quantities)."
                ),
                "rationale": (
                    "Soil Health Card records highlight regional nutrient limitations. "
                    "Official Soil Health Card guidelines ensure balanced fertilization."
                ),
                "evidence": f"SHC benchmark rating: {nutrient_name} is {nutrient_level}",
                "data_source": "National Soil Health Card Portal",
            })

    # -------------------------------------------------------------------------
    # Rule 6: Satellite Regional Vegetation Context (Explicit Metadata Framing)
    # -------------------------------------------------------------------------
    # Sentinel-2 reduceRegion runs on a 500m buffer (~78.5 ha). It reflects broader
    # regional vegetation trends and is NOT a real-time individual plant leaf diagnosis.
    # Missing observation_date or cloud_percentage is reported explicitly as unavailable.
    if satellite and isinstance(satellite, dict) and satellite.get("available") is True:
        ndvi_mean = satellite.get("ndvi_mean")
        obs_date = satellite.get("observation_date")
        cloud_pct = satellite.get("cloud_percentage")

        if _is_finite_number(ndvi_mean):
            ndvi_val = float(ndvi_mean)
            date_str = str(obs_date) if obs_date and str(obs_date).strip() else "observation date unavailable"
            cloud_str = f"{float(cloud_pct):.1f}%" if _is_finite_number(cloud_pct) else "cloud percentage unavailable"

            actions.append({
                "id": "ACTION_SATELLITE_REGIONAL_CONTEXT",
                "priority": 3,
                "timeframe": "NEXT_FIELD_VISIT",
                "category": "SATELLITE_CONTEXT",
                "title": "Review Regional Vegetation Context (Sentinel-2)",
                "action": (
                    f"Sentinel-2 satellite observation ({date_str}, cloud cover: {cloud_str}) "
                    f"recorded a mean NDVI of {ndvi_val:.2f} across the 500m surrounding area. "
                    "Note that satellite NDVI reflects broad area canopy density and is not a "
                    "real-time leaf diagnosis; verify field vigor during ground rounds."
                ),
                "rationale": (
                    "Remote sensing over a 500m radius (~78 hectares) captures broader landscape "
                    "greenness rather than single-plot foliar condition. Ground observation remains essential."
                ),
                "evidence": f"Sentinel-2 mean NDVI: {ndvi_val:.2f} (observed: {date_str}, cloud: {cloud_str})",
                "data_source": "Sentinel-2 / Google Earth Engine",
            })

    # -------------------------------------------------------------------------
    # Priority Sorting
    # -------------------------------------------------------------------------
    actions.sort(key=lambda a: a.get("priority", 99))

    return actions
