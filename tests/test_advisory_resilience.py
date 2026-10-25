import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import io
import requests

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from backend.main import app
from backend.gemini_service import (
    generate_advisory,
    generate_chat_reply,
    generate_openrouter_advisory,
    get_service_unavailable_advisory,
    AdvisoryResult,
    split_bilingual_advisory,
)


class TestAdvisoryResilience(unittest.TestCase):
    """
    Test suite verifying Lesson 1 Dual-LLM resilience:
    - Gemini success (OpenRouter not called)
    - Gemini failure with successful OpenRouter fallback
    - Both providers fail (controlled graceful fallback without fabricating data)
    - Timeout / malformed provider response
    - Endpoint-level /analyze and /chat compatibility
    """

    def setUp(self):
        self.sample_context = {
            "crop": "Tomato",
            "growth_stage": "Flowering",
            "soil_moisture": 62.0,
            "weather": {
                "status": "available",
                "temperature": 25.0,
                "humidity": 50,
                "rain_probability": 10,
            },
            "disease": "Tomato___Early_blight",
            "disease_confidence": 0.92,
            "risk": {
                "overall_risk": "HIGH",
                "disease_risk": "HIGH",
                "water_risk": "MEDIUM",
                "weather_risk": "LOW",
            },
        }
        self.client = TestClient(app)

    # -------------------------------------------------------------------------
    # 1. Gemini success: OpenRouter is NOT called
    # -------------------------------------------------------------------------
    @patch("backend.gemini_service.requests.post")
    @patch("backend.gemini_service.client")
    def test_gemini_success_openrouter_not_called(self, mock_client, mock_post):
        mock_interaction = MagicMock()
        mock_interaction.output_text = """=== ENGLISH ===
**Main risk:** Early blight in tomato crop.
**Why the risk matters:**
- High disease confidence at 92%.
**What to do now:**
- Inspect leaves and remove infected foliage.
**More information needed:**
- Crop stage details.

=== HINDI ===
**मुख्य जोखिम:** टमाटर में अगेती झुलसा रोग।
**जोखिम क्यों महत्वपूर्ण है:**
- 92% रोग संभावना दर्ज की गई है।
**अभी क्या करें:**
- संक्रमित पत्तियों को हटाएँ।
**अतिरिक्त जानकारी की आवश्यकता:**
- फसल की अवस्था।"""
        mock_client.interactions.create.return_value = mock_interaction

        result_hi = generate_advisory(self.sample_context, language="hinglish")

        # Verify Gemini was called
        mock_client.interactions.create.assert_called_once()
        # Verify OpenRouter was NOT called
        mock_post.assert_not_called()

        self.assertIsInstance(result_hi, AdvisoryResult)
        self.assertIn("अगेती झुलसा", result_hi)
        self.assertIn("Early blight", result_hi.advisory_en)
        self.assertIn("अगेती झुलसा", result_hi.advisory_hi)

        # Test English output selection
        result_en = generate_advisory(self.sample_context, language="english")
        self.assertIn("Early blight", result_en)

    # -------------------------------------------------------------------------
    # 2. Gemini failure followed by successful OpenRouter fallback
    # -------------------------------------------------------------------------
    @patch("backend.gemini_service.requests.post")
    @patch("backend.gemini_service.client")
    def test_gemini_failure_openrouter_fallback_success(self, mock_client, mock_post):
        # Simulate Gemini failure (timeout or quota error)
        mock_client.interactions.create.side_effect = Exception("Gemini client timeout 30s")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": """=== ENGLISH ===
**Main risk:** Target spot detected via OpenRouter fallback.
**Why the risk matters:**
- Foliar damage spread.
**What to do now:**
- Check lower leaf surface.
**More information needed:**
- None.

=== HINDI ===
**मुख्य जोखिम:** ओपनराउटर बैकअप द्वारा टमाटर में टार्गेट स्पॉट।
**जोखिम क्यों महत्वपूर्ण है:**
- पत्तियों का नुकसान।
**अभी क्या करें:**
- पत्तों की निचली सतह देखें।
**अतिरिक्त जानकारी की आवश्यकता:**
- कोई नहीं।"""
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-mock"}):
            result = generate_advisory(self.sample_context, language="hinglish")

        # Verify Gemini was attempted once
        mock_client.interactions.create.assert_called_once()
        # Verify OpenRouter was called as fallback
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        self.assertEqual(call_kwargs["json"]["model"], "nvidia/nemotron-3.5-lightning:free")

        self.assertIsInstance(result, AdvisoryResult)
        self.assertIn("ओपनराउटर बैकअप द्वारा टमाटर में टार्गेट स्पॉट", result)
        self.assertIn("Target spot detected via OpenRouter fallback", result.advisory_en)

    # -------------------------------------------------------------------------
    # 3. Both providers fail: controlled failure without fabricating advisory
    # -------------------------------------------------------------------------
    @patch("backend.gemini_service.requests.post")
    @patch("backend.gemini_service.client")
    def test_both_providers_fail_returns_controlled_advisory(self, mock_client, mock_post):
        # Gemini fails
        mock_client.interactions.create.side_effect = TimeoutError("Gemini read timeout")
        # OpenRouter fails too
        mock_post.side_effect = requests.exceptions.ConnectionError("OpenRouter network error")

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-mock"}):
            result = generate_advisory(self.sample_context, language="hinglish")

        # Verify no unhandled exception was thrown and fallback was returned
        self.assertIsInstance(result, AdvisoryResult)
        self.assertIn("एआई कृषि परामर्श सेवा वर्तमान में अस्थायी रूप से अनुपलब्ध है", result)
        self.assertIn("AI advisory service is temporarily unavailable", result.advisory_en)
        # Verify it references the detected condition without fabricating advice
        self.assertIn("Tomato Early_blight", result.advisory_en)

    # -------------------------------------------------------------------------
    # 4. Timeout or malformed provider response handled
    # -------------------------------------------------------------------------
    @patch("backend.gemini_service.requests.post")
    def test_malformed_openrouter_response_raises_clean_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Malformed: missing "choices" key
        mock_response.json.return_value = {"error": {"message": "Service unavailable"}}
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-mock"}):
            with self.assertRaises(ValueError) as ctx:
                generate_openrouter_advisory("test prompt")
            self.assertIn("Malformed OpenRouter response structure", str(ctx.exception))

    def test_missing_openrouter_api_key_raises_clean_error(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}, clear=False):
            with self.assertRaises(ValueError) as ctx:
                generate_openrouter_advisory("test prompt")
            self.assertIn("OPENROUTER_API_KEY is not configured", str(ctx.exception))

    @patch("backend.gemini_service.requests.post")
    def test_openrouter_custom_model_env_override(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Custom model response"}}]
        }
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            "OPENROUTER_API_KEY": "test-key-mock",
            "OPENROUTER_MODEL": "custom-org/custom-model:free",
        }):
            reply = generate_openrouter_advisory("test prompt")

        self.assertEqual(reply, "Custom model response")
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        self.assertEqual(call_kwargs["json"]["model"], "custom-org/custom-model:free")

    @patch("backend.gemini_service.requests.post")
    @patch("backend.gemini_service.client")
    def test_chat_gemini_failure_openrouter_fallback_success(self, mock_client, mock_post):
        mock_client.interactions.create.side_effect = Exception("Gemini timeout")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "टमाटर में ड्रिप सिंचाई करें।"}}]
        }
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-mock"}):
            reply = generate_chat_reply("सिंचाई सलाह", language="hinglish")

        self.assertEqual(reply, "टमाटर में ड्रिप सिंचाई करें।")
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        self.assertEqual(call_kwargs["json"]["model"], "nvidia/nemotron-3.5-lightning:free")

    @patch("backend.gemini_service.requests.post")
    @patch("backend.gemini_service.client")
    def test_chat_openrouter_404_handled_gracefully(self, mock_client, mock_post):
        mock_client.interactions.create.side_effect = Exception("Gemini intermittent error")
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = '{"error":{"message":"no provider serves this model anymore","code":404}}'
        http_err = requests.exceptions.HTTPError("404 Client Error: Not Found", response=mock_response)
        mock_response.raise_for_status.side_effect = http_err
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-mock"}):
            reply_hi = generate_chat_reply("टमाटर में सिंचाई?", language="hinglish")
            self.assertIn("एआई सेवा वर्तमान में अस्थायी रूप से अनुपलब्ध है", reply_hi)

            reply_en = generate_chat_reply("Tomato irrigation?", language="english")
            self.assertIn("AI service is temporarily unavailable", reply_en)

    # -------------------------------------------------------------------------
    # 5. Endpoint-level: POST /chat behavior under success and double failure
    # -------------------------------------------------------------------------
    @patch("backend.gemini_service.client")
    def test_endpoint_chat_success(self, mock_client):
        mock_interaction = MagicMock()
        mock_interaction.output_text = "टमाटर की फसल में सिंचाई शाम को करें।"
        mock_client.interactions.create.return_value = mock_interaction

        response = self.client.post(
            "/chat",
            json={"message": "टमाटर में सिंचाई कब करें?", "language": "hinglish"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reply"], "टमाटर की फसल में सिंचाई शाम को करें।")

    @patch("backend.gemini_service.requests.post")
    @patch("backend.gemini_service.client")
    def test_endpoint_chat_both_providers_fail_bilingual(self, mock_client, mock_post):
        mock_client.interactions.create.side_effect = Exception("Gemini 500")
        mock_post.side_effect = Exception("OpenRouter 502")

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-mock"}):
            # Hinglish chat request
            resp_hi = self.client.post(
                "/chat",
                json={"message": "कीटनाशक सलाह?", "language": "hinglish"},
            )
            self.assertEqual(resp_hi.status_code, 200)
            self.assertIn("एआई सेवा वर्तमान में अस्थायी रूप से अनुपलब्ध है", resp_hi.json()["reply"])

            # English chat request
            resp_en = self.client.post(
                "/chat",
                json={"message": "Pesticide advice?", "language": "english"},
            )
            self.assertEqual(resp_en.status_code, 200)
            self.assertIn("AI service is temporarily unavailable", resp_en.json()["reply"])

    # -------------------------------------------------------------------------
    # 6. Endpoint-level: POST /analyze behavior when both AI providers fail
    # -------------------------------------------------------------------------
    @patch("backend.main.get_satellite_context")
    @patch("backend.main.get_weather")
    @patch("backend.main.predict_disease")
    @patch("backend.gemini_service.requests.post")
    @patch("backend.gemini_service.client")
    def test_endpoint_analyze_both_providers_fail_does_not_crash(
        self, mock_client, mock_post, mock_predict, mock_weather, mock_satellite
    ):
        # Mock vision model output
        mock_predict.return_value = {
            "class_index": 29,
            "disease": "Tomato___Early_blight",
            "confidence": 0.94,
        }
        # Mock weather
        mock_weather.return_value = {
            "status": "available",
            "temperature": 26.5,
            "humidity": 55,
            "rain_probability": 0,
            "forecast": {},
        }
        # Mock satellite
        mock_satellite.return_value = {
            "available": True,
            "observation_date": "2026-10-20",
            "cloud_percentage": 5.0,
            "ndvi_mean": 0.42,
            "ndvi_median": 0.41,
        }
        # Mock AI providers BOTH failing
        mock_client.interactions.create.side_effect = TimeoutError("Gemini timed out")
        mock_post.side_effect = requests.exceptions.Timeout("OpenRouter timed out")

        # Fake image file upload
        fake_image = io.BytesIO(b"fake-image-bytes-header")

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-mock"}):
            response = self.client.post(
                "/analyze",
                files={"file": ("leaf.jpg", fake_image, "image/jpeg")},
                data={
                    "soil_moisture": "62.0",
                    "latitude": "24.5854",
                    "longitude": "73.7125",
                    "language": "hinglish",
                },
            )

        # The endpoint MUST return HTTP 200 OK and NOT crash with HTTP 500
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Telemetry must be completely intact
        self.assertEqual(data["analysis"], "Tomato___Early_blight")
        self.assertEqual(data["confidence"], 0.94)
        self.assertEqual(data["soil_moisture"], 62.0)
        self.assertEqual(data["irrigation"], "Irrigation Not Required")
        self.assertEqual(data["weather"]["status"], "available")
        self.assertEqual(data["satellite"]["available"], True)
        self.assertEqual(data["risk"]["overall_risk"], "HIGH")
        self.assertGreater(len(data["crop_recommendations"]["recommendations"]), 0)

        # Advisory must contain the controlled unavailable notice, not crash
        self.assertIn("एआई कृषि परामर्श सेवा वर्तमान में अस्थायी रूप से अनुपलब्ध है", data["advisory"])
        self.assertIn("AI advisory service is temporarily unavailable", data["advisory_en"])
        self.assertIn("Tomato Early_blight", data["advisory_en"])


if __name__ == "__main__":
    unittest.main()
