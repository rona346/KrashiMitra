import time
from google import genai
from google.genai import types
import os
import requests

client = genai.Client(
    http_options={
        "timeout": 10000,
        "retry_options": {"attempts": 1},
    }
)


def generate_openrouter_advisory(prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")

    openrouter_start = time.perf_counter()

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openrouter/free",
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        },
        timeout=20,
    )

    print(f"[PERF] OpenRouter: {time.perf_counter() - openrouter_start:.2f}s")

    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    print(f"[DEBUG] OpenRouter advisory: {content[:500]}")
    return content


def generate_advisory(farm_context: dict) -> str:
    prompt = f"""
You are KrashiMitra AI, an agricultural intelligence assistant for Indian farmers.

Use the structured farm context below to provide a practical, concise advisory.

Farm context:
{farm_context}

Your response must:
1. Identify the main agricultural risk.
2. Explain the important factors behind that risk.
3. Give practical actions the farmer can take.
4. Clearly mention if more information is needed.
5. Use simple English for this initial backend test.
6. Do not invent measurements, disease names, medicines, or facts.
7. Do not claim certainty when the available data is uncertain.

Return only the farmer advisory.
"""

    try:
        gemini_start = time.perf_counter()

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
        )
        print(f"[PERF] Gemini: {time.perf_counter() - gemini_start:.2f}s")

        return interaction.output_text

    except Exception as gemini_error:
        print(f"Gemini advisory failed: {gemini_error}")
        fallback_start = time.perf_counter()
        fallback_response = generate_openrouter_advisory(prompt)
        print(f"[PERF] Fallback total: {time.perf_counter() - fallback_start:.2f}s")
        return fallback_response


def generate_chat_reply(message: str) -> str:
    prompt = f"""
You are KrashiMitra AI, a helpful agriculture assistant for Indian farmers.

Answer the farmer naturally and directly in simple Hindi or easy Hinglish.
Be friendly, practical, and concise.
Do not invent facts, disease names, medicines, or treatments.

Farmer's question:
{message}

Return only the answer.
"""

    try:
        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
        )

        return interaction.output_text

    except Exception as gemini_error:
        print(f"Gemini chat failed: {gemini_error}")
        return generate_openrouter_advisory(prompt)
