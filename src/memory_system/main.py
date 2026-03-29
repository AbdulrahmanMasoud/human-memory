"""FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request

from memory_system.api.forgetting import router as forgetting_router
from memory_system.api.graph import router as graph_router
from memory_system.api.memories import router as memories_router
from memory_system.api.stats import router as stats_router
from memory_system.config import settings
from memory_system.core.actr import ACTRMemory
from memory_system.core.consolidation import ConsolidationEngine
from memory_system.core.embeddings import EmbeddingService
from memory_system.core.memory_service import MemoryService
from memory_system.stores.neo4j_store import Neo4jStore
from memory_system.stores.postgres_store import PostgresMetadataStore
from memory_system.stores.qdrant_store import QdrantMemoryStore

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize stores and models on startup, cleanup on shutdown."""
    logger.info("Starting Human-Like Memory System...")

    # Initialize embedding service (external API)
    embedding_service = EmbeddingService(
        api_base=settings.embedding_api_base,
        api_key=settings.embedding_api_key,
        model=settings.embedding_model,
        embedding_dim=settings.embedding_dim,
    )
    embedding_service.load()
    logger.info("Embedding service initialized")

    # Initialize stores
    pg_store = PostgresMetadataStore(dsn=settings.postgres_dsn)
    qdrant_store = QdrantMemoryStore(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        vector_size=settings.embedding_dim,
    )
    qdrant_store.ensure_collection()
    logger.info("PostgreSQL and Qdrant stores initialized")

    # Initialize Neo4j (optional — graceful fallback if unavailable)
    neo4j_store: Neo4jStore | None = None
    try:
        neo4j_store = Neo4jStore(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password,
        )
        if await neo4j_store.verify_connectivity():
            logger.info("Neo4j connected")
        else:
            neo4j_store = None
    except Exception as e:
        logger.warning("Neo4j not available: %s — spreading activation disabled", e)
        neo4j_store = None

    # Initialize ACT-R engine
    actr = ACTRMemory(
        decay=settings.actr_decay_rate,
        noise_std=settings.actr_noise_std,
        threshold=settings.actr_retrieval_threshold,
    )

    # Create memory service
    memory_service = MemoryService(
        postgres_store=pg_store,
        qdrant_store=qdrant_store,
        embedding_service=embedding_service,
        actr=actr,
    )

    # Create consolidation engine
    consolidation_engine = ConsolidationEngine(
        pg_store=pg_store,
        qdrant_store=qdrant_store,
        neo4j_store=neo4j_store,
        llm_api_base=settings.llm_api_base,
        llm_api_key=settings.embedding_api_key,
        llm_model=settings.llm_model,
    )

    # Attach to app state
    app.state.memory_service = memory_service
    app.state.neo4j_store = neo4j_store
    app.state.consolidation_engine = consolidation_engine

    yield

    # Cleanup
    embedding_service.close()
    if neo4j_store:
        await neo4j_store.close()
    await pg_store.close()
    qdrant_store.close()
    logger.info("Memory system shut down")


app = FastAPI(
    title="Human-Like Memory System",
    description=(
        "ACT-R cognitive architecture based memory system for AI agents. "
        "Implements episodic, semantic, and procedural memory with "
        "biologically-inspired forgetting and consolidation."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(memories_router)
app.include_router(stats_router)
app.include_router(graph_router)
app.include_router(forgetting_router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Liveness check — returns ok if the app process is running."""
    return {"status": "ok"}


@app.get("/ready", tags=["system"])
async def ready(request: Request) -> dict[str, object]:
    """Readiness check — verifies all backend connections."""
    checks: dict[str, str] = {}

    # PostgreSQL
    try:
        service = request.app.state.memory_service
        await service.pg.get_stats()
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {e}"

    # Qdrant
    try:
        service = request.app.state.memory_service
        service.qdrant.client.get_collections()
        checks["qdrant"] = "ok"
    except Exception as e:
        checks["qdrant"] = f"error: {e}"

    # Neo4j (optional)
    neo4j = getattr(request.app.state, "neo4j_store", None)
    if neo4j:
        try:
            await neo4j.verify_connectivity()
            checks["neo4j"] = "ok"
        except Exception as e:
            checks["neo4j"] = f"error: {e}"
    else:
        checks["neo4j"] = "not configured"

    all_ok = all(v == "ok" for k, v in checks.items() if k != "neo4j")
    return {"status": "ready" if all_ok else "degraded", "checks": checks}
