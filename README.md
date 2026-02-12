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

