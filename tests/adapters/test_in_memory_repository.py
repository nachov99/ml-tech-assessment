from app.adapters.in_memory_repository import InMemoryTranscriptRepository
from app.domain.models import TranscriptAnalysis


def test_save_and_get_by_id():
    repo = InMemoryTranscriptRepository()
    analysis = TranscriptAnalysis(
        id="abc-123",
        summary="Test summary",
        action_items=["action 1", "action 2"],
    )

    repo.save(analysis)
    result = repo.get_by_id("abc-123")

    assert result is not None
    assert result.id == "abc-123"
    assert result.summary == "Test summary"
    assert result.action_items == ["action 1", "action 2"]


def test_get_by_id_not_found():
    repo = InMemoryTranscriptRepository()

    result = repo.get_by_id("nonexistent")

    assert result is None


def test_save_overwrites_existing():
    repo = InMemoryTranscriptRepository()
    analysis_v1 = TranscriptAnalysis(id="abc-123", summary="v1", action_items=[])
    analysis_v2 = TranscriptAnalysis(id="abc-123", summary="v2", action_items=["new"])

    repo.save(analysis_v1)
    repo.save(analysis_v2)
    result = repo.get_by_id("abc-123")

    assert result.summary == "v2"
    assert result.action_items == ["new"]


def test_get_all_returns_all_saved():
    repo = InMemoryTranscriptRepository()
    a1 = TranscriptAnalysis(id="1", summary="s1", action_items=[])
    a2 = TranscriptAnalysis(id="2", summary="s2", action_items=[])

    repo.save(a1)
    repo.save(a2)
    results = repo.get_all()

    assert len(results) == 2
    ids = {r.id for r in results}
    assert ids == {"1", "2"}


def test_get_all_returns_empty_list():
    repo = InMemoryTranscriptRepository()

    results = repo.get_all()

    assert results == []