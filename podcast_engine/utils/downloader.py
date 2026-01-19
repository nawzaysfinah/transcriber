import shutil
from pathlib import Path
from typing import Dict, Tuple

from tqdm import tqdm
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError


def download_audio(episode_url: str, output_dir: Path) -> Tuple[Path, Dict]:
    """
    Download a Spotify podcast episode as MP3 using yt-dlp.
    Returns the path to the MP3 file and a metadata dictionary.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if shutil.which("ffmpeg") is None:
        raise FileNotFoundError("ffmpeg is required for audio extraction but was not found on PATH.")

    progress = tqdm(total=100, desc="Downloading audio", unit="%", leave=False)

    def _hook(d: Dict) -> None:
        if d.get("status") == "downloading":
            try:
                percent = float(d.get("_percent_str", "0").replace("%", "").strip())
            except ValueError:
                percent = 0.0
            progress.n = int(percent)
            progress.refresh()
        elif d.get("status") in {"finished", "error"}:
            progress.n = 100
            progress.refresh()

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
        ],
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [_hook],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(episode_url, download=True)
    except (DownloadError, ExtractorError) as exc:
        raise RuntimeError(
            "Audio download failed. Spotify episodes are often DRM-protected; yt-dlp cannot fetch them. "
            "Use a publicly accessible audio URL or a podcast feed URL without DRM."
        ) from exc
    finally:
        progress.close()

    episode_id = info.get("id") or "episode"
    audio_path = output_dir / f"{episode_id}.mp3"

    metadata = {
        "id": episode_id,
        "title": info.get("title", "Unknown episode"),
        "duration": int(info.get("duration") or 0),
        "url": info.get("webpage_url", episode_url),
        "uploader": info.get("uploader"),
    }

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found at {audio_path}")

    return audio_path, metadata
