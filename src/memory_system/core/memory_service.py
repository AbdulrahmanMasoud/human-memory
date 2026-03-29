"""Memory service — orchestrates stores and ACT-R retrieval pipeline."""

import time
import uuid

from memory_system.core.actr import ACTRMemory
from memory_system.core.embeddings import EmbeddingService
from memory_system.models.memory import (
    AccessRecord,
    DecayResponse,
    MemoryCreateResponse,
    MemoryDetail,
    MemoryResponse,
    MemorySearchResponse,
    MemorySearchResult,
    MemoryStats,
)
from memory_system.stores.postgres_store import PostgresMetadataStore
from memory_system.stores.qdrant_store import QdrantMemoryStore


class MemoryService:
    """Orchestrates the memory retrieval pipeline using ACT-R activation."""

    def __init__(
        self,
        postgres_store: PostgresMetadataStore,
        qdrant_store: QdrantMemoryStore,
        embedding_service: EmbeddingService,
        actr: ACTRMemory,
    ) -> None:
        self.pg = postgres_store
        self.qdrant = qdrant_store
        self.embeddings = embedding_service
        self.actr = actr

    async def store(
        self,
        content: str,
        memory_type: str = "episodic",
        context: str | None = None,
    ) -> MemoryCreateResponse:
        """Store a new memory (FR-001)."""
        memory_id = uuid.uuid4()
        now = time.time()

        # Generate embedding
        vector = self.embeddings.embed(content)

        # Store metadata in PostgreSQL
        mem = await self.pg.create_memory(
            content=content,
            memory_type=memory_type,
            memory_id=memory_id,
        )

        # Store vector in Qdrant
        self.qdrant.upsert_memory(
            memory_id=memory_id,
            vector=vector,
            content=content,
            memory_type=memory_type,
            activation=mem.activation,
            timestamp=now,
        )

        return MemoryCreateResponse(
            memory_id=mem.memory_id,
            activation=mem.activation,
            created_at=mem.created_at,
        )

    async def retrieve(
        self,
        query: str,
        top_k: int = 7,
        min_activation: float | None = None,
    ) -> MemorySearchResponse:
        """Retrieve memories using ACT-R activation pipeline (FR-002, FR-003).

        Pipeline:
        1. Embed query → Qdrant search (top_k * 3 candidates)
        2. Fetch access history from PostgreSQL
        3. Compute ACT-R activation for each candidate
        4. Filter by threshold, sort, take top_k
        5. Record access events for returned memories
        """
        threshold = min_activation if min_activation is not None else self.actr.threshold
        current_time = time.time()

        # Step 1: Embed and search Qdrant for candidates
        query_vector = self.embeddings.embed(query)
        candidates = self.qdrant.search(query_vector, limit=top_k * 3)

        if not candidates:
            return MemorySearchResponse(results=[], count=0)

        # Step 2-3: Compute ACT-R activation for each candidate
        scored: list[tuple[dict[str, object], float, float]] = []
        for candidate in candidates:
            memory_id = uuid.UUID(str(candidate["id"]))
            similarity = float(candidate["score"])  # type: ignore[arg-type]

            # Fetch access history from PostgreSQL
            access_times = await self.pg.get_access_times(memory_id)

            # Compute total activation (V1: only B_i + ε)
            activation = self.actr.total_activation(
                access_times=access_times,
                current_time=current_time,
                include_noise=True,
            )

            if activation > threshold:
                scored.append((candidate, activation, similarity))

        # Step 4: Sort by activation, take top_k
        scored.sort(key=lambda x: x[1], reverse=True)
        top_results = scored[:top_k]

        # Step 5: Record access events and build response
        results: list[MemorySearchResult] = []
        for candidate, activation, similarity in top_results:
            memory_id = uuid.UUID(str(candidate["id"]))

            # Record access (FR-006)
            await self.pg.record_access(memory_id, context="search_retrieval")

            # Fetch metadata for response
            mem = await self.pg.get_memory(memory_id)
            if mem is None:
                continue

            results.append(
                MemorySearchResult(
                    memory_id=mem.memory_id,
                    content=mem.content,
                    activation=activation,
                    similarity=similarity,
                    last_accessed=mem.last_accessed,
                    access_count=mem.access_count,
                )
            )

        return MemorySearchResponse(results=results, count=len(results))

    async def recall(self, memory_id: uuid.UUID) -> MemoryResponse | None:
        """Direct recall by ID (FR-007). Also records access."""
        mem = await self.pg.get_active_memory(memory_id)
        if mem is None:
            return None

        # Record access
        await self.pg.record_access(memory_id, context="direct_recall")

        # Refresh to get updated access count
        mem = await self.pg.get_memory(memory_id)
        if mem is None:
            return None

        return MemoryResponse(
            memory_id=mem.memory_id,
            content=mem.content,
            activation=mem.activation,
            memory_type=mem.memory_type,
            created_at=mem.created_at,
            last_accessed=mem.last_accessed,
            access_count=mem.access_count,
        )

    async def forget(self, memory_id: uuid.UUID) -> bool:
        """Soft-delete a memory (FR-008)."""
        deleted = await self.pg.delete_memory(memory_id)
        if deleted:
            self.qdrant.update_payload(memory_id, {"status": "deleted"})
        return deleted

    async def inspect(self, memory_id: uuid.UUID) -> MemoryDetail | None:
        """Full memory inspection (FR-010)."""
        mem = await self.pg.get_memory(memory_id)
        if mem is None:
            return None

        access_records = await self.pg.get_access_history(memory_id)

        return MemoryDetail(
            memory_id=mem.memory_id,
            content=mem.content,
            memory_type=mem.memory_type,
            created_at=mem.created_at,
            last_accessed=mem.last_accessed,
            access_count=mem.access_count,
            activation=mem.activation,
            salience=mem.salience,
            emotion_valence=mem.emotion_valence,
            emotion_arousal=mem.emotion_arousal,
            decay_rate=mem.decay_rate,
            status=mem.status,
            access_history=[
                AccessRecord(accessed_at=ar.accessed_at, context=ar.context)
                for ar in access_records
            ],
        )

    async def stats(self) -> MemoryStats:
        """Get system-wide statistics (FR-009)."""
        raw = await self.pg.get_stats()
        return MemoryStats(
            total=raw["total"],  # type: ignore[arg-type]
            active=raw["active"],  # type: ignore[arg-type]
            decayed=raw["decayed"],  # type: ignore[arg-type]
            deleted=raw["deleted"],  # type: ignore[arg-type]
            avg_activation=raw["avg_activation"],  # type: ignore[arg-type]
        )

    async def run_decay(self) -> DecayResponse:
        """Run batch decay update (FR-004, FR-005, FR-012).

        For each active memory:
        1. Fetch access history (capped at 1000, FR-011)
        2. Recompute B_i
        3. Update activation in both PostgreSQL and Qdrant
        4. Mark as decayed if below threshold
        """
        current_time = time.time()
        active_memories = await self.pg.get_all_active_memories()
        processed = 0
        decayed = 0

        for mem in active_memories:
            access_times = await self.pg.get_access_times(mem.memory_id, limit=1000)

            # Recompute activation (no noise during decay — deterministic)
            activation = self.actr.total_activation(
                access_times=access_times,
                current_time=current_time,
                include_noise=False,
            )

            # Update PostgreSQL
            await self.pg.update_activation(mem.memory_id, activation)

            # Update Qdrant payload
            payload_update: dict[str, object] = {"activation": activation}

            if not self.actr.can_retrieve(activation):
                await self.pg.mark_decayed(mem.memory_id)
                payload_update["status"] = "decayed"
                decayed += 1

            self.qdrant.update_payload(mem.memory_id, payload_update)
            processed += 1

        return DecayResponse(memories_processed=processed, memories_decayed=decayed)
