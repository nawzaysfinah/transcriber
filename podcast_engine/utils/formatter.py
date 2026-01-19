from pathlib import Path
from typing import Dict


def _format_timestamp(seconds: float) -> str:
    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def transcript_to_markdown(transcript: Dict) -> str:
    title = transcript.get("title") or "Podcast Episode"
    duration = transcript.get("duration", 0)
    language = transcript.get("language", "unknown")
    source_url = transcript.get("source_url", "")

    lines = [
        f"# {title}",
        "",
        f"- Source: {source_url}",
        f"- Duration: {_format_timestamp(duration)}",
        f"- Language: {language}",
        "",
        "## Transcript",
    ]

    for segment in transcript.get("segments", []):
        start = _format_timestamp(segment.get("start", 0.0))
        end = _format_timestamp(segment.get("end", 0.0))
        text = segment.get("text", "").strip()
        lines.append(f"- [{start} - {end}] {text}")

    return "\n".join(lines).strip() + "\n"


def save_markdown(transcript: Dict, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    markdown = transcript_to_markdown(transcript)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path
