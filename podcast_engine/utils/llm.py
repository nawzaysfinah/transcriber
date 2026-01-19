import shutil
import subprocess
from pathlib import Path


def _load_prompt(prompt_path: Path) -> str:
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8").strip()


def generate_content(model: str, prompt_path: Path, transcript_markdown: str, task: str) -> str:
    prompt_template = _load_prompt(prompt_path)
    composed_prompt = f"{prompt_template}\n\nTranscript:\n{transcript_markdown}"

    if shutil.which("ollama") is None:
        raise FileNotFoundError("Ollama CLI not found on PATH. Install and ensure it is available offline.")

    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=composed_prompt,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Ollama generation failed for {task}: {exc.stderr or exc.stdout}") from exc

    output = result.stdout.strip()
    if not output:
        raise RuntimeError(f"Ollama returned empty output for {task}")
    return output
