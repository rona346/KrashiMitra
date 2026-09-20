from google import genai
import os
import requests

from google import genai

client = genai.Client()


def generate_openrouter_advisory(prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")

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
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]


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
        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
        )
        return interaction.output_text

    except Exception as gemini_error:
        print(f"Gemini advisory failed: {gemini_error}")
        return generate_openrouter_advisory(prompt)

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

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
    )

    return interaction.output_text
