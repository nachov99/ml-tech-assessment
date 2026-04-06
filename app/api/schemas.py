import pydantic


class AnalyzeResponse(pydantic.BaseModel):
    id: str
    summary: str
    action_items: list[str]


class BatchAnalyzeRequest(pydantic.BaseModel):
    transcripts: list[str]
    

class BatchAnalyzeResponse(pydantic.BaseModel):
    results: list[AnalyzeResponse]
