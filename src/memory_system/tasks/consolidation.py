"""Celery task for periodic consolidation cycle."""

import asyncio
import logging

from memory_system.celery_app import celery
from memory_system.config import settings
from memory_system.core.consolidation import ConsolidationEngine
from memory_system.stores.neo4j_store import Neo4jStore
from memory_system.stores.postgres_store import PostgresMetadataStore
from memory_system.stores.qdrant_store import QdrantMemoryStore

logger = logging.getLogger(__name__)


@celery.task(name="memory_system.tasks.consolidation.run_consolidation")
def run_consolidation() -> dict[str, int]:
    """Run the 4-phase consolidation cycle.

    Runs every 6 hours via Celery Beat.
    """
    logger.info("Starting scheduled consolidation...")

    pg_store = PostgresMetadataStore(dsn=settings.postgres_dsn)
    qdrant_store = QdrantMemoryStore(host=settings.qdrant_host, port=settings.qdrant_port)

    neo4j_store: Neo4jStore | None = None
    try:
        neo4j_store = Neo4jStore(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password,
        )
    except Exception as e:
        logger.warning("Neo4j not available for consolidation: %s", e)

    engine = ConsolidationEngine(
        pg_store=pg_store,
        qdrant_store=qdrant_store,
        neo4j_store=neo4j_store,
        llm_api_base=settings.llm_api_base,
        llm_api_key=settings.embedding_api_key,  # reuse embedding API key
        llm_model=settings.llm_model,
    )

    loop = asyncio.new_event_loop()
    try:
        report = loop.run_until_complete(engine.run_cycle())
        return report.model_dump()
    finally:
        if neo4j_store:
            loop.run_until_complete(neo4j_store.close())
        loop.run_until_complete(pg_store.close())
        qdrant_store.close()
        loop.close()
