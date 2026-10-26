import os
import sys
import time
import unittest
from unittest.mock import patch, MagicMock
import concurrent.futures

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from backend.main import app
from backend.weather_service import get_weather
from backend.satellite_service import get_satellite_context


class TestConcurrencyAndTimeouts(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_and_preflight_responsive_during_heavy_chat(self):
        """
        Verify that GET / and CORS OPTIONS /chat respond immediately even
        while a chat request is processing a simulated slow LLM response.
        """
        def slow_chat_reply(message, language="hinglish"):
            time.sleep(0.5)
            return "Simulated slow LLM response"

        with patch("backend.main.generate_chat_reply", side_effect=slow_chat_reply):
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # Launch heavy chat request
                future_chat = executor.submit(
                    self.client.post,
                    "/chat",
                    json={"message": "What is the best irrigation schedule?", "language": "english"},
                )

                # Ensure chat has started on a worker thread
                time.sleep(0.05)

                # Ping GET / and OPTIONS /chat concurrently
                t0 = time.perf_counter()
                resp_get = self.client.get("/")
                resp_options = self.client.options(
                    "/chat",
                    headers={
                        "Origin": "http://localhost:5173",
                        "Access-Control-Request-Method": "POST",
                        "Access-Control-Request-Headers": "content-type",
                    },
                )
                ping_latency = time.perf_counter() - t0

                # Wait for chat to finish
                resp_chat = future_chat.result(timeout=2.0)

                # Assertions
                self.assertEqual(resp_get.status_code, 200)
                self.assertEqual(resp_get.json(), {"message": "KrishiMitra AI backend is running"})
                self.assertEqual(resp_options.status_code, 200)
                self.assertEqual(resp_chat.status_code, 200)
                self.assertEqual(resp_chat.json(), {"reply": "Simulated slow LLM response"})
                # Concurrency check: ping finished much faster than the 0.5s slow chat
                self.assertLess(ping_latency, 0.25, f"Ping latency was {ping_latency:.3f}s, expected < 0.25s")

    def test_health_and_preflight_responsive_during_heavy_analyze(self):
        """
        Verify that GET / and CORS OPTIONS /chat respond immediately even
        while /analyze is processing a simulated heavy AI/Earth Engine pipeline.
        """
        def slow_process(*args, **kwargs):
            time.sleep(0.5)
            return {
                "filename": "test.jpg",
                "analysis": "Tomato___healthy",
                "confidence": 0.95,
                "class_index": 37,
                "advisory": "Healthy crop",
            }

        with patch("backend.main._process_analyze_sync", side_effect=slow_process):
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # Launch heavy analyze request
                future_analyze = executor.submit(
                    self.client.post,
                    "/analyze",
                    files={"file": ("test.jpg", b"fake_image_bytes", "image/jpeg")},
                    data={"soil_moisture": 60.0, "latitude": 24.5, "longitude": 73.7, "language": "english"},
                )

                # Ensure analyze has started on a worker thread
                time.sleep(0.05)

                # Ping GET / and OPTIONS /chat concurrently
                t0 = time.perf_counter()
                resp_get = self.client.get("/")
                resp_options = self.client.options(
                    "/chat",
                    headers={
                        "Origin": "http://localhost:5173",
                        "Access-Control-Request-Method": "POST",
                        "Access-Control-Request-Headers": "content-type",
                    },
                )
                ping_latency = time.perf_counter() - t0

                # Wait for analyze to finish
                resp_analyze = future_analyze.result(timeout=2.0)

                # Assertions
                self.assertEqual(resp_get.status_code, 200)
                self.assertEqual(resp_options.status_code, 200)
                self.assertEqual(resp_analyze.status_code, 200)
                self.assertEqual(resp_analyze.json()["analysis"], "Tomato___healthy")
                # Concurrency check
                self.assertLess(ping_latency, 0.25, f"Ping latency was {ping_latency:.3f}s, expected < 0.25s")

    @patch("backend.satellite_service.SATELLITE_TIMEOUT_SECONDS", 0.2)
    @patch("backend.satellite_service._fetch_satellite_context_sync")
    def test_satellite_service_bounded_timeout(self, mock_fetch):
        """
        Verify that if Google Earth Engine hangs or exceeds SATELLITE_TIMEOUT_SECONDS,
        get_satellite_context aborts within the timeout and returns available: False.
        """
        def mock_hanging_satellite(lat, lon):
            time.sleep(1.0)
            return {"available": True}

        mock_fetch.side_effect = mock_hanging_satellite

        t0 = time.perf_counter()
        result = get_satellite_context(24.5854, 73.7125)
        elapsed = time.perf_counter() - t0

        self.assertFalse(result["available"])
        self.assertIn("timed out", result["limitations"][0])
        self.assertLess(elapsed, 0.8, f"Call took {elapsed:.2f}s, expected timeout around 0.2s")

    @patch("backend.weather_service.requests.get")
    def test_weather_service_timeout_handling(self, mock_requests_get):
        """
        Verify that if Open-Meteo times out or fails, get_weather returns a clean
        degraded status without raising an unhandled exception.
        """
        import requests
        mock_requests_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        result = get_weather(24.5854, 73.7125)
        self.assertEqual(result["status"], "unavailable")
        self.assertIsNone(result["temperature"])
        self.assertIn("Weather service temporarily unavailable", result["warnings"][0])


if __name__ == "__main__":
    unittest.main()
