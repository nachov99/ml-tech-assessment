from abc import ABC, abstractmethod

from app.domain.models import TranscriptAnalysis

class TranscriptRepository(ABC):
    @abstractmethod
    def save(self, analysis: TranscriptAnalysis) -> None:
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> TranscriptAnalysis | None:
        pass

    @abstractmethod
    def get_all(self) -> list[TranscriptAnalysis]:
        pass
