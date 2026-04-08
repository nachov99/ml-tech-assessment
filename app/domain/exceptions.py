class TranscriptEmptyError(ValueError):
    """Raised when a transcript is empty or whitespace-only."""
    pass


class LLMOutputError(RuntimeError):
    """Raised when LLM output fails validation (e.g. empty summary or no action items)."""
    pass
