from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, field_validator


class ProcessRequest(BaseModel):
    url: HttpUrl

    @field_validator("url")
    @classmethod
    def ensure_spotify_or_http(cls, v: HttpUrl) -> HttpUrl:
        # Requirement notes: validate Spotify format; we also allow any HTTP(S) URL but flag malformed input.
        if v.scheme not in {"http", "https"}:
            raise ValueError("URL must be http or https")
        return v


class ProcessResponse(BaseModel):
    status: str
    message: str


class LogEntry(BaseModel):
    time: datetime
    level: str
    message: str
    stage: Optional[str] = None


class StatusResponse(BaseModel):
    state: str  # idle, running, completed, error
    step: Optional[str] = None
    error: Optional[str] = None
    logs: List[LogEntry] = []


class ResultsResponse(BaseModel):
    transcript_markdown: str
    summary_markdown: str
    thread_markdown: str
