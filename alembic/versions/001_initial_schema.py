"""Initial schema: memory_metadata and access_history tables.

Revision ID: 001
Revises: None
Create Date: 2026-03-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "memory_metadata",
        sa.Column("memory_id", UUID(as_uuid=True), primary_key=True),
        sa.Column("memory_type", sa.String(20), server_default="episodic"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("last_accessed", TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("access_count", sa.Integer(), server_default="1"),
        sa.Column("activation", sa.Float(), server_default="1.0"),
        sa.Column("salience", sa.Float(), server_default="0.5"),
        sa.Column("emotion_valence", sa.Float(), server_default="0.0"),
        sa.Column("emotion_arousal", sa.Float(), server_default="0.3"),
        sa.Column("decay_rate", sa.Float(), server_default="0.5"),
        sa.Column("status", sa.String(20), server_default="active"),
    )

    op.create_index(
        "idx_memory_activation_active",
        "memory_metadata",
        ["activation"],
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index("idx_memory_last_accessed", "memory_metadata", ["last_accessed"])
    op.create_index("idx_memory_status", "memory_metadata", ["status"])

    op.create_table(
        "access_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "memory_id",
            UUID(as_uuid=True),
            sa.ForeignKey("memory_metadata.memory_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("accessed_at", TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("context", sa.Text(), nullable=True),
    )

    op.create_index(
        "idx_access_history_memory_time",
        "access_history",
        ["memory_id", "accessed_at"],
    )


def downgrade() -> None:
    op.drop_table("access_history")
    op.drop_table("memory_metadata")
