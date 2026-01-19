# Podcast Transcription & Manipulation Engine

Offline-first pipeline that downloads a single public audio link (e.g., YouTube), transcribes it locally with `whisper.cpp`, and generates a clean transcript, summary, and X/Twitter thread using a local Ollama model. Includes a local web UI (FastAPI + React/Vite) with live progress, logs, editable outputs, and downloads, while keeping the CLI as the source of truth.

## Features
- Offline-by-default: yt-dlp + ffmpeg + whisper.cpp + Ollama (no cloud calls).
- One run produces: audio → transcript JSON (source of truth) → formatted Markdown → summary → X thread.
- Local web UI: paste URL, see live progress/logs, edit summary/thread, download outputs; prevents concurrent jobs.
- CLI remains fully supported for headless use.
- Structured JSON logs and guarded error handling.

## Project Layout
```
podcast_engine/
├── cli.py                 # CLI entrypoint
├── main.py                # Core orchestration (used by CLI + API)
├── config.py / logger.py  # env + JSON logging
├── backend/               # FastAPI app wrapping the core engine
├── frontend/              # React/Vite single-page UI
├── prompts/               # summary.txt, x_thread.txt
├── utils/                 # downloader, transcriber, formatter, llm helpers
├── audio/                 # <episode_id>.mp3
├── transcripts/           # <episode_id>.json (source of truth) + .md
└── outputs/
    ├── summaries/         # <episode_id>_summary.md
    └── threads/           # <episode_id>_x_thread.md
```

## Prerequisites
- macOS, Python 3.11+.
- `ffmpeg` available on PATH.
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (installed via requirements).
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) built locally (binary `whisper-cli`).
- Whisper model file (e.g., `ggml-small.en.bin`) stored locally.
- [Ollama](https://ollama.ai) installed and a model pulled (default `ollama pull llama3`).
- Node 18+ for the frontend (Vite).

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r podcast_engine/requirements.txt
```

Configure paths in `podcast_engine/.env` if needed:
- `WHISPER_CPP_BIN` (default: `./whisper.cpp/build/bin/whisper-cli`)
- `WHISPER_MODEL_PATH` (default: `./models/ggml-small.en.bin`)
- `OLLAMA_MODEL` (default: `llama3`)
- `AUDIO_DIR`, `TRANSCRIPTS_DIR`, `OUTPUTS_DIR`, `PROMPTS_DIR` (override if desired)

## Usage
CLI (from repo root):
```bash
python -m podcast_engine.cli "<public_audio_url>"
```
Outputs land under `podcast_engine/audio`, `podcast_engine/transcripts`, and `podcast_engine/outputs`.

### Run the backend (FastAPI)
```bash
source .venv/bin/activate
uvicorn podcast_engine.backend.app:app --host 0.0.0.0 --port 8000 --reload
```

### Run the frontend (React/Vite)
```bash
cd podcast_engine/frontend
npm install
npm run dev
# open http://localhost:5173
```
The UI hits the local API at `http://localhost:8000` and prevents concurrent jobs. You can paste a public audio link, track progress, edit summary/thread, download outputs, and view logs in dark mode.

### One-shot launcher
```bash
./run.sh
```
Uses tmux if available (backend + frontend panes); otherwise starts backend in background and frontend in foreground.

## Troubleshooting
- DRM-protected sources (including many Spotify episodes) will not download. Use a public audio URL (e.g., YouTube, open RSS MP3).
- whisper.cpp errors: verify `WHISPER_CPP_BIN` and `WHISPER_MODEL_PATH` exist and are executable/readable.
- Ollama errors: ensure `ollama list` shows your model and Ollama is running locally.
- ffmpeg missing: install via Homebrew (`brew install ffmpeg`) or ensure it is on PATH.
- Transcription empty: ensure ffmpeg is present, the model path is valid, and the whisper binary is the built `whisper-cli`.

## Extensibility
- Utilities are modular: swap downloader/transcriber/LLM backends with minimal changes.
- Prompts live in `podcast_engine/prompts` for easy iteration.
- Transcript JSON is the source of truth for downstream features (search, RAG, API/UI layers).
- Backend wraps the core engine (no duplication) and can be reused by future API consumers.
- Frontend is a single-page UI with clear seams to grow into saved libraries or search later.
