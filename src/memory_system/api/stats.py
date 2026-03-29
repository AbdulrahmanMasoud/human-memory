"""FastAPI router for system statistics and memory inspection."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from memory_system.models.memory import MemoryDetail, MemoryStats

router = APIRouter(tags=["stats"])


def _get_service(request: Request):  # type: ignore[no-untyped-def]
    return request.app.state.memory_service


@router.get("/v1/stats", response_model=MemoryStats)
async def get_stats(request: Request) -> MemoryStats:
    """Get system-wide memory statistics."""
    service = _get_service(request)
    return await service.stats()


@router.get("/v1/memories/{memory_id}/inspect", response_model=MemoryDetail)
async def inspect_memory(memory_id: UUID, request: Request) -> MemoryDetail:
    """Get full metadata and access history for a memory."""
    service = _get_service(request)
    result = await service.inspect(memory_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return result
