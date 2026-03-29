"""FastAPI router for memory store/retrieve/recall/forget operations."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from memory_system.models.memory import (
    DecayResponse,
    DeleteResponse,
    MemoryCreate,
    MemoryCreateResponse,
    MemoryResponse,
    MemorySearchRequest,
    MemorySearchResponse,
)

router = APIRouter(prefix="/v1/memories", tags=["memories"])


def _get_service(request: Request):  # type: ignore[no-untyped-def]
    return request.app.state.memory_service


@router.post("", response_model=MemoryCreateResponse, status_code=201)
async def store_memory(body: MemoryCreate, request: Request) -> MemoryCreateResponse:
    """Store a new episodic memory."""
    service = _get_service(request)
    return await service.store(
        content=body.content,
        memory_type=body.memory_type,
        context=body.context,
    )


@router.post("/search", response_model=MemorySearchResponse)
async def search_memories(body: MemorySearchRequest, request: Request) -> MemorySearchResponse:
    """Retrieve memories by semantic query with ACT-R activation ranking."""
    service = _get_service(request)
    return await service.retrieve(
        query=body.query,
        top_k=body.top_k,
        min_activation=body.min_activation,
    )


@router.get("/{memory_id}", response_model=MemoryResponse)
async def recall_memory(memory_id: UUID, request: Request) -> MemoryResponse:
    """Recall a specific memory by ID. Also records an access event."""
    service = _get_service(request)
    result = await service.recall(memory_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Memory not found or decayed")
    return result


@router.delete("/{memory_id}", response_model=DeleteResponse)
async def forget_memory(memory_id: UUID, request: Request) -> DeleteResponse:
    """Soft-delete (forget) a memory."""
    service = _get_service(request)
    deleted = await service.forget(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return DeleteResponse(memory_id=memory_id, deleted=True)


@router.post("/decay", response_model=DecayResponse)
async def trigger_decay(request: Request) -> DecayResponse:
    """Manually trigger the decay process."""
    service = _get_service(request)
    return await service.run_decay()
