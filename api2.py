import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"),
)


app = FastAPI()
api_router = APIRouter(prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIST_DIR = os.path.join(BASE_DIR, "tone-ui", "dist")
LEGACY_STATIC_DIR = os.path.join(BASE_DIR, "static")

STATIC_DIR = UI_DIST_DIR if os.path.isdir(UI_DIST_DIR) else LEGACY_STATIC_DIR

assets_dir = os.path.join(STATIC_DIR, "assets")
if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {
        "error": (
            "Frontend not built. Run `npm install` and `npm run build` "
            "inside tone-ui to create tone-ui/dist/."
        )
    }


class ToneRequest(BaseModel):
    input_text: str
    text_type: str


class ToneResponse(BaseModel):
    professional_text: str
    text_type: str



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


def build_prompt(input_text: str, text_type: str, refine: bool = False) -> str:
    prompt = f"""
Rewrite the text below in a {text_type} professional tone.
    
    CONSTRAINTS:
    - Output ONLY the professionalized paragraph.
    - Do not include any intro, outro, or 'Here is the rewrite'.
    - Use a single, cohesive paragraph.
    - Correct all spelling and grammar mistakes.
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


def professionalize(input_text: str, text_type: str) -> dict:
    prompt = build_prompt(input_text, text_type)

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        professional_text = response.choices[0].message.content.strip()

    except Exception as e:
        print("api2 (professionalize):", e)
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
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        refined_text = response.choices[0].message.content.strip()

    except Exception as e:
        print("OPENAI ERROR (refine):", e)
        refined_text = previous_output["professional_text"]

    return {
        "professional_text": refined_text,
        "text_type": previous_output["text_type"]
    }


@api_router.post("/professionalize", response_model=ToneResponse)
def professionalize_api(req: ToneRequest):
    return professionalize(req.input_text, req.text_type)


@api_router.post("/refine", response_model=ToneResponse)
def refine_api(req: ToneRequest):
    initial = {
        "professional_text": req.input_text,
        "text_type": req.text_type
    }
    return change_recommendation(initial)


app.include_router(api_router)

@app.post("/professionalize", response_model=ToneResponse)
def professionalize_api_legacy(req: ToneRequest):
    return professionalize(req.input_text, req.text_type)


@app.post("/refine", response_model=ToneResponse)
def refine_api_legacy(req: ToneRequest):
    initial = {
        "professional_text": req.input_text,
        "text_type": req.text_type
    }
    return change_recommendation(initial)
