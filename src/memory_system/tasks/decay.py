"""Celery task for batch decay update."""

import asyncio
import logging

from memory_system.celery_app import celery
from memory_system.config import settings
from memory_system.core.actr import ACTRMemory
from memory_system.core.embeddings import EmbeddingService
from memory_system.core.memory_service import MemoryService
from memory_system.stores.postgres_store import PostgresMetadataStore
from memory_system.stores.qdrant_store import QdrantMemoryStore

logger = logging.getLogger(__name__)


def _create_service() -> MemoryService:
    """Create a memory service instance for the worker."""
    pg_store = PostgresMetadataStore(dsn=settings.postgres_dsn)
    qdrant_store = QdrantMemoryStore(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
    )
    embedding_service = EmbeddingService(
        model_name=settings.embedding_model,
        embedding_dim=settings.embedding_dim,
    )
    actr = ACTRMemory(
        decay=settings.actr_decay_rate,
        noise_std=settings.actr_noise_std,
        threshold=settings.actr_retrieval_threshold,
    )
    return MemoryService(
        postgres_store=pg_store,
        qdrant_store=qdrant_store,
        embedding_service=embedding_service,
        actr=actr,
    )


@celery.task(name="memory_system.tasks.decay.batch_update_decay")
def batch_update_decay() -> dict[str, int]:
    """Batch recalculate activation for all active memories.

    Runs every 30 minutes via Celery Beat.
    Marks memories below threshold as decayed.
    """
    logger.info("Starting batch decay update...")
    service = _create_service()

    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(service.run_decay())
        logger.info(
            "Decay complete: %d processed, %d decayed",
            result.memories_processed,
            result.memories_decayed,
        )
        return {
            "memories_processed": result.memories_processed,
            "memories_decayed": result.memories_decayed,
        }
    finally:
        loop.run_until_complete(service.pg.close())
        service.qdrant.close()
        loop.close()
