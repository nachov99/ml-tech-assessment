from app.domain.models import TranscriptAnalysis
from app.ports.repository import TranscriptRepository


class InMemoryTranscriptRepository(TranscriptRepository):
    def __init__(self) -> None:
        self._storage: dict[str, TranscriptAnalysis] = {}
    
    def save(self, analysis: TranscriptAnalysis) -> None:
        self._storage[analysis.id] = analysis
    
    def get_by_id(self, id: str) -> TranscriptAnalysis | None:
        return self._storage.get(id)
    
    def get_all(self) -> list[TranscriptAnalysis]:
        return list(self._storage.values())
