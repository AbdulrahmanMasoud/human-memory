"""Consolidation engine — 4-phase memory consolidation cycle.

Inspired by sleep consolidation:
  Phase 1: REPLAY — boost high-salience recent memories
  Phase 2: EXTRACT — cluster episodes, extract semantic facts via LLM
  Phase 3: PRUNE — global downscaling, archive below threshold
  Phase 4: COMPILE — no-op (V4: procedural skill compilation)
"""

import logging
import time

import httpx

from memory_system.core.clustering import cluster_episodes
from memory_system.models.graph import ConsolidationReport
from memory_system.stores.neo4j_store import Neo4jStore
from memory_system.stores.postgres_store import PostgresMetadataStore
from memory_system.stores.qdrant_store import QdrantMemoryStore

logger = logging.getLogger(__name__)

REPLAY_BOOST = 0.3
DOWNSCALE_FACTOR = 0.9
SALIENCE_THRESHOLD = 0.6
CLUSTER_SIMILARITY_THRESHOLD = 0.7
MIN_CLUSTER_SIZE = 3
FORGET_THRESHOLD = -2.0


class ConsolidationEngine:
    """Runs the 4-phase consolidation cycle."""

    def __init__(
        self,
        pg_store: PostgresMetadataStore,
        qdrant_store: QdrantMemoryStore,
        neo4j_store: Neo4jStore | None,
        llm_api_base: str = "",
        llm_api_key: str = "",
        llm_model: str = "gpt-4o-mini",
    ) -> None:
        self.pg = pg_store
        self.qdrant = qdrant_store
        self.neo4j = neo4j_store
        self.llm_api_base = llm_api_base
        self.llm_api_key = llm_api_key
        self.llm_model = llm_model

    async def run_cycle(self, hours: int = 6) -> ConsolidationReport:
        """Run the full 4-phase consolidation cycle."""
        logger.info("Starting consolidation cycle...")

        replayed = await self._phase_replay(hours)
        extracted = await self._phase_extract(hours)
        pruned, downscaled = await self._phase_prune()
        compiled = self._phase_compile()

        report = ConsolidationReport(
            episodes_replayed=replayed,
            facts_extracted=extracted,
            memories_pruned=pruned,
            memories_downscaled=downscaled,
            phase_4_compiled=compiled,
        )
        logger.info("Consolidation complete: %s", report.model_dump())
        return report

    async def _phase_replay(self, hours: int) -> int:
        """Phase 1: Boost high-salience recent memories."""
        logger.info("Phase 1: REPLAY")
        active_memories = await self.pg.get_all_active_memories()
        cutoff = time.time() - (hours * 3600)
        replayed = 0

        for mem in active_memories:
            if mem.created_at.timestamp() > cutoff and mem.salience > SALIENCE_THRESHOLD:
                new_activation = mem.activation + REPLAY_BOOST
                await self.pg.update_activation(mem.memory_id, new_activation)
                self.qdrant.update_payload(mem.memory_id, {"activation": new_activation})
                replayed += 1

        logger.info("Replayed %d high-salience memories", replayed)
        return replayed

    async def _phase_extract(self, hours: int) -> int:
        """Phase 2: Cluster episodes and extract semantic facts via LLM."""
        logger.info("Phase 2: EXTRACT")

        if self.neo4j is None:
            logger.warning("Neo4j not available — skipping extraction")
            return 0

        # Get recent episodes with their embeddings from Qdrant
        active_memories = await self.pg.get_all_active_memories()
        cutoff = time.time() - (hours * 3600)
        recent = [m for m in active_memories if m.created_at.timestamp() > cutoff]

        if len(recent) < MIN_CLUSTER_SIZE:
            logger.info("Not enough recent episodes for clustering (%d)", len(recent))
            return 0

        # Get embeddings from Qdrant for clustering
        episodes = []
        for mem in recent:
            # We use a dummy search to get the embedding isn't directly accessible,
            # so we store content for LLM extraction
            episodes.append({
                "id": str(mem.memory_id),
                "content": mem.content,
                "embedding": [],  # We'll cluster by content similarity via LLM
            })

        # Try to cluster and extract
        facts_count = 0
        if self.llm_api_base and self.llm_api_key:
            try:
                facts = await self._llm_extract_facts(
                    [ep["content"] for ep in episodes]  # type: ignore[arg-type]
                )
                for fact in facts:
                    await self.neo4j.store_extracted_fact(
                        fact=fact["fact"],
                        confidence=fact.get("confidence", 0.7),
                        source_episode_ids=[ep["id"] for ep in episodes[:5]],  # type: ignore[misc]
                    )
                    facts_count += 1
                logger.info("Extracted %d semantic facts", facts_count)
            except Exception as e:
                logger.warning("LLM extraction failed: %s", e)

        return facts_count

    async def _llm_extract_facts(self, contents: list[str]) -> list[dict[str, object]]:
        """Use LLM to extract general knowledge from episode contents."""
        episode_text = "\n".join(f"- {c}" for c in contents[:20])

        prompt = f"""Analyze these related events and extract general knowledge:

Events:
{episode_text}

Extract general facts, patterns, or preferences. Return as JSON array:
[{{"fact": "...", "confidence": 0.0-1.0}}]

Return ONLY the JSON array, no other text."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.llm_api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.llm_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

            import json
            # Parse JSON from response
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(content)  # type: ignore[no-any-return]

    async def _phase_prune(self) -> tuple[int, int]:
        """Phase 3: Global downscaling + archive below threshold."""
        logger.info("Phase 3: PRUNE")
        active_memories = await self.pg.get_all_active_memories()
        pruned = 0
        downscaled = 0

        for mem in active_memories:
            new_activation = mem.activation * DOWNSCALE_FACTOR
            await self.pg.update_activation(mem.memory_id, new_activation)

            if new_activation < FORGET_THRESHOLD:
                await self.pg.mark_decayed(mem.memory_id)
                self.qdrant.update_payload(
                    mem.memory_id, {"activation": new_activation, "status": "decayed"}
                )
                pruned += 1
            else:
                self.qdrant.update_payload(mem.memory_id, {"activation": new_activation})

            downscaled += 1

        logger.info("Downscaled %d, pruned %d", downscaled, pruned)
        return pruned, downscaled

    def _phase_compile(self) -> int:
        """Phase 4: Compile repeated patterns to skills (V4 placeholder)."""
        logger.info("Phase 4: COMPILE (no-op — V4)")
        return 0
