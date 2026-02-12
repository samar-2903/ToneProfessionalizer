import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)



tone_professionalize_declaration = {
    "name": "professionalize_tone",
    "description": (
        "Professionalizes the tone of a given input text. "
        "Supports academic, corporate, political, or neutral styles."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "input_text": {
                "type": "string",
                "description": "The input text that needs to be professionalized",
            },
            "text_type": {
                "type": "string",
                "enum": ["academic", "corporate", "political", "default"],
                "description": "The professional domain/style to apply",
            },
        },
        "required": ["input_text", "text_type"],
    },
}

# ----------------------------
# Prompt Builder
# ----------------------------

def build_prompt(input_text: str, text_type: str, refine: bool = False) -> str:
    prompt = f"""
You are a professional writing assistant.

Rewrite the following text in a {text_type} professional tone.
"""

    if refine:
        prompt += (
            "Refine the text further by improving clarity, formality, "
            "and flow without changing the original meaning.\n"
        )

    prompt += f"""
TEXT:
{input_text}
"""

    return prompt.strip()

# ----------------------------
# Core Functions
# ----------------------------

def professionalize(input_text: str, text_type: str) -> dict:
    """
    First-pass professionalization using Gemini.
    """
    prompt = build_prompt(input_text, text_type)

    try:
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash-lite", # Updated model name string
            messages=[{"role": "user", "content": prompt}],
        )
        professional_text = response.choices[0].message.content.strip()
        
        # YOU NEEDED THIS RETURN BLOCK:
        return {
            "professional_text": professional_text,
            "text_type": text_type
        }

    except Exception as e:
        print("GEMINI ERROR:", e)
        raise

def change_recommendation(previous_output: dict) -> dict:
    """
    Second-pass refinement using Gemini.
    """
    prompt = build_prompt(
        previous_output["professional_text"],
        previous_output["text_type"],
        refine=True
    )

    try:
        response = client.chat.completions.create(
            model="google/gemini-3-flash-preview",
            messages=[{"role": "user", "content": prompt}],
        )
        refined_text = response.choices[0].message.content.strip()

    except Exception as e:
        refined_text = previous_output["professional_text"]

    return {
        "professional_text": refined_text,
        "text_type": previous_output["text_type"]
    }

# ----------------------------
# Terminal Test Harness
# ----------------------------

if __name__ == "__main__":
    user_text = input("Please enter the text here")
    text_type = input("Please enter the text type")

    print("\n=== ORIGINAL INPUT ===")
    print(user_text)

    v1 = professionalize(user_text, text_type)

    print("\n=== PROFESSIONALIZED OUTPUT ===")
    print(v1["professional_text"])

    v2 = change_recommendation(v1)

    print("\n=== REFINED OUTPUT ===")
    print(v2["professional_text"])
