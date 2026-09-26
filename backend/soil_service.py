import json
import csv
from pathlib import Path

PROJECT_DATASET_PATH = Path(__file__).parent / "data" / "soil_nutrient_analysis.csv"
FULL_DATASET_PATH = (
    Path.home()
    / "Downloads"
    / "Soil_Nutrient_Analysis_download"
    / "soil-nutrient-analysis.csv"
)


def get_soil_nutrients(
    state: str,
    district: str,
    block: str | None = None,
    village: str | None = None,
) -> dict:
    csv_path = FULL_DATASET_PATH if FULL_DATASET_PATH.exists() else PROJECT_DATASET_PATH
    cache_path = (
        Path(__file__).parent / "data" / "soil_cache" / "rajasthan_udaipur.json"
    )

    if (
        state.strip().lower() == "rajasthan"
        and district.strip().lower() == "udaipur"
        and cache_path.exists()
    ):
        with open(cache_path, "r", encoding="utf-8") as file:
            return json.load(file)

    nutrients = {}

    with open(csv_path, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            state_value = row.get("state_name") or row.get("State Name (state_name)")
            district_value = row.get("district_name") or row.get(
                "District Name (district_name)"
            )
            block_value = row.get("block_name") or row.get("Block Name (block_name)")
            village_value = row.get("village_name") or row.get(
                "Village Name (village_name)"
            )

            if not state_value or state_value.strip().lower() != state.strip().lower():
                continue

            if (
                not district_value
                or district_value.strip().lower() != district.strip().lower()
            ):
                continue

            if block and (
                not block_value or block_value.strip().lower() != block.strip().lower()
            ):
                continue

            if village and (
                not village_value
                or village_value.strip().lower() != village.strip().lower()
            ):
                continue

            nutrient_name = (
                row.get("nutrient_name")
                or row.get("Nutrient Name (nutrient_name)")
                or ""
            ).strip()

            nutrient_level = (
                row.get("nutrient_level")
                or row.get("Nutrient Level (nutrient_level)")
                or ""
            ).strip()

            value = (row.get("value") or row.get("Value (value)") or "").strip()

            if nutrient_name:
                nutrients[nutrient_name] = {
                    "level": nutrient_level,
                    "value": value,
                }

    return nutrients


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


def build_soil_profile(data: dict | None = None) -> dict:
    data = data or {}

    nutrient_mapping = {
        "nitrogen": "Nitrogen",
        "phosphorus": "Phosphorus",
        "potassium": "Potassium",
        "sulfur": "Sulphur",
        "zinc": "Zinc",
        "iron": "Iron",
        "copper": "Copper",
        "manganese": "Manganese",
        "boron": "Boron",
        "ph": "Soil Ph",
        "electrical_conductivity": "Electrical Conductivity",
        "organic_carbon": "Organic Carbon",
    }

    return {
        parameter: data.get(source_name)
        for parameter, source_name in nutrient_mapping.items()
    }
