from pathlib import Path
from typing import Dict, Tuple

from podcast_engine.config import load_settings
from podcast_engine.logger import get_logger
from podcast_engine.utils.downloader import download_audio
from podcast_engine.utils.formatter import save_markdown
from podcast_engine.utils.llm import generate_content
from podcast_engine.utils.transcriber import transcribe_audio

logger = get_logger("podcast_engine")


def _episode_id_from(metadata: Dict, audio_path: Path) -> str:
    return metadata.get("id") or audio_path.stem


def process_episode(episode_url: str) -> Dict[str, Path]:
    settings = load_settings()
    logger.info("Starting processing", extra={"stage": "init", "url": episode_url})

    audio_path: Path
    metadata: Dict
    try:
        audio_path, metadata = download_audio(episode_url, settings.audio_dir)
        logger.info(
            "Audio downloaded",
            extra={"stage": "download", "audio": str(audio_path), "metadata": metadata},
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Audio download failed", extra={"stage": "download", "error": str(exc)})
        raise

    try:
        transcript_json_path, transcript_data = transcribe_audio(audio_path, settings, metadata)
        logger.info(
            "Transcription complete",
            extra={"stage": "transcription", "transcript": str(transcript_json_path)},
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Transcription failed", extra={"stage": "transcription", "error": str(exc)})
        raise

    episode_id = _episode_id_from(metadata, audio_path)
    transcript_md_path = settings.transcripts_dir / f"{episode_id}.md"
    save_markdown(transcript_data, transcript_md_path)
    logger.info(
        "Formatted transcript saved",
        extra={"stage": "formatting", "markdown": str(transcript_md_path)},
    )

    transcript_markdown = transcript_md_path.read_text(encoding="utf-8")

    summary_output = settings.summaries_dir / f"{episode_id}_summary.md"
    thread_output = settings.threads_dir / f"{episode_id}_x_thread.md"

    try:
        summary_text = generate_content(settings.ollama_model, settings.summary_prompt, transcript_markdown, "summary")
        summary_output.write_text(summary_text + "\n", encoding="utf-8")
        logger.info("Summary generated", extra={"stage": "llm", "output": str(summary_output)})
    except Exception as exc:  # noqa: BLE001
        logger.exception("Summary generation failed", extra={"stage": "llm", "error": str(exc)})
        raise

    try:
        thread_text = generate_content(settings.ollama_model, settings.x_thread_prompt, transcript_markdown, "x_thread")
        thread_output.write_text(thread_text + "\n", encoding="utf-8")
        logger.info("X thread generated", extra={"stage": "llm", "output": str(thread_output)})
    except Exception as exc:  # noqa: BLE001
        logger.exception("Thread generation failed", extra={"stage": "llm", "error": str(exc)})
        raise

    logger.info("Processing finished", extra={"stage": "complete"})
    return {
        "audio": audio_path,
        "transcript_json": transcript_json_path,
        "transcript_md": transcript_md_path,
        "summary": summary_output,
        "thread": thread_output,
    }
