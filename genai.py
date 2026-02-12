import os
from openai import OpenAI

# The client gets the API key from the environment variable `OPENROUTER_API_KEY`.
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

response = client.chat.completions.create(
    model="google/gemini-3-flash-preview",
    messages=[{"role": "user", "content": "Explain how AI works in a few words"}],
)
print(response.choices[0].message.content)
