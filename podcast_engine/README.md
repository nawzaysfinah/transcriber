# Podcast Transcription & Manipulation Engine

Offline-first CLI that downloads a Spotify podcast episode, transcribes it locally with `whisper.cpp`, and produces a transcript, Markdown, a concise summary, and an X (Twitter) thread using a local Ollama model.

## Features
- Single-command pipeline: download → transcribe → format → summarise → X thread
- Fully offline: yt-dlp + whisper.cpp + Ollama (no cloud APIs)
- Structured logs and progress indicators
- Opinionated folder layout for future extensions

## Prerequisites
- macOS with Python 3.11+ (tested), `ffmpeg`, and `git`
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) Python package (installed via `requirements.txt`)
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) built locally (set `WHISPER_CPP_BIN` to its binary)
- Whisper model file (e.g., `ggml-medium.en.bin` or `ggml-small.en.bin`) downloaded locally
- [Ollama](https://ollama.ai) installed with a local model (e.g., `ollama pull llama3`)

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r podcast_engine/requirements.txt
```

Update `.env` if paths differ:
- `WHISPER_CPP_BIN`: Path to whisper.cpp binary (e.g., `./whisper.cpp/build/bin/whisper-cli`)
- `WHISPER_MODEL_PATH`: Path to local model file (default: `./models/ggml-small.en.bin`)
- `OLLAMA_MODEL`: Local Ollama model name
- `AUDIO_DIR`, `TRANSCRIPTS_DIR`, `OUTPUTS_DIR`, `PROMPTS_DIR`: Override directories if desired

## Usage
Run from the repository root so the package resolves correctly:
```bash
python -m podcast_engine.cli "<spotify_episode_url>"
```
Outputs are written to:
- `audio/<episode_id>.mp3`
- `transcripts/<episode_id>.json` (source of truth)
- `transcripts/<episode_id>.md`
- `outputs/summaries/<episode_id>_summary.md`
- `outputs/threads/<episode_id>_x_thread.md`

## Notes on whisper.cpp
- Ensure `ffmpeg` is available for yt-dlp to extract audio.
- Choose a balanced model (e.g., medium/small) for speed vs. accuracy.

## Extension Points
- Utilities are modular: swap downloader/transcriber/LLM without touching CLI.
- Clear seams for future semantic search, knowledge ingestion, or API/UI layers.

## Troubleshooting
- Spotify episodes are usually DRM-protected and cannot be downloaded by yt-dlp; use a publicly accessible audio URL or podcast feed.
- Download errors: confirm the URL is a valid Spotify episode and yt-dlp is up to date.
- Transcription errors: verify `WHISPER_CPP_BIN` and `WHISPER_MODEL_PATH` paths.
- LLM errors: ensure Ollama is running and the configured model is pulled locally.
