import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# ----------------------------
# Improved Prompt Builder
# ----------------------------

def build_prompt(input_text: str, text_type: str) -> str:
    """Creates a prompt that forces a single paragraph output."""
    return f"""
    Rewrite the text below in a {text_type} professional tone.
    
    CONSTRAINTS:
    - Output ONLY the professionalized paragraph.
    - Do not include any intro, outro, or 'Here is the rewrite'.
    - Use a single, cohesive paragraph.
    - Correct all spelling and grammar mistakes.

    TEXT:
    {input_text}
    """

# ----------------------------
# Core Function
# ----------------------------

def professionalize(input_text: str, text_type: str) -> str:
    """Sends request to Gemini and returns a clean string."""
    prompt = build_prompt(input_text, text_type)
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash-lite", # Use a stable model name
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error contacting Gemini: {e}"

# ----------------------------
# Execution
# ----------------------------

if __name__ == "__main__":
    user_text = input("Enter the messy text: ")
    text_type = input("Enter style (corporate/academic/political): ")

    print("\n--- PROCESSING ---")
    
    # We only need one call now because our prompt is much stronger
    result = professionalize(user_text, text_type)

    print("\n=== CLEAN PROFESSIONAL OUTPUT ===")
    print(result)
