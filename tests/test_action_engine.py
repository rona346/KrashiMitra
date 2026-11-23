import math
import os
import sys
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.action_engine import generate_farm_actions, _is_finite_number


class TestFarmActionEngine(unittest.TestCase):
    """
    Unit test suite for backend/action_engine.py verifying:
    - Grounded, non-hallucinatory action generation
    - Safe empty-list fallback on missing/unverified telemetry
    - Cautious wording (no dosage, no arbitrary spray bans, no uncalibrated irrigation commands)
    - Rejection of booleans, NaN, and infinity across all numeric inputs
    - Complete isolation of synthetic mock AgriStack data
    """

    # -------------------------------------------------------------------------
    # 1. Empty context returns []
    # -------------------------------------------------------------------------
    def test_empty_context_returns_empty_list(self):
        self.assertEqual(generate_farm_actions({}), [])
        self.assertEqual(generate_farm_actions(None), [])

    # -------------------------------------------------------------------------
    # 2. Missing/unavailable telemetry returns []
    # -------------------------------------------------------------------------
    def test_missing_unavailable_telemetry_returns_empty_list(self):
        context = {
            "disease": None,
            "disease_confidence": None,
            "soil_moisture": None,
            "weather": {"status": "unavailable"},
            "satellite": {"available": False},
            "soil_profile": None,
            "location": {},
        }
        self.assertEqual(generate_farm_actions(context), [])

    # -------------------------------------------------------------------------
    # 3. Healthy disease screening generates routine observation only
    # -------------------------------------------------------------------------
    def test_healthy_disease_screening_generates_routine_observation_only(self):
        context = {
            "disease": "Tomato___healthy",
            "disease_confidence": 0.95,
        }
        actions = generate_farm_actions(context)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action["id"], "ACTION_FOLIAR_HEALTHY_OBSERVATION")
        self.assertEqual(action["category"], "PATHOLOGY_VERIFICATION")
        self.assertIn("healthy", action["action"].lower())
        # Must not instruct destructive or chemical intervention
        self.assertNotIn("quarantine", action["action"].lower())
        self.assertNotIn("remove", action["action"].lower())
        self.assertNotIn("spray", action["action"].lower())

    # -------------------------------------------------------------------------
    # 4. Suspected disease generates field verification and KVK guidance
    # -------------------------------------------------------------------------
    def test_suspected_disease_generates_field_verification_and_kvk(self):
        context = {
            "disease": "Tomato___Early_blight",
            "disease_confidence": 0.92,
        }
        actions = generate_farm_actions(context)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action["id"], "ACTION_PATHOLOGY_FIELD_VERIFICATION")
        self.assertEqual(action["category"], "PATHOLOGY_VERIFICATION")
        self.assertIn("Early blight", action["title"])
        self.assertIn("inspect", action["action"].lower())
        self.assertIn("kvk", action["action"].lower())
        self.assertIn("consult", action["action"].lower())
        # Must not order chemical application or defoliation
        self.assertNotIn("apply fungicide", action["action"].lower())
        self.assertNotIn("remove leaves", action["action"].lower())

    # -------------------------------------------------------------------------
    # 5. Rain probability below 60 does not trigger
    # -------------------------------------------------------------------------
    def test_rain_probability_below_60_does_not_trigger(self):
        context = {
            "weather": {
                "status": "available",
                "rain_probability": 59.9,
            }
        }
        self.assertEqual(generate_farm_actions(context), [])

    # -------------------------------------------------------------------------
    # 6. Rain probability >= 60 triggers label precaution
    # -------------------------------------------------------------------------
    def test_rain_probability_gte_60_triggers_label_precaution(self):
        context = {
            "weather": {
                "status": "available",
                "rain_probability": 60.0,
            }
        }
        actions = generate_farm_actions(context)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action["id"], "ACTION_WEATHER_RAINFAST_CHECK")
        self.assertEqual(action["category"], "WEATHER_PRECAUTION")
        self.assertIn("rainfast", action["action"].lower())
        self.assertIn("label", action["action"].lower())

    # -------------------------------------------------------------------------
    # 7. Rain probability outside 0-100 does not trigger
    # -------------------------------------------------------------------------
    def test_rain_probability_outside_0_to_100_does_not_trigger(self):
        context_high = {"weather": {"status": "available", "rain_probability": 105.0}}
        context_neg = {"weather": {"status": "available", "rain_probability": -10.0}}
        self.assertEqual(generate_farm_actions(context_high), [])
        self.assertEqual(generate_farm_actions(context_neg), [])

    # -------------------------------------------------------------------------
    # 8. Rain action does not contain a generic spray delay
    # -------------------------------------------------------------------------
    def test_rain_action_does_not_contain_generic_spray_delay(self):
        context = {
            "weather": {
                "status": "available",
                "rain_probability": 75.0,
            }
        }
        actions = generate_farm_actions(context)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        # Must not claim generic intervals or prescribe blanket delays
        self.assertNotIn("2 to 6 hours", action["action"])
        self.assertNotIn("typically", action["action"].lower())
        self.assertNotIn("delay spraying by", action["action"].lower())
        self.assertNotIn("do not spray today", action["action"].lower())

    # -------------------------------------------------------------------------
    # 9. Soil moisture generates cautious observation and uses User-Provided source
    # -------------------------------------------------------------------------
    def test_soil_moisture_cautious_observation_and_user_provided_source(self):
        context = {"soil_moisture": 55.4}
        actions = generate_farm_actions(context)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action["id"], "ACTION_SOIL_MOISTURE_IN_SITU_CHECK")
        self.assertEqual(action["category"], "WATER_OBSERVATION")
        self.assertEqual(action["data_source"], "User-Provided Soil Moisture")
        self.assertIn("soil moisture value of 55.4%", action["action"])
        self.assertNotIn("volumetric soil moisture reading", action["action"].lower())
        self.assertIn("root zone", action["action"].lower())
        # Must not claim universal thresholds, fixed depths, or irrigation commands
        self.assertNotIn("10–15 cm", action["action"])
        self.assertNotIn("10-15 cm", action["action"])
        self.assertNotIn("irrigation required", action["action"].lower())

    # -------------------------------------------------------------------------
    # 10. Soil moisture rejects bool, NaN, and infinity
    # -------------------------------------------------------------------------
    def test_soil_moisture_rejects_bool_nan_and_infinity(self):
        self.assertEqual(generate_farm_actions({"soil_moisture": True}), [])
        self.assertEqual(generate_farm_actions({"soil_moisture": False}), [])
        self.assertEqual(generate_farm_actions({"soil_moisture": float("nan")}), [])
        self.assertEqual(generate_farm_actions({"soil_moisture": float("inf")}), [])
        self.assertEqual(generate_farm_actions({"soil_moisture": float("-inf")}), [])

    # -------------------------------------------------------------------------
    # 11. Humidity precaution triggers only when rule conditions are met
    # -------------------------------------------------------------------------
    def test_humidity_precaution_conditions(self):
        # Meets conditions: humidity >= 80 and temp >= 20
        context_ok = {
            "weather": {
                "status": "available",
                "humidity": 85.0,
                "temperature": 25.0,
            }
        }
        actions = generate_farm_actions(context_ok)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action["id"], "ACTION_WEATHER_HUMIDITY_SCOUTING")
        self.assertIn("dense lower foliage", action["action"])
        self.assertNotIn("fungus is spreading", action["action"].lower())

        # Low humidity (< 80) -> does not trigger
        context_low_hum = {
            "weather": {
                "status": "available",
                "humidity": 79.0,
                "temperature": 25.0,
            }
        }
        self.assertEqual(generate_farm_actions(context_low_hum), [])

        # Low temp (< 20) -> does not trigger
        context_low_temp = {
            "weather": {
                "status": "available",
                "humidity": 85.0,
                "temperature": 19.0,
            }
        }
        self.assertEqual(generate_farm_actions(context_low_temp), [])

        # Unavailable weather status -> does not trigger
        context_unavail = {
            "weather": {
                "status": "unavailable",
                "humidity": 85.0,
                "temperature": 25.0,
            }
        }
        self.assertEqual(generate_farm_actions(context_unavail), [])

    # -------------------------------------------------------------------------
    # 12. SHC benchmark action does not invent dosage
    # -------------------------------------------------------------------------
    def test_shc_benchmark_action_does_not_invent_dosage(self):
        context = {
            "soil_profile": {
                "nitrogen": {"level": "Low", "value": "0"},
            },
            "location": {"district": "Udaipur"},
        }
        actions = generate_farm_actions(context)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action["id"], "ACTION_SOIL_SHC_BENCHMARK_REVIEW")
        self.assertEqual(action["category"], "SOIL_BENCHMARK")
        self.assertIn("Nitrogen", action["title"])
        self.assertIn("Udaipur", action["action"])
        # Must not invent chemical quantities or kg/ha
        self.assertNotIn("kg", action["action"].lower())
        self.assertNotIn("urea", action["action"].lower())
        self.assertIn("do not apply unverified chemical quantities", action["action"].lower())

    # -------------------------------------------------------------------------
    # 13. Missing district does not claim a district-specific benchmark
    # -------------------------------------------------------------------------
    def test_missing_district_does_not_claim_district_specific_benchmark(self):
        # When location has no district
        context_no_dist = {
            "soil_profile": {
                "nitrogen": {"level": "Low", "value": "0"},
            },
            "location": {},
        }
        actions_no_dist = generate_farm_actions(context_no_dist)
        self.assertEqual(len(actions_no_dist), 1)
        action_no_dist = actions_no_dist[0]
        self.assertIn("Soil Health Card benchmark data indicates", action_no_dist["action"])
        self.assertNotIn("for your district", action_no_dist["action"].lower())
        self.assertNotIn("for unknown", action_no_dist["action"].lower())
        self.assertNotIn("for none", action_no_dist["action"].lower())

        # When reliable district is present
        context_with_dist = {
            "soil_profile": {
                "nitrogen": {"level": "Low", "value": "0"},
            },
            "location": {"district": "Udaipur"},
        }
        actions_with_dist = generate_farm_actions(context_with_dist)
        self.assertIn("Soil Health Card benchmark data for Udaipur indicates", actions_with_dist[0]["action"])

    # -------------------------------------------------------------------------
    # 14. Mock AgriStack data alone generates no action
    # -------------------------------------------------------------------------
    def test_mock_agristack_data_alone_generates_no_action(self):
        context = {
            "agristack": {
                "farmer_id": "KM-FARMER-001",
                "name": "Demo Farmer",
                "farm": {
                    "crop": "Tomato",
                    "area_acres": 2.5,
                    "irrigation": "Drip",
                    "soil_type": "Loamy",
                },
            }
        }
        self.assertEqual(generate_farm_actions(context), [])

    # -------------------------------------------------------------------------
    # 15. Satellite action uses exact observation date, cloud %, NDVI, and 500m
    # -------------------------------------------------------------------------
    def test_satellite_action_uses_exact_metadata_and_500m_context(self):
        context = {
            "satellite": {
                "available": True,
                "observation_date": "2026-09-18",
                "cloud_percentage": 8.4,
                "ndvi_mean": 0.44,
            }
        }
        actions = generate_farm_actions(context)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action["id"], "ACTION_SATELLITE_REGIONAL_CONTEXT")
        self.assertEqual(action["category"], "SATELLITE_CONTEXT")
        self.assertIn("2026-09-18", action["action"])
        self.assertIn("8.4%", action["action"])
        self.assertIn("0.44", action["action"])
        self.assertIn("500m", action["action"])
        self.assertIn("not a real-time leaf diagnosis", action["action"].lower())
        self.assertIn("ground", action["action"].lower())

    # -------------------------------------------------------------------------
    # 16. Missing satellite metadata uses explicit unavailable wording
    # -------------------------------------------------------------------------
    def test_missing_satellite_metadata_uses_explicit_unavailable_wording(self):
        context = {
            "satellite": {
                "available": True,
                "observation_date": None,
                "cloud_percentage": None,
                "ndvi_mean": 0.38,
            }
        }
        actions = generate_farm_actions(context)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertIn("observation date unavailable", action["action"])
        self.assertIn("cloud percentage unavailable", action["action"])
        # Misleading placeholders must not be used
        self.assertNotIn("recent pass", action["action"].lower())
        self.assertNotIn("minimal", action["action"].lower())

    # -------------------------------------------------------------------------
    # 17. Unavailable satellite data generates no satellite action
    # -------------------------------------------------------------------------
    def test_unavailable_satellite_data_generates_no_satellite_action(self):
        context = {
            "satellite": {
                "available": False,
                "observation_date": None,
                "cloud_percentage": None,
                "ndvi_mean": None,
            }
        }
        self.assertEqual(generate_farm_actions(context), [])

    # -------------------------------------------------------------------------
    # 18. Numeric telemetry rejects bool, NaN, and infinity across all signals
    # -------------------------------------------------------------------------
    def test_numeric_telemetry_rejects_bool_nan_and_infinity_across_signals(self):
        # Disease confidence
        self.assertEqual(generate_farm_actions({"disease": "Tomato___Early_blight", "disease_confidence": True}), [])
        self.assertEqual(generate_farm_actions({"disease": "Tomato___Early_blight", "disease_confidence": float("nan")}), [])
        self.assertEqual(generate_farm_actions({"disease": "Tomato___Early_blight", "disease_confidence": float("inf")}), [])

        # Rain probability
        self.assertEqual(generate_farm_actions({"weather": {"status": "available", "rain_probability": True}}), [])
        self.assertEqual(generate_farm_actions({"weather": {"status": "available", "rain_probability": float("nan")}}), [])
        self.assertEqual(generate_farm_actions({"weather": {"status": "available", "rain_probability": float("inf")}}), [])

        # Weather humidity and temperature
        self.assertEqual(generate_farm_actions({"weather": {"status": "available", "humidity": True, "temperature": 25.0}}), [])
        self.assertEqual(generate_farm_actions({"weather": {"status": "available", "humidity": 85.0, "temperature": True}}), [])
        self.assertEqual(generate_farm_actions({"weather": {"status": "available", "humidity": float("nan"), "temperature": 25.0}}), [])
        self.assertEqual(generate_farm_actions({"weather": {"status": "available", "humidity": 85.0, "temperature": float("nan")}}), [])
        self.assertEqual(generate_farm_actions({"weather": {"status": "available", "humidity": float("inf"), "temperature": 25.0}}), [])

        # Satellite mean NDVI
        self.assertEqual(generate_farm_actions({"satellite": {"available": True, "ndvi_mean": True}}), [])
        self.assertEqual(generate_farm_actions({"satellite": {"available": True, "ndvi_mean": float("nan")}}), [])
        self.assertEqual(generate_farm_actions({"satellite": {"available": True, "ndvi_mean": float("inf")}}), [])


if __name__ == "__main__":
    unittest.main()
