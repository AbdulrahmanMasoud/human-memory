"""PostgreSQL store for procedural memory (compiled skills)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Float, Integer, String, Text, select, update
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from memory_system.models.database import Base
from memory_system.stores.postgres_store import PostgresMetadataStore


class ProceduralSkill(Base):
    """Compiled skill from repeated successful patterns."""

    __tablename__ = "procedural_skills"

    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    preconditions: Mapped[dict] = mapped_column(JSONB, default=dict)  # type: ignore[type-arg]
    action_pattern: Mapped[dict] = mapped_column(JSONB, default=dict)  # type: ignore[type-arg]
    success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    compiled_from: Mapped[list] = mapped_column(JSONB, default=list)  # type: ignore[type-arg]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ProceduralStore:
    """Adapter for procedural skill operations."""

    def __init__(self, pg_store: PostgresMetadataStore) -> None:
        self.session_factory = pg_store.session_factory

    async def store_skill(
        self,
        name: str,
        preconditions: dict[str, object],
        action_pattern: dict[str, object],
        success_rate: float,
        source_episode_ids: list[str],
    ) -> ProceduralSkill:
        """Store a new compiled skill."""
        skill = ProceduralSkill(
            name=name,
            preconditions=preconditions,
            action_pattern=action_pattern,
            success_rate=success_rate,
            execution_count=1,
            compiled_from=source_episode_ids,
        )
        async with self.session_factory() as session:
            session.add(skill)
            await session.commit()
            await session.refresh(skill)
        return skill

    async def get_skill(self, skill_id: uuid.UUID) -> ProceduralSkill | None:
        """Get a skill by ID."""
        async with self.session_factory() as session:
            return await session.get(ProceduralSkill, skill_id)

    async def get_all_skills(self) -> list[ProceduralSkill]:
        """Get all procedural skills."""
        async with self.session_factory() as session:
            result = await session.execute(select(ProceduralSkill))
            return list(result.scalars().all())

    async def increment_execution(self, skill_id: uuid.UUID) -> None:
        """Increment skill execution count."""
        async with self.session_factory() as session:
            stmt = (
                update(ProceduralSkill)
                .where(ProceduralSkill.skill_id == skill_id)
                .values(execution_count=ProceduralSkill.execution_count + 1)
            )
            await session.execute(stmt)
            await session.commit()
