import json
import subprocess
from pathlib import Path
from typing import Dict, Tuple

from tqdm import tqdm

from podcast_engine.config import Settings


def transcribe_audio(
    audio_path: Path,
    settings: Settings,
    metadata: Dict,
    source: str = "spotify",
) -> Tuple[Path, Dict]:
    """
    Run whisper.cpp to produce a transcript JSON and normalize it to the required schema.
    """
    transcripts_dir = settings.transcripts_dir
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    episode_id = metadata.get("id", audio_path.stem)
    tmp_output_base = transcripts_dir / f"{episode_id}_raw"
    raw_json_path = Path(f"{tmp_output_base}.json")

    whisper_bin = settings.whisper_cpp_bin
    if whisper_bin.name == "main":
        candidate = whisper_bin.with_name("whisper-cli")
        if candidate.exists():
            whisper_bin = candidate
    if not whisper_bin.exists():
        raise FileNotFoundError(f"whisper.cpp binary not found at {whisper_bin}")
    if not settings.whisper_model_path.exists():
        raise FileNotFoundError(f"Whisper model not found at {settings.whisper_model_path}")

    progress = tqdm(total=1, desc="Transcribing audio", leave=False)

    cmd = [
        str(whisper_bin),
        "-m",
        str(settings.whisper_model_path),
        "-f",
        str(audio_path),
        "-of",
        str(tmp_output_base),
        "-oj",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        progress.close()
        stdout = exc.stdout.decode() if exc.stdout else ""
        stderr = exc.stderr.decode() if exc.stderr else ""
        raise RuntimeError(f"whisper.cpp failed: {stderr or stdout}") from exc

    progress.update(1)
    progress.close()

    if not raw_json_path.exists():
        raise FileNotFoundError(f"whisper.cpp did not produce JSON at {raw_json_path}")

    with raw_json_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    segments = []
    for segment in raw_data.get("segments", []):
        text = segment.get("text", "").strip()
        if not text:
            continue
        segments.append(
            {
                "start": float(segment.get("start", 0.0)),
                "end": float(segment.get("end", 0.0)),
                "text": text,
            }
        )

    transcript = {
        "source": source,
        "source_url": metadata.get("url"),
        "title": metadata.get("title"),
        "duration": int(metadata.get("duration") or 0),
        "language": raw_data.get("language", "unknown"),
        "segments": segments,
    }

    final_path = transcripts_dir / f"{episode_id}.json"
    with final_path.open("w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)

    # Clean up raw output to avoid clutter but keep the normalized version.
    if raw_json_path.exists():
        raw_json_path.unlink()

    return final_path, transcript
