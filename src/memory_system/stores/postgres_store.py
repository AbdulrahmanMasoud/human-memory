"""PostgreSQL metadata store adapter."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from memory_system.models.database import AccessHistory, MemoryMetadata


class PostgresMetadataStore:
    """Thin adapter for memory metadata operations in PostgreSQL."""

    def __init__(self, dsn: str) -> None:
        self.engine = create_async_engine(dsn, pool_size=10, max_overflow=20)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def close(self) -> None:
        await self.engine.dispose()

    async def create_memory(
        self,
        content: str,
        memory_type: str = "episodic",
        memory_id: uuid.UUID | None = None,
    ) -> MemoryMetadata:
        """Insert a new memory metadata record."""
        now = datetime.now(UTC)
        mem = MemoryMetadata(
            memory_id=memory_id or uuid.uuid4(),
            memory_type=memory_type,
            content=content,
            created_at=now,
            last_accessed=now,
        )
        async with self.session_factory() as session:
            session.add(mem)
            # Also add initial access record
            access = AccessHistory(
                memory_id=mem.memory_id,
                accessed_at=now,
                context="initial_store",
            )
            session.add(access)
            await session.commit()
            await session.refresh(mem)
        return mem

    async def get_memory(self, memory_id: uuid.UUID) -> MemoryMetadata | None:
        """Fetch a single memory by ID."""
        async with self.session_factory() as session:
            result = await session.get(MemoryMetadata, memory_id)
            return result

    async def get_active_memory(self, memory_id: uuid.UUID) -> MemoryMetadata | None:
        """Fetch a memory only if its status is 'active'."""
        async with self.session_factory() as session:
            stmt = select(MemoryMetadata).where(
                MemoryMetadata.memory_id == memory_id,
                MemoryMetadata.status == "active",
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def record_access(self, memory_id: uuid.UUID, context: str | None = None) -> None:
        """Record an access event and update metadata."""
        now = datetime.now(UTC)
        async with self.session_factory() as session:
            # Update metadata
            stmt = (
                update(MemoryMetadata)
                .where(MemoryMetadata.memory_id == memory_id)
                .values(
                    last_accessed=now,
                    access_count=MemoryMetadata.access_count + 1,
                )
            )
            await session.execute(stmt)

            # Add access record
            access = AccessHistory(memory_id=memory_id, accessed_at=now, context=context)
            session.add(access)
            await session.commit()

    async def get_access_times(self, memory_id: uuid.UUID, limit: int = 1000) -> list[float]:
        """Get access timestamps as epoch seconds, most recent first."""
        async with self.session_factory() as session:
            stmt = (
                select(AccessHistory.accessed_at)
                .where(AccessHistory.memory_id == memory_id)
                .order_by(AccessHistory.accessed_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [dt.timestamp() for dt in rows]

    async def get_access_history(
        self, memory_id: uuid.UUID, limit: int = 1000
    ) -> list[AccessHistory]:
        """Get full access history records."""
        async with self.session_factory() as session:
            stmt = (
                select(AccessHistory)
                .where(AccessHistory.memory_id == memory_id)
                .order_by(AccessHistory.accessed_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def update_activation(self, memory_id: uuid.UUID, activation: float) -> None:
        """Update a memory's activation score."""
        async with self.session_factory() as session:
            stmt = (
                update(MemoryMetadata)
                .where(MemoryMetadata.memory_id == memory_id)
                .values(activation=activation)
            )
            await session.execute(stmt)
            await session.commit()

    async def mark_decayed(self, memory_id: uuid.UUID) -> None:
        """Mark a memory as decayed."""
        async with self.session_factory() as session:
            stmt = (
                update(MemoryMetadata)
                .where(MemoryMetadata.memory_id == memory_id)
                .values(status="decayed")
            )
            await session.execute(stmt)
            await session.commit()

    async def delete_memory(self, memory_id: uuid.UUID) -> bool:
        """Soft-delete a memory (set status to 'deleted')."""
        async with self.session_factory() as session:
            stmt = (
                update(MemoryMetadata)
                .where(
                    MemoryMetadata.memory_id == memory_id,
                    MemoryMetadata.status != "deleted",
                )
                .values(status="deleted")
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0  # type: ignore[return-value]

    async def get_all_active_memories(self) -> list[MemoryMetadata]:
        """Get all memories with status 'active'."""
        async with self.session_factory() as session:
            stmt = select(MemoryMetadata).where(MemoryMetadata.status == "active")
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_stats(self) -> dict[str, int | float]:
        """Get aggregate statistics."""
        async with self.session_factory() as session:
            # Total by status
            total_stmt = select(
                MemoryMetadata.status, func.count(MemoryMetadata.memory_id)
            ).group_by(MemoryMetadata.status)
            result = await session.execute(total_stmt)
            counts: dict[str, int] = {}
            for status, count in result.all():
                counts[status] = count

            # Average activation of active memories
            avg_stmt = select(func.avg(MemoryMetadata.activation)).where(
                MemoryMetadata.status == "active"
            )
            avg_result = await session.execute(avg_stmt)
            avg_activation = avg_result.scalar() or 0.0

            return {
                "total": sum(counts.values()),
                "active": counts.get("active", 0),
                "decayed": counts.get("decayed", 0),
                "deleted": counts.get("deleted", 0),
                "avg_activation": float(avg_activation),
            }
