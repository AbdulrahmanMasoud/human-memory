"""Neo4j knowledge graph store adapter for semantic memory."""

import logging

from neo4j import AsyncGraphDatabase, AsyncDriver

logger = logging.getLogger(__name__)


class Neo4jStore:
    """Thin adapter for knowledge graph operations in Neo4j."""

    def __init__(self, uri: str, user: str, password: str) -> None:
        self._driver: AsyncDriver = AsyncGraphDatabase.driver(
            uri, auth=(user, password)
        )

    async def close(self) -> None:
        await self._driver.close()

    async def verify_connectivity(self) -> bool:
        try:
            await self._driver.verify_connectivity()
            return True
        except Exception:
            logger.warning("Neo4j not available — spreading activation disabled")
            return False

    async def create_concept(
        self, name: str, type: str = "concept", activation: float = 0.8
    ) -> dict[str, object]:
        """Create or update a concept node."""
        query = """
        MERGE (c:Concept {name: $name})
        SET c.type = $type, c.activation = $activation
        RETURN c.name AS name, c.type AS type, c.activation AS activation
        """
        async with self._driver.session() as session:
            result = await session.run(query, name=name, type=type, activation=activation)
            record = await result.single()
            return dict(record) if record else {}

    async def create_relation(
        self, source: str, target: str, relation_type: str, weight: float = 1.0
    ) -> dict[str, object]:
        """Create a typed relationship between concepts."""
        query = f"""
        MATCH (s:Concept {{name: $source}})
        MATCH (t:Concept {{name: $target}})
        MERGE (s)-[r:{relation_type}]->(t)
        SET r.weight = $weight
        RETURN s.name AS source, t.name AS target, type(r) AS relation_type, r.weight AS weight
        """
        async with self._driver.session() as session:
            result = await session.run(query, source=source, target=target, weight=weight)
            record = await result.single()
            return dict(record) if record else {}

    async def get_concept(self, name: str) -> dict[str, object] | None:
        """Get a concept with its relationships."""
        query = """
        MATCH (c:Concept {name: $name})
        OPTIONAL MATCH (c)-[r]-(other:Concept)
        RETURN c.name AS name, c.type AS type, c.activation AS activation,
               collect({target: other.name, type: type(r), weight: r.weight}) AS relations
        """
        async with self._driver.session() as session:
            result = await session.run(query, name=name)
            record = await result.single()
            if record is None:
                return None
            return dict(record)

    async def spreading_activation(
        self, active_concepts: list[str], depth: int = 2, limit: int = 10
    ) -> list[dict[str, object]]:
        """Compute spreading activation from active concepts.

        Returns related concepts sorted by accumulated spread weight.
        S_i = Σ W_k × S_ki where W_k = 1/N (equal attention).
        """
        if not active_concepts:
            return []

        # Neo4j doesn't allow parameterized path length, so we inject it safely
        safe_depth = max(1, min(int(depth), 4))
        query = f"""
        UNWIND $active_concepts AS source_name
        MATCH (source:Concept {{name: source_name}})-[r*1..{safe_depth}]-(target:Concept)
        WHERE NOT target.name IN $active_concepts
        WITH target,
             sum(reduce(w = 1.0, rel IN r | w * rel.weight) * (1.0 / $context_size)) AS spread
        RETURN target.name AS name, target.activation AS activation, spread AS path_weight
        ORDER BY path_weight DESC
        LIMIT $limit
        """
        async with self._driver.session() as session:
            result = await session.run(
                query,
                active_concepts=active_concepts,
                context_size=len(active_concepts),
                limit=limit,
            )
            records = [dict(r) async for r in result]
            return records

    async def search_graph(
        self, concept: str, depth: int = 2
    ) -> list[dict[str, object]]:
        """Traverse the graph from a starting concept."""
        safe_depth = max(1, min(int(depth), 4))
        query = f"""
        MATCH (start:Concept {{name: $concept}})-[r*1..{safe_depth}]-(related:Concept)
        RETURN related.name AS name, related.type AS type, related.activation AS activation,
               reduce(w = 1.0, rel IN r | w * rel.weight) AS path_weight
        ORDER BY path_weight DESC
        """
        async with self._driver.session() as session:
            result = await session.run(query, concept=concept)
            return [dict(r) async for r in result]

    async def store_extracted_fact(
        self, fact: str, confidence: float, source_episode_ids: list[str]
    ) -> dict[str, object]:
        """Store an extracted semantic fact with links to source episodes."""
        query = """
        MERGE (f:Concept {name: $fact})
        SET f.type = 'fact', f.activation = $confidence, f.confidence = $confidence
        WITH f
        UNWIND $source_ids AS ep_id
        MERGE (ep:Episode {id: ep_id})
        MERGE (f)-[r:EXTRACTED_FROM]->(ep)
        SET r.weight = $confidence
        RETURN f.name AS name, f.activation AS activation
        """
        async with self._driver.session() as session:
            result = await session.run(
                query, fact=fact, confidence=confidence, source_ids=source_episode_ids
            )
            record = await result.single()
            return dict(record) if record else {}
