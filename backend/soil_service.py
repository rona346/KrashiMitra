SOIL_HEALTH_PARAMETERS = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "sulfur",
    "zinc",
    "iron",
    "copper",
    "manganese",
    "boron",
    "ph",
    "electrical_conductivity",
    "organic_carbon",
]


def build_soil_profile(data: dict) -> dict:
    return {parameter: data.get(parameter) for parameter in SOIL_HEALTH_PARAMETERS}
