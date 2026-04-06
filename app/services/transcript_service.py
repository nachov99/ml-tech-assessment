import asyncio
import logging
import uuid

from app.domain.models import TranscriptAnalysis
from app.dto.llm_response import TranscriptAnalysisDTO
from app.ports.llm import LLm
from app.ports.repository import TranscriptRepository
from app.prompts import SYSTEM_PROMPT, RAW_USER_PROMPT

logger = logging.getLogger(__name__)


class TranscriptService:
    def __init__(self, llm: LLm, repository: TranscriptRepository) -> None:
        self._llm = llm
        self._repository = repository
        
    def analyze(self, transcript: str) -> TranscriptAnalysis:
        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty")
        
        user_prompt = RAW_USER_PROMPT.format(transcript=transcript)
        logger.info("Calling LLM for single analysis")
        dto = self._llm.run_completion(SYSTEM_PROMPT, user_prompt, TranscriptAnalysisDTO)
        
        if not dto.summary or not dto.summary.strip():
            raise RuntimeError("LLM returned an empty summary")
        if not dto.action_items:
            raise RuntimeError("LLM returned no action items")
        
        analysis = TranscriptAnalysis(
            id=str(uuid.uuid4()),
            summary=dto.summary,
            action_items=dto.action_items,
        )
        self._repository.save(analysis)
        logger.info("Transcript analysis saved: id=%s", analysis.id)
        return analysis
    
    def get_by_id(self, id: str) -> TranscriptAnalysis | None:
        return self._repository.get_by_id(id)
    
    def get_all(self) -> list[TranscriptAnalysis]:
        return self._repository.get_all()
    
    async def analyze_batch(self, transcripts: list[str]) -> list[TranscriptAnalysis]:
        for t in transcripts:
            if not t or not t.strip():
                raise ValueError("Transcript cannot be empty")
        
        logger.info("Calling LLM for %d transcripts concurrently", len(transcripts))
        tasks = [
            self._llm.run_completion_async(
                SYSTEM_PROMPT,
                RAW_USER_PROMPT.format(transcript=t),
                TranscriptAnalysisDTO,
            )
            for t in transcripts
        ]
        
        results = await asyncio.gather(*tasks)
        
        analyses = []
        for dto in results:
            if not dto.summary or not dto.summary.strip():
                raise RuntimeError("LLM returned an empty summary")
            if not dto.action_items:
                raise RuntimeError("LLM returned no action items")
            analysis = TranscriptAnalysis(
                id=str(uuid.uuid4()),
                summary=dto.summary,
                action_items=dto.action_items,
            )
            self._repository.save(analysis)
            analyses.append(analysis)
        logger.info("Batch complete, saved %d analyses", len(analyses))
        return analyses
