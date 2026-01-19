from fastapi import APIRouter, HTTPException

from podcast_engine.backend.schemas import (
    LogEntry,
    ProcessRequest,
    ProcessResponse,
    ResultsResponse,
    StatusResponse,
)
from podcast_engine.backend.services.engine_service import engine_service

router = APIRouter()


@router.post("/process", response_model=ProcessResponse)
def process_podcast(request: ProcessRequest) -> ProcessResponse:
    try:
        engine_service.start(str(request.url))
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ProcessResponse(status="accepted", message="Processing started.")


@router.get("/status", response_model=StatusResponse)
def get_status() -> StatusResponse:
    state = engine_service.status()
    logs = [
        LogEntry(
            time=entry["time"],
            level=entry["level"],
            message=entry["message"],
            stage=entry.get("stage"),
        )
        for entry in state.logs
    ]
    return StatusResponse(state=state.state, step=state.step, error=state.error, logs=logs)


@router.get("/results", response_model=ResultsResponse)
def get_results() -> ResultsResponse:
    results = engine_service.results()
    return ResultsResponse(
        transcript_markdown=results["transcript_markdown"],
        summary_markdown=results["summary_markdown"],
        thread_markdown=results["thread_markdown"],
    )
