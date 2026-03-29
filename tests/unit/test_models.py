"""Tests for Pydantic models."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from memory_system.models.memory import (
    MemoryCreate,
    MemoryCreateResponse,
    MemoryDetail,
    MemorySearchRequest,
    MemorySearchResult,
    MemoryStats,
)


class TestMemoryCreate:
    def test_valid_content(self) -> None:
        m = MemoryCreate(content="Hello world")
        assert m.content == "Hello world"
        assert m.memory_type == "episodic"
        assert m.context is None

    def test_empty_content_rejected(self) -> None:
        with pytest.raises(Exception):
            MemoryCreate(content="")

    def test_custom_type(self) -> None:
        m = MemoryCreate(content="test", memory_type="semantic")
        assert m.memory_type == "semantic"


class TestMemorySearchRequest:
    def test_defaults(self) -> None:
        r = MemorySearchRequest(query="test query")
        assert r.top_k == 7
        assert r.min_activation is None

    def test_custom_top_k(self) -> None:
        r = MemorySearchRequest(query="test", top_k=20)
        assert r.top_k == 20

    def test_top_k_bounds(self) -> None:
        with pytest.raises(Exception):
            MemorySearchRequest(query="test", top_k=0)
        with pytest.raises(Exception):
            MemorySearchRequest(query="test", top_k=200)


class TestMemoryCreateResponse:
    def test_serialization(self) -> None:
        r = MemoryCreateResponse(
            memory_id=uuid4(),
            activation=1.0,
            created_at=datetime.now(UTC),
        )
        data = r.model_dump()
        assert "memory_id" in data
        assert data["activation"] == 1.0


class TestMemorySearchResult:
    def test_all_fields(self) -> None:
        r = MemorySearchResult(
            memory_id=uuid4(),
            content="test content",
            activation=0.85,
            similarity=0.92,
            last_accessed=datetime.now(UTC),
            access_count=5,
        )
        assert r.activation == 0.85
        assert r.similarity == 0.92


class TestMemoryStats:
    def test_stats(self) -> None:
        s = MemoryStats(total=100, active=80, decayed=15, deleted=5, avg_activation=0.65)
        assert s.total == 100
        assert s.active + s.decayed + s.deleted == 100


class TestMemoryDetail:
    def test_full_detail(self) -> None:
        d = MemoryDetail(
            memory_id=uuid4(),
            content="detailed memory",
            memory_type="episodic",
            created_at=datetime.now(UTC),
            last_accessed=datetime.now(UTC),
            access_count=3,
            activation=0.75,
            salience=0.5,
            emotion_valence=0.0,
            emotion_arousal=0.3,
            decay_rate=0.5,
            status="active",
            access_history=[],
        )
        assert d.status == "active"
        assert len(d.access_history) == 0
