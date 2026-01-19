import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import HTTPException, status

from podcast_engine.logger import get_logger
from podcast_engine.main import process_episode


@dataclass
class JobState:
    state: str = "idle"  # idle, running, completed, error
    step: Optional[str] = None
    error: Optional[str] = None
    logs: List[Dict] = field(default_factory=list)


class InMemoryLogHandler(logging.Handler):
    def __init__(self, job_state: JobState):
        super().__init__()
        self.job_state = job_state

    def emit(self, record: logging.LogRecord) -> None:
        entry = {
            "time": datetime.utcfromtimestamp(record.created),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "stage": getattr(record, "stage", None),
        }
        if entry["stage"]:
            self.job_state.step = entry["stage"]
        self.job_state.logs.append(entry)


class EngineService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._job_state = JobState()
        self._results: Optional[Dict[str, str]] = None
        self._thread: Optional[threading.Thread] = None

    def start(self, url: str) -> None:
        self.acquire()
        # Reset state
        self._job_state = JobState(state="running", step="init", logs=[])
        self._results = None

        self._thread = threading.Thread(target=self._run_job, args=(url,), daemon=True)
        self._thread.start()

    def _run_job(self, url: str) -> None:
        logger = get_logger("podcast_engine")
        handler = InMemoryLogHandler(self._job_state)
        logger.addHandler(handler)
        try:
            paths = process_episode(url)
            self._results = {
                "transcript_markdown": Path(paths["transcript_md"]).read_text(encoding="utf-8"),
                "summary_markdown": Path(paths["summary"]).read_text(encoding="utf-8"),
                "thread_markdown": Path(paths["thread"]).read_text(encoding="utf-8"),
            }
            self._job_state.state = "completed"
            self._job_state.step = "complete"
        except Exception as exc:  # noqa: BLE001
            self._job_state.state = "error"
            self._job_state.error = str(exc)
            self._job_state.step = self._job_state.step or "error"
        finally:
            logger.removeHandler(handler)
            if self._lock.locked():
                self._lock.release()

    def status(self) -> JobState:
        return self._job_state

    def results(self) -> Dict[str, str]:
        if self._job_state.state != "completed" or not self._results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Results are not available. Run a job first.",
            )
        return self._results

    def acquire(self) -> None:
        acquired = self._lock.acquire(blocking=False)
        if not acquired:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A job is already running. Please wait until it completes.",
            )


engine_service = EngineService()
