from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    whisper_cpp_bin: Path
    whisper_model_path: Path
    ollama_model: str
    audio_dir: Path
    transcripts_dir: Path
    outputs_dir: Path
    prompts_dir: Path

    @property
    def summaries_dir(self) -> Path:
        return self.outputs_dir / "summaries"

    @property
    def threads_dir(self) -> Path:
        return self.outputs_dir / "threads"

    @property
    def summary_prompt(self) -> Path:
        return self.prompts_dir / "summary.txt"

    @property
    def x_thread_prompt(self) -> Path:
        return self.prompts_dir / "x_thread.txt"


def _expand_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def load_settings() -> Settings:
    base_dir = Path(__file__).resolve().parent
    load_dotenv(base_dir / ".env")

    whisper_cpp_bin = _expand_path(os.getenv("WHISPER_CPP_BIN", "./whisper.cpp/build/bin/whisper-cli"))
    whisper_model_path = _expand_path(os.getenv("WHISPER_MODEL_PATH", "./models/ggml-small.en.bin"))
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3")

    audio_dir = _expand_path(os.getenv("AUDIO_DIR", str(base_dir / "audio")))
    transcripts_dir = _expand_path(os.getenv("TRANSCRIPTS_DIR", str(base_dir / "transcripts")))
    outputs_dir = _expand_path(os.getenv("OUTPUTS_DIR", str(base_dir / "outputs")))
    prompts_dir = _expand_path(os.getenv("PROMPTS_DIR", str(base_dir / "prompts")))

    for path in (audio_dir, transcripts_dir, outputs_dir, prompts_dir, outputs_dir / "summaries", outputs_dir / "threads"):
        path.mkdir(parents=True, exist_ok=True)

    return Settings(
        whisper_cpp_bin=whisper_cpp_bin,
        whisper_model_path=whisper_model_path,
        ollama_model=ollama_model,
        audio_dir=audio_dir,
        transcripts_dir=transcripts_dir,
        outputs_dir=outputs_dir,
        prompts_dir=prompts_dir,
    )
