from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
)
from app.services.transcript_service import TranscriptService

router = APIRouter(prefix="/transcripts", tags=["transcripts"])

_service: TranscriptService | None = None


def init_router(service: TranscriptService) -> None:
    global _service
    _service = service


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_transcript(request: AnalyzeRequest):
    try:
        result = _service.analyze(request.transcript)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail="LLM service unavailable")
    return AnalyzeResponse(
        id=result.id,
        summary=result.summary,
        action_items=result.action_items,
    )


@router.get("/{id}", response_model=AnalyzeResponse)
async def get_transcript(id: str):
    result = _service.get_by_id(id)
    if result is None:
        raise HTTPException(status_code=404, detail="Transcript analysis not found")
    return AnalyzeResponse(
        id=result.id,
        summary=result.summary,
        action_items=result.action_items,
    )


@router.post("/analyze-batch", response_model=BatchAnalyzeResponse)
async def analyze_batch(request: BatchAnalyzeRequest):
    if not request.transcripts:
        raise HTTPException(status_code=400, detail="Transcripts list cannot be empty")
    try:
        results = await _service.analyze_batch(request.transcripts)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail="LLM service unavailable")
    return BatchAnalyzeResponse(
        results=[
            AnalyzeResponse(
                id=r.id,
                summary=r.summary,
                action_items=r.action_items,
            )
            for r in results
        ]
    )
