import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ----------------------------
# ENV + OPENROUTER SETUP
# ----------------------------

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# ----------------------------
# FASTAPI SETUP
# ----------------------------

app = FastAPI()

# CORS (needed for JS frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # devathon-safe
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# REQUEST / RESPONSE MODELS
# ----------------------------

class ToneRequest(BaseModel):
    input_text: str
    text_type: str


class ToneResponse(BaseModel):
    professional_text: str
    text_type: str


# ----------------------------
# FUNCTION DECLARATION (UNCHANGED)
# ----------------------------

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
# PROMPT BUILDER (UNCHANGED LOGIC)
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
# CORE LOGIC (UNCHANGED)
# ----------------------------

def professionalize(input_text: str, text_type: str) -> dict:
    prompt = build_prompt(input_text, text_type)

    try:
        response = client.chat.completions.create(
            model="google/gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
        )
        professional_text = response.choices[0].message.content.strip()

    except Exception as e:
        print("GEMINI ERROR (professionalize):", e)
        professional_text = input_text

    return {
        "professional_text": professional_text,
        "text_type": text_type
    }


def change_recommendation(previous_output: dict) -> dict:
    prompt = build_prompt(
        previous_output["professional_text"],
        previous_output["text_type"],
        refine=True
    )

    try:
        response = client.chat.completions.create(
            model="google/gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
        )
        refined_text = response.choices[0].message.content.strip()

    except Exception as e:
        print("GEMINI ERROR (refine):", e)
        refined_text = previous_output["professional_text"]

    return {
        "professional_text": refined_text,
        "text_type": previous_output["text_type"]
    }

# ----------------------------
# FASTAPI ENDPOINTS (WRAPPER ONLY)
# ----------------------------

@app.post("/professionalize", response_model=ToneResponse)
def professionalize_api(req: ToneRequest):
    return professionalize(req.input_text, req.text_type)


@app.post("/refine", response_model=ToneResponse)
def refine_api(req: ToneRequest):
    initial = {
        "professional_text": req.input_text,
        "text_type": req.text_type
    }
    return change_recommendation(initial)
