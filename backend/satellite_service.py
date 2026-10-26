import concurrent.futures
import os
import time
import ee
from datetime import date

EE_PROJECT = "krashimitra-ai-2026"
SATELLITE_TIMEOUT_SECONDS = float(os.getenv("SATELLITE_TIMEOUT_SECONDS", "12.0"))
_satellite_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def initialize_earth_engine():
    try:
        ee.Initialize(project=EE_PROJECT)
        print("[INFO] Earth Engine initialized successfully.")
    except Exception as exc:
        print(f"[WARNING] Earth Engine initialization failed: {exc}. Satellite features will degrade gracefully.")


def get_sentinel_collection(latitude, longitude):
    end_date = ee.Date(date.today().isoformat())
    start_date = end_date.advance(-90, "day")
    point = ee.Geometry.Point([longitude, latitude])

    return (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterDate(start_date, end_date)
        .filterBounds(point)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
    )


def get_recent_sentinel_image(latitude, longitude):
    point = ee.Geometry.Point([longitude, latitude])
    region = point.buffer(100)

    collection = (
        get_sentinel_collection(latitude, longitude)
        .filterBounds(region)
        .sort("system:time_start", False)
    )

    if collection.size().getInfo() == 0:
        return None

    return collection.first()


def get_recent_ndvi(latitude, longitude):
    image = get_recent_sentinel_image(latitude, longitude)
    return calculate_ndvi(image)


def _fetch_satellite_context_sync(latitude, longitude):
    satellite_start = time.perf_counter()
    image = get_recent_sentinel_image(latitude, longitude)

    if image is None:
        return {
            "available": False,
            "observation_date": None,
            "cloud_percentage": None,
            "ndvi_mean": None,
            "ndvi_median": None,
            "ndvi_min": None,
            "ndvi_max": None,
            "source": "Sentinel-2 / Google Earth Engine",
            "limitations": [
                "No usable Sentinel-2 scene was available for this location and time window."
            ],
        }

    metadata = get_scene_metadata(image)

    ndvi_image = calculate_ndvi(image)

    ndvi_stats = get_ndvi_statistics(
        ndvi_image,
        latitude,
        longitude,
    )

    print(
        f"[PERF] Satellite internal total: {time.perf_counter() - satellite_start:.2f}s"
    )

    return {
        "available": True,
        "observation_date": metadata["observation_date"],
        "cloud_percentage": metadata["cloud_percentage"],
        "ndvi_mean": ndvi_stats.get("NDVI_mean"),
        "ndvi_median": ndvi_stats.get("NDVI_median"),
        "ndvi_min": ndvi_stats.get("NDVI_min"),
        "ndvi_max": ndvi_stats.get("NDVI_max"),
        "source": "Sentinel-2 / Google Earth Engine",
        "limitations": [
            "NDVI indicates broader vegetation condition and is not a disease diagnosis.",
            "Satellite observation date may differ from the current date because of cloud cover and scene availability.",
        ],
    }


def get_satellite_context(latitude, longitude):
    future = _satellite_executor.submit(_fetch_satellite_context_sync, latitude, longitude)
    try:
        return future.result(timeout=SATELLITE_TIMEOUT_SECONDS)
    except concurrent.futures.TimeoutError:
        print(
            f"[WARNING] Satellite data query timed out after {SATELLITE_TIMEOUT_SECONDS}s"
        )
        return {
            "available": False,
            "observation_date": None,
            "cloud_percentage": None,
            "ndvi_mean": None,
            "ndvi_median": None,
            "ndvi_min": None,
            "ndvi_max": None,
            "source": "Sentinel-2 / Google Earth Engine",
            "limitations": [
                f"Satellite data query timed out after {SATELLITE_TIMEOUT_SECONDS:.1f}s."
            ],
        }
    except Exception as error:
        print(f"[WARNING] Satellite data retrieval failed: {error}")
        return {
            "available": False,
            "observation_date": None,
            "cloud_percentage": None,
            "ndvi_mean": None,
            "ndvi_median": None,
            "ndvi_min": None,
            "ndvi_max": None,
            "source": "Sentinel-2 / Google Earth Engine",
            "limitations": [f"Satellite data unavailable: {str(error)}"],
        }


def get_scene_metadata(image):
    date = ee.Date(image.get("system:time_start")).format("YYYY-MM-dd").getInfo()
    cloud = image.get("CLOUDY_PIXEL_PERCENTAGE").getInfo()

    return {
        "observation_date": date,
        "cloud_percentage": cloud,
    }


def calculate_ndvi(image):
    return image.normalizedDifference(["B8", "B4"]).rename("NDVI")


def get_ndvi_statistics(ndvi_image, latitude, longitude):
    region = ee.Geometry.Point([longitude, latitude]).buffer(500)

    stats = ndvi_image.reduceRegion(
        reducer=(
            ee.Reducer.mean()
            .combine(ee.Reducer.median(), sharedInputs=True)
            .combine(ee.Reducer.minMax(), sharedInputs=True)
        ),
        geometry=region,
        scale=10,
        maxPixels=1_000_000,
    )

    return stats.getInfo()


def check_recent_scenes(latitude, longitude):
    point = ee.Geometry.Point([longitude, latitude])

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterDate("2026-08-20", "2026-09-20")
        .filterBounds(point.buffer(100))
        .sort("system:time_start", False)
    )

    scenes = collection.limit(10).getInfo()

    for scene in scenes["features"]:
        properties = scene["properties"]
        scene_date = (
            ee.Date(properties["system:time_start"]).format("YYYY-MM-dd").getInfo()
        )
        print(
            properties.get("system:index"),
            scene_date,
            properties.get("CLOUDY_PIXEL_PERCENTAGE"),
        )
