# Podcast Transcription & Manipulation Engine

CLI-first, offline pipeline that downloads a single podcast episode, transcribes it locally with `whisper.cpp`, and generates a clean transcript, summary, and X/Twitter thread using a local Ollama model.

## Features
- Offline-by-default: yt-dlp + ffmpeg + whisper.cpp + Ollama (no cloud calls).
- Single command: download → transcribe → markdown → summary → X thread.
- Opinionated outputs and prompts for consistent results.
- Structured JSON logs with progress bars.

## Project Layout
```
podcast_engine/
├── cli.py                 # CLI entrypoint (python -m podcast_engine.cli <url>)
├── main.py                # Orchestration
├── config.py              # .env-driven settings and paths
├── logger.py              # JSON logging
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
Run from repo root:
```bash
python -m podcast_engine.cli "<public_podcast_audio_url>"
```
Outputs land under `podcast_engine/audio`, `podcast_engine/transcripts`, and `podcast_engine/outputs`.

## Troubleshooting
- DRM/Spotify: yt-dlp cannot fetch DRM-protected Spotify episodes. Use a public audio URL or RSS MP3.
- whisper.cpp errors: verify `WHISPER_CPP_BIN` and `WHISPER_MODEL_PATH` exist and are executable/readable.
- Ollama errors: ensure `ollama list` shows your model and Ollama is running locally.
- ffmpeg missing: install via Homebrew (`brew install ffmpeg`) or ensure it is on PATH.

## Extensibility
- Utilities are modular: swap downloader/transcriber/LLM backends with minimal changes.
- Prompts live in `podcast_engine/prompts` for easy iteration.
- Transcript JSON is the source of truth for downstream features (search, RAG, API/UI layers).
