import os
import requests


def get_weather(lat: float, lon: float) -> dict:
    """
    Return structured weather data for a farm location.

    IMD integration will plug into this function later.
    """

    return {
        "status": "unavailable",
        "source": "IMD",
        "latitude": lat,
        "longitude": lon,
        "temperature": None,
        "humidity": None,
        "rainfall": None,
        "rain_probability": None,
        "forecast": [],
        "warnings": [],
    }
