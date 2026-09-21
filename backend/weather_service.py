import os
import requests


def get_weather(lat: float, lon: float) -> dict:
    """
    Return structured weather data for a farm location.

    IMD integration will plug into this function later.
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "forecast_days": 7,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    daily = data.get("daily", {})
    rain_probability = (
        daily.get("precipitation_probability_max", [None])[0]
    )
    current = data["current"]
    temperature = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    rainfall = current.get("precipitation")

    return {
        "status": "available",
        "source": "Open-Meteo",
        "latitude": lat,
        "longitude": lon,
        "temperature": temperature,
        "humidity": humidity,
        "rainfall": rainfall,
        "rain_probability": rain_probability,
        "forecast": data.get("daily", {}),
        "warnings": [],
    }
