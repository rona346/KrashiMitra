import time
from google import genai
from google.genai import types
import os
import requests

print("GEMINI_API_KEY loaded:", bool(os.environ.get("GEMINI_API_KEY")))

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options={
        "timeout": 10000,
        "retry_options": {"attempts": 1},
    },
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
            "model": "nex-agi/nex-n2.5-mini:free",
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
    print(f"[DEBUG] OpenRouter status: {response.status_code}")
    print(f"[DEBUG] OpenRouter body: {response.text[:1000]}")

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


def generate_chat_reply(message: str, language: str = "hinglish") -> str:
    if language == "english":
        language_instruction = "Answer only in simple English."
    else:
        language_instruction = "Answer only in simple Hindi using Devanagari script."

    prompt = f"""
You are KrashiMitra AI, a helpful agriculture assistant for Indian farmers.

{language_instruction}

STRICT LANGUAGE RULES:
- Use only Hindi and English/Hinglish.
- Do NOT use Japanese, Bengali, Gujarati, Punjabi, Tamil, Telugu, or any other language.
- Do NOT use random Unicode words or characters from other languages.
- Do not mix languages unnecessarily.
- Keep the answer natural, simple, and farmer-friendly.
- You may use normal English agriculture terms when commonly used.
- Before returning the answer, check that no words from another language or script are present.
- For Hindi, use Devanagari script. Do not use Hinglish or Roman Hindi.

SAFETY RULES:
- Do not invent facts, disease names, medicines, treatments, or chemical dosages.
- Do not give specific pesticide/fungicide dosage unless it is explicitly provided in reliable context.
- If the exact treatment is uncertain, recommend consulting a local agricultural expert/KVK.
- Be practical and concise.

Farmer's question:
{message}

Return only the final answer.
"""

    try:
        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
        )

        return interaction.output_text

    except Exception as gemini_error:
        print(f"Gemini chat failed: {gemini_error}")

        try:
            return generate_openrouter_advisory(prompt)
        except Exception as openrouter_error:
            print(f"OpenRouter chat failed: {openrouter_error}")
            return (
                "AI service is temporarily unavailable. Please try again in a moment."
            )
