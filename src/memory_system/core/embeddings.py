"""Embedding service via external API (OpenAI-compatible).

Supports any OpenAI-compatible embedding endpoint:
- OpenAI (api.openai.com)
- Anthropic (via proxy)
- Ollama (localhost:11434)
- vLLM, LiteLLM, etc.

Falls back to a hash-based deterministic vector if no API key is configured.
"""

import hashlib
import logging
import math

import httpx

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generates text embeddings via an external API."""

    def __init__(
        self,
        api_base: str = "https://api.openai.com/v1",
        api_key: str = "",
        model: str = "text-embedding-3-small",
        embedding_dim: int = 1536,
    ) -> None:
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.embedding_dim = embedding_dim
        self._client: httpx.Client | None = None
        self._available = False

    def load(self) -> None:
        """Initialize the HTTP client. Call once at startup."""
        if self.api_key:
            self._client = httpx.Client(
                base_url=self.api_base,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            self._available = True
            logger.info("Embedding API configured: %s", self.api_base)
        else:
            logger.warning(
                "No EMBEDDING_API_KEY set — using hash-based fallback vectors. "
                "Semantic search quality will be limited."
            )

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()

    def _hash_embed(self, text: str) -> list[float]:
        """Generate a deterministic pseudo-embedding from text hash.

        Not semantically meaningful, but allows store/recall/decay to work
        without an embedding API. Good enough for testing.
        """
        h = hashlib.sha256(text.encode()).digest()
        # Expand hash to fill embedding_dim
        values: list[float] = []
        for i in range(self.embedding_dim):
            byte_val = h[i % len(h)]
            # Map to [-1, 1] range and vary by position
            val = math.sin(byte_val * 0.0245 + i * 0.1)
            values.append(val)
        # L2 normalize
        norm = math.sqrt(sum(v * v for v in values))
        if norm > 0:
            values = [v / norm for v in values]
        return values

    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text string.

        Falls back to hash-based vector if API not configured.
        """
        if not self._available:
            return self._hash_embed(text)

        assert self._client is not None
        response = self._client.post(
            "/embeddings",
            json={
                "input": text,
                "model": self.model,
            },
        )
        response.raise_for_status()
        data = response.json()
        embedding: list[float] = data["data"][0]["embedding"]
        return embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        if not self._available:
            return [self._hash_embed(t) for t in texts]

        assert self._client is not None
        response = self._client.post(
            "/embeddings",
            json={
                "input": texts,
                "model": self.model,
            },
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]
