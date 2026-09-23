import csv
import json
from pathlib import Path

FULL_DATASET_PATH = (
    Path.home()
    / "Downloads"
    / "Soil_Nutrient_Analysis_download"
    / "soil-nutrient-analysis.csv"
)

CACHE_PATH = Path(__file__).parent / "data" / "soil_cache" / "rajasthan_udaipur.json"


TARGET_STATE = "Rajasthan"
TARGET_DISTRICT = "Udaipur"


def preprocess():
    nutrients = {}

    print("Reading SHC dataset...")
    print(f"Source: {FULL_DATASET_PATH}")

    with open(
        FULL_DATASET_PATH,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["state_name"].strip().lower() != TARGET_STATE.lower():
                continue

            if row["district_name"].strip().lower() != TARGET_DISTRICT.lower():
                continue

            nutrient_name = row["nutrient_name"].strip()

            nutrients[nutrient_name] = {
                "level": row["nutrient_level"].strip(),
                "value": row["value"].strip(),
            }

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CACHE_PATH, "w", encoding="utf-8") as file:
        json.dump(nutrients, file, indent=2)

    print(f"Cached nutrients: {len(nutrients)}")
    print(f"Cache saved to: {CACHE_PATH}")


if __name__ == "__main__":
    preprocess()
