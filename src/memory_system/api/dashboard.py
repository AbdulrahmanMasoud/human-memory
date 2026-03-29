"""FastAPI router for dashboard data endpoints."""

from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter(tags=["dashboard"])


@router.get("/v1/memories")
async def list_memories(
    request: Request,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, object]:
    """List all memories (any status) with pagination."""
    service = request.app.state.memory_service
    memories = await service.pg.get_all_memories(offset=offset, limit=limit)
    return {
        "memories": [
            {
                "memory_id": str(m.memory_id),
                "content": m.content[:200],
                "memory_type": m.memory_type,
                "activation": m.activation,
                "salience": m.salience,
                "status": m.status,
                "access_count": m.access_count,
                "created_at": m.created_at.isoformat(),
                "last_accessed": m.last_accessed.isoformat(),
            }
            for m in memories
        ],
        "offset": offset,
        "limit": limit,
    }


@router.get("/v1/graph/export")
async def export_graph(
    request: Request,
    limit: int = Query(default=200, ge=1, le=1000),
) -> dict[str, object]:
    """Export full knowledge graph for D3 visualization."""
    neo4j = getattr(request.app.state, "neo4j_store", None)
    if neo4j is None:
        raise HTTPException(status_code=503, detail="Neo4j not available")
    return await neo4j.get_full_graph(limit=limit)
