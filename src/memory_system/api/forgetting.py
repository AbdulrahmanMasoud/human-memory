"""FastAPI router for forgetting strategy operations."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/memories", tags=["forgetting"])


class ForgetStrategyRequest(BaseModel):
    """Request to apply a forgetting strategy."""

    strategy: str = Field(
        ...,
        description="One of: interference, rif, strategic_prune, capacity_overflow",
    )
    params: dict[str, object] = Field(
        default_factory=dict,
        description="Strategy-specific parameters (e.g., goals for strategic_prune)",
    )


class ForgetStrategyResponse(BaseModel):
    """Response from applying a forgetting strategy."""

    strategy: str
    memories_affected: int


@router.post("/forget-strategy", response_model=ForgetStrategyResponse)
async def apply_forget_strategy(
    body: ForgetStrategyRequest, request: Request
) -> ForgetStrategyResponse:
    """Apply a specific forgetting strategy."""
    from memory_system.core.forgetting import ForgettingEngine

    engine = ForgettingEngine()
    service = request.app.state.memory_service
    affected = 0

    if body.strategy == "strategic_prune":
        goals = body.params.get("goals", [])
        if isinstance(goals, list):
            active = await service.pg.get_all_active_memories()
            mems = [
                {"id": str(m.memory_id), "content": m.content, "activation": m.activation}
                for m in active
            ]
            updates = engine.compute_strategic_prune(mems, goals)  # type: ignore[arg-type]
            for mem_id, new_act in updates:
                import uuid

                await service.pg.update_activation(uuid.UUID(mem_id), new_act)
            affected = len(updates)

    elif body.strategy == "capacity_overflow":
        active = await service.pg.get_all_active_memories()
        mems = [{"id": str(m.memory_id), "activation": m.activation} for m in active]
        to_archive = engine.compute_capacity_overflow(mems)
        for mem_id in to_archive:
            import uuid

            await service.pg.mark_decayed(uuid.UUID(mem_id))
        affected = len(to_archive)

    return ForgetStrategyResponse(strategy=body.strategy, memories_affected=affected)
