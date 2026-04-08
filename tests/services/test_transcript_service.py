import pytest
from unittest.mock import MagicMock, AsyncMock

from app.domain.exceptions import TranscriptEmptyError, LLMOutputError
from app.domain.models import TranscriptAnalysis
from app.dto.llm_response import TranscriptAnalysisDTO
from app.services.transcript_service import TranscriptService


def _make_service():
    llm = MagicMock()
    repository = MagicMock()
    service = TranscriptService(llm=llm, repository=repository)
    return service, llm, repository


def test_analyze_returns_analysis():
    service, llm, repository = _make_service()
    llm.run_completion.return_value = TranscriptAnalysisDTO(
        summary="Test summary",
        action_items=["action 1"],
    )

    result = service.analyze("some transcript")

    assert isinstance(result, TranscriptAnalysis)
    assert result.summary == "Test summary"
    assert result.action_items == ["action 1"]
    assert len(result.id) > 0


def test_analyze_calls_llm_with_correct_args():
    service, llm, repository = _make_service()
    llm.run_completion.return_value = TranscriptAnalysisDTO(
        summary="s", action_items=["a1"]
    )

    service.analyze("hello world")

    llm.run_completion.assert_called_once()
    args = llm.run_completion.call_args
    assert "hello world" in args[0][1]
    assert args[0][2] is TranscriptAnalysisDTO


def test_analyze_saves_to_repository():
    service, llm, repository = _make_service()
    llm.run_completion.return_value = TranscriptAnalysisDTO(
        summary="s", action_items=["a1"]
    )

    result = service.analyze("transcript")

    repository.save.assert_called_once()
    saved = repository.save.call_args[0][0]
    assert saved.id == result.id


def test_analyze_raises_on_empty_transcript():
    service, llm, repository = _make_service()

    with pytest.raises(TranscriptEmptyError, match="Transcript cannot be empty"):
        service.analyze("")

    with pytest.raises(TranscriptEmptyError, match="Transcript cannot be empty"):
        service.analyze("   ")


def test_get_by_id_delegates_to_repository():
    service, llm, repository = _make_service()
    expected = TranscriptAnalysis(id="123", summary="s", action_items=[])
    repository.get_by_id.return_value = expected

    result = service.get_by_id("123")

    assert result == expected
    repository.get_by_id.assert_called_once_with("123")


def test_get_by_id_returns_none_when_not_found():
    service, llm, repository = _make_service()
    repository.get_by_id.return_value = None

    result = service.get_by_id("nonexistent")

    assert result is None


@pytest.mark.asyncio
async def test_analyze_batch_processes_concurrently():
    service, llm, repository = _make_service()
    llm.run_completion_async = AsyncMock(
        side_effect=[
            TranscriptAnalysisDTO(summary="summary 1", action_items=["a1"]),
            TranscriptAnalysisDTO(summary="summary 2", action_items=["a2"]),
        ]
    )

    results = await service.analyze_batch(["transcript 1", "transcript 2"])

    assert len(results) == 2
    assert results[0].summary == "summary 1"
    assert results[1].summary == "summary 2"
    assert llm.run_completion_async.call_count == 2
    assert repository.save.call_count == 2


@pytest.mark.asyncio
async def test_analyze_batch_raises_on_empty_transcript():
    service, llm, repository = _make_service()

    with pytest.raises(TranscriptEmptyError, match="Transcript cannot be empty"):
        await service.analyze_batch(["valid", ""])


def test_analyze_raises_on_empty_llm_summary():
    service, llm, repository = _make_service()
    llm.run_completion.return_value = TranscriptAnalysisDTO(
        summary="", action_items=["a1"]
    )

    with pytest.raises(LLMOutputError, match="empty summary"):
        service.analyze("valid transcript")


def test_analyze_raises_on_empty_llm_action_items():
    service, llm, repository = _make_service()
    llm.run_completion.return_value = TranscriptAnalysisDTO(
        summary="valid summary", action_items=[]
    )

    with pytest.raises(LLMOutputError, match="no action items"):
        service.analyze("valid transcript")


@pytest.mark.asyncio
async def test_analyze_batch_raises_on_empty_llm_summary():
    service, llm, repository = _make_service()
    llm.run_completion_async = AsyncMock(
        return_value=TranscriptAnalysisDTO(summary="", action_items=["a1"])
    )

    with pytest.raises(LLMOutputError, match="empty summary"):
        await service.analyze_batch(["valid transcript"])


@pytest.mark.asyncio
async def test_analyze_batch_raises_on_empty_llm_action_items():
    service, llm, repository = _make_service()
    llm.run_completion_async = AsyncMock(
        return_value=TranscriptAnalysisDTO(summary="valid summary", action_items=[])
    )

    with pytest.raises(LLMOutputError, match="no action items"):
        await service.analyze_batch(["valid transcript"])
