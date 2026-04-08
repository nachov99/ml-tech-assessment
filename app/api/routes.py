import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import (
    AnalyzeResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
)
from app.domain.exceptions import TranscriptEmptyError, LLMOutputError
from app.services.transcript_service import TranscriptService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


def get_service() -> TranscriptService:
    raise RuntimeError("Service dependency not configured")


@router.get("/analyze", response_model=AnalyzeResponse)
async def analyze_transcript(
    transcript: str,
    service: TranscriptService = Depends(get_service),
):
    logger.info("Analyzing transcript of length %d", len(transcript))
    try:
        result = service.analyze(transcript)
    except TranscriptEmptyError as e:
        logger.warning("Validation error: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except LLMOutputError as e:
        logger.error("LLM output validation failed: %s", str(e))
        raise HTTPException(status_code=502, detail=str(e))
    except Exception:
        logger.exception("LLM call failed")
        raise HTTPException(status_code=502, detail="LLM service unavailable")
    logger.info("Transcript analyzed successfully: %s", result.id)
    return AnalyzeResponse(
        id=result.id,
        summary=result.summary,
        action_items=result.action_items,
    )


@router.get("/", response_model=list[AnalyzeResponse])
async def list_transcripts(
    service: TranscriptService = Depends(get_service),
):
    logger.info("Listing all transcript analyses")
    results = service.get_all()
    return [
        AnalyzeResponse(
            id=r.id,
            summary=r.summary,
            action_items=r.action_items,
        )
        for r in results
    ]


@router.get("/{id}", response_model=AnalyzeResponse)
async def get_transcript(
    id: str,
    service: TranscriptService = Depends(get_service),
):
    logger.info("Fetching transcript id=%s", id)
    result = service.get_by_id(id)
    if result is None:
        logger.warning("Transcript not found: id=%s", id)
        raise HTTPException(status_code=404, detail="Transcript analysis not found")
    logger.info("Transcript fetched successfully: id=%s", id)
    return AnalyzeResponse(
        id=result.id,
        summary=result.summary,
        action_items=result.action_items,
    )


@router.post("/analyze-batch", response_model=BatchAnalyzeResponse)
async def analyze_batch(
    request: BatchAnalyzeRequest,
    service: TranscriptService = Depends(get_service),
):
    logger.info("Batch analysis requested for %d transcripts", len(request.transcripts))
    if not request.transcripts:
        raise HTTPException(status_code=400, detail="Transcripts list cannot be empty")
    try:
        results = await service.analyze_batch(request.transcripts)
    except TranscriptEmptyError as e:
        logger.warning("Validation error during batch analysis: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except LLMOutputError as e:
        logger.error("LLM output validation failed during batch: %s", str(e))
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error during batch analysis: %s", str(e))
        raise HTTPException(status_code=502, detail="LLM service unavailable")
    logger.info("Batch analysis completed successfully for %d transcripts", len(results))
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
