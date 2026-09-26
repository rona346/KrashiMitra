import time
from google import genai
from google.genai import types
import os
import requests

print("GEMINI_API_KEY loaded:", bool(os.environ.get("GEMINI_API_KEY")))

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options={
        "timeout": 30.0,
        "retry_options": {"attempts": 1},
    },
)


class AdvisoryResult(str):
    """String subclass that also carries advisory_en and advisory_hi attributes and dict-like access."""

    def __new__(cls, content, advisory_en=None, advisory_hi=None):
        obj = super().__new__(cls, content)
        obj.advisory_en = advisory_en or content
        obj.advisory_hi = advisory_hi or content
        return obj

    def get(self, key, default=None):
        if key == "advisory":
            return str(self)
        if key == "advisory_en":
            return self.advisory_en
        if key == "advisory_hi":
            return self.advisory_hi
        return default


def split_bilingual_advisory(text: str) -> tuple[str, str]:
    if "=== HINDI ===" in text:
        parts = text.split("=== HINDI ===")
        en = parts[0].replace("=== ENGLISH ===", "").strip()
        hi = parts[1].strip()
        return en, hi
    elif "=== HINDI ADVISORY ===" in text:
        parts = text.split("=== HINDI ADVISORY ===")
        en = parts[0].replace("=== ENGLISH ADVISORY ===", "").strip()
        hi = parts[1].strip()
        return en, hi
    return text.strip(), text.strip()


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
        timeout=30,
    )

    print(f"[PERF] OpenRouter: {time.perf_counter() - openrouter_start:.2f}s")
    print(f"[DEBUG] OpenRouter status: {response.status_code}")
    try:
        print(f"[DEBUG] OpenRouter body: {response.text[:500]}")
    except Exception:
        pass

    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    try:
        print(f"[DEBUG] OpenRouter advisory: {content[:300]}")
    except Exception:
        pass
    return content


def generate_advisory(farm_context: dict, language: str = "hinglish") -> AdvisoryResult:
    raw_disease = farm_context.get("disease", "Identified Condition")
    display_disease = str(raw_disease).replace("___", " ")

    prompt = f"""
You are KrashiMitra AI, an agricultural intelligence assistant for Indian farmers.

Use the structured farm context below to provide a practical, concise advisory.

Farm context:
{farm_context}

Identified condition: {display_disease}
Technical identifier: {raw_disease}

Provide a concise agricultural advisory in BOTH English and Hindi.
Format your response exactly with these section separators:

=== ENGLISH ===
**Main risk:** [Identify main agricultural risk using only facts explicitly provided in farm context; do not assume crop stage if not provided]
**Why the risk matters:** [2-3 concise bullet points using only provided facts; do not infer weather, symptoms, or causal links]
**What to do now:** [2-3 practical observation and verification steps; do not invent unverified sprays or treatments]
**More information needed:** [1-2 concise points noting missing details like crop stage or weather if not provided]

=== HINDI ===
**मुख्य जोखिम:** [Identify main agricultural risk in natural, farmer-readable Hindi using only provided facts; use readable display disease name]
**जोखिम क्यों महत्वपूर्ण है:** [2-3 concise bullet points in natural Hindi using only provided facts; do not infer unprovided weather or causes]
**अभी क्या करें:** [2-3 practical observation and verification steps in natural Hindi; do not invent unverified sprays]
**अतिरिक्त जानकारी की आवश्यकता:** [1-2 concise points in natural Hindi noting missing details if not provided]

Rules:
- Use only facts explicitly present in the farm context. Do not infer or invent crop stage, weather conditions, symptoms, disease severity, progression, or causal links.
- If details (such as crop stage, weather, or soil thresholds) are missing, state that they are not provided and ask for them under "More information needed" / "अतिरिक्त जानकारी की आवश्यकता".
- Treat soil_moisture as a recorded measurement value only unless crop-specific thresholds and context are provided. Do not call it favorable, high, or low, and do not link it to disease spread without evidence.
- Give only general observation, field inspection, and verification steps when disease-specific management is not supported. Do not invent sprays, medicines, or field actions as proven treatment. For uncertain treatment, advise checking the product label and consulting a local agricultural officer.
- In the Hindi section, use simple, natural farmer-readable Hindi in Devanagari script. Prefer short sentences and common words. Avoid awkward literal translations and mixed Hindi-English grammar.
- In the Hindi section, use only the readable display disease name ({display_disease}) in English/Latin script; do not repeat or output the raw technical identifier with triple underscores ({raw_disease}).
- Keep technical terms and measurements (e.g. {display_disease}, NDVI, Sentinel-2, numbers, units, and percentages) in English/Latin script.
- In Hindi, translate humidity as "आर्द्रता" or "हवा में नमी".
- Never output Chinese, Cyrillic, or any unrelated scripts or characters.
- Do not claim certainty when the available data is uncertain.
- Keep both sections concise and practical.

Return only the farmer advisory.
"""

    raw_output = ""
    try:
        gemini_start = time.perf_counter()

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
        )
        print(f"[PERF] Gemini: {time.perf_counter() - gemini_start:.2f}s")
        raw_output = interaction.output_text

    except Exception as gemini_error:
        print(f"Gemini advisory failed: {gemini_error}")
        fallback_start = time.perf_counter()
        raw_output = generate_openrouter_advisory(prompt)
        print(f"[PERF] Fallback total: {time.perf_counter() - fallback_start:.2f}s")

    en_advisory, hi_advisory = split_bilingual_advisory(raw_output)
    selected_advisory = hi_advisory if language != "english" else en_advisory
    return AdvisoryResult(
        selected_advisory, advisory_en=en_advisory, advisory_hi=hi_advisory
    )


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
