# AGENTS.md

Project memory for `ai-arena-vc` — a minimal clone of arena.ai.

## What this project is
A very simple arena.ai clone: the user enters one prompt, and the responses of
two AI models are shown side by side for comparison. No voting, no streaming.

## Architecture & key reasoning
- **Groq platform only.** Both models are served *by Groq* (we never call
  OpenAI's API directly). `openai/gpt-oss-120b` is an OpenAI model **hosted on
  Groq's platform** — it is called through Groq exactly like
  `llama-3.3-70b-versatile`.
- **Use the official `groq` Python package** (not the raw `openai` SDK). It
  points at Groq's API by default, so the code stays clean:
  `from groq import Groq` + `client.chat.completions.create(...)`.
- **Parallel calls.** The two model calls run concurrently via
  `concurrent.futures.ThreadPoolExecutor(max_workers=2)` so total latency is
  ~one model's response time, not the sum.
- **Per-model error isolation.** Each model call is wrapped so a failure on one
  side shows an error message in that column instead of crashing the run.

## UI (Gradio)
- `Blocks` layout: prompt `TextBox` → Submit (primary) + Clear buttons → two
  side-by-side output `TextBox`es labeled with each model name.
- Enter key in the prompt box also triggers Submit.
- **Clear** resets the prompt and both outputs so the user can try a new prompt.

## Project structure
- `main.py` — Groq client, `get_response()`, `compare()` (parallel), and the
  Gradio `Blocks` UI.
- `pyproject.toml` — deps managed by `uv` (`gradio`, `groq`).

## Conventions
- Dependency manager: **uv**. Add deps with `uv add <pkg>`.
- A virtualenv is created by `uv` at `.venv` (created automatically on first
  `uv sync`). Activate it before running: `source .venv/bin/activate`. If it
  doesn't exist yet, run `uv sync` first so uv creates a fresh one and installs
  dependencies.
- API key: `GROQ_API_KEY` (read from env at runtime; never hardcode).

## How to run
```
uv sync                # creates .venv and installs deps if missing
source .venv/bin/activate
python main.py
```
Then open the printed Gradio URL (default `http://127.0.0.1:7860`).
