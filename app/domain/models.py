from dataclasses import dataclass

@dataclass
class TranscriptAnalysis:
    id: str
    summary: str
    action_items: list[str]
