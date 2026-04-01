import pydantic

class TranscriptAnalysisDTO(pydantic.BaseModel):
    summary: str
    action_items: list[str]