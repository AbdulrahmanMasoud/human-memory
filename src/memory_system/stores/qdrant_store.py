"""Qdrant vector database store adapter."""

import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    UpdateResult,
    VectorParams,
)


class QdrantMemoryStore:
    """Thin adapter for vector operations in Qdrant."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "episodic_memories",
        vector_size: int = 384,
    ) -> None:
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.vector_size = vector_size

    def ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )

    def upsert_memory(
        self,
        memory_id: uuid.UUID,
        vector: list[float],
        content: str,
        memory_type: str = "episodic",
        activation: float = 1.0,
        timestamp: float = 0.0,
    ) -> UpdateResult:
        """Store or update a memory vector with payload."""
        return self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=str(memory_id),
                    vector=vector,
                    payload={
                        "content": content,
                        "memory_type": memory_type,
                        "status": "active",
                        "activation": activation,
                        "timestamp": timestamp,
                    },
                )
            ],
        )

    def search(
        self,
        query_vector: list[float],
        limit: int = 21,
        status: str = "active",
    ) -> list[dict[str, object]]:
        """Search for similar memories, filtered by status.

        Uses query_points (Qdrant v1.13+ API).
        Returns list of dicts with: id, score (cosine similarity), payload.
        """
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=Filter(
                must=[FieldCondition(key="status", match=MatchValue(value=status))]
            ),
            limit=limit,
        )
        return [
            {
                "id": r.id,
                "score": r.score,
                "payload": r.payload,
            }
            for r in results.points
        ]

    def update_payload(self, memory_id: uuid.UUID, payload: dict[str, object]) -> None:
        """Update payload fields for a point."""
        self.client.set_payload(
            collection_name=self.collection_name,
            payload=payload,
            points=[str(memory_id)],
        )

    def delete(self, memory_id: uuid.UUID) -> None:
        """Delete a point from the collection."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[str(memory_id)],
        )

    def close(self) -> None:
        """Close the client connection."""
        self.client.close()
