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

def build_prompt(input_text: str, text_type: str) -> str:
    # Adding strict output constraints
    return f"""
    Rewrite the text below in a {text_type} professional tone.
    
    CONSTRAINTS:
    - Output ONLY the professionalized paragraph.
    - Do not include introductory remarks (like "Here is your text").
    - Do not use quotes or labels.
    - Improve clarity and flow significantly.

    TEXT:
    {input_text}
    """

def professionalize(input_text: str, text_type: str) -> str:
    prompt = build_prompt(input_text, text_type)
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash",
            messages=[{"role": "user", "content": prompt}],
        )
        # Just return the string directly
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"
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
