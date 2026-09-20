from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="In one sentence, explain why soil moisture matters for crop health."
)

print(interaction.output_text)