# Tone Professionalizer

## Overview
A small web app that rewrites user text into a professional tone (corporate, academic, political) and can iteratively refine the result. The frontend is a React UI and the backend is a FastAPI service that calls OpenRouter models.

## Features
- Professionalize text into selected tone.
- Refine output repeatedly.
- Light/dark theme toggle.
- Copy-to-clipboard for results.

## Project Layout
- `api.py`: FastAPI app, OpenRouter client, API endpoints, and static file serving.
- `tone-ui/`: Vite + React frontend.
- `tone-ui/src/App.tsx`: Main UI logic.
- `tone-ui/src/style.css`: UI styling.
- `tone-ui/src/components/ui/bg-pattern.tsx`: Background pattern component.
- `main.py`, `tone.py`, `test3.py`, `genai.py`: earlier/experimental scripts.
- `index.html`, `index2.html`: legacy static prototypes.

## Tech Stack
Backend
- Python
- FastAPI
- Pydantic
- python-dotenv
- OpenAI SDK configured for OpenRouter

Frontend
- React + TypeScript
- Vite
- Tailwind CSS
- clsx + tailwind-merge

## Setup

### 1) Create `.env`
Create a `.env` file in the project root with:

```
OPENROUTER_API_KEY=your_key_here
```

### 2) Install frontend deps
From `tone-ui/`:

```
npm install
```

### 3) Build the frontend
From `tone-ui/`:

```
npm run build
```

This creates `tone-ui/dist/`, which `api.py` serves as the static frontend.

### 4) Run the backend
From the project root:

```
python api.py
```

Then open `http://localhost:8000` in your browser.

## Development (frontend)
If you want to run the UI in dev mode instead of using FastAPI static files:

```
cd tone-ui
npm run dev
```

By default, the frontend calls `/api`. If your API runs elsewhere, set:

```
VITE_API_BASE=http://localhost:8000/api
```

## API
Base path: `/api`

### POST `/api/professionalize`
Request body:
```
{
  "input_text": "string",
  "text_type": "corporate" | "academic" | "political"
}
```
Response:
```
{
  "professional_text": "string",
  "text_type": "corporate" | "academic" | "political"
}
```

### POST `/api/refine`
Same request and response format as `/professionalize`. Uses the previous output as input and refines it further.

## Notes
- The backend uses OpenRouter via the OpenAI SDK with `base_url="https://openrouter.ai/api/v1"`.
- If `tone-ui/dist/` does not exist, the root `/` route returns an error message with build instructions.

## Common Commands
From `tone-ui/`:
- `npm run dev`
- `npm run build`
- `npm run preview`
