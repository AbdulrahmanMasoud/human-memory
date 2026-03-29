"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration for the Human-Like Memory System."""

    model_config = {"env_prefix": "", "case_sensitive": False}

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "memory_system"
    postgres_user: str = "memory"
    postgres_password: str = "memory_secret"

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Neo4j (V2+)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j_secret"

    # ACT-R Parameters
    actr_decay_rate: float = 0.5
    actr_noise_std: float = 0.25
    actr_retrieval_threshold: float = -1.0

    # Embedding API (OpenAI-compatible)
    embedding_api_base: str = "https://api.openai.com/v1"
    embedding_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536

    # LLM (V2+ consolidation, V3+ emotion)
    llm_api_base: str = "http://localhost:11434/v1"
    llm_api_key: str = ""
    llm_model: str = "llama3"

    # Working Memory (V3+)
    working_memory_capacity: int = 7

    # Emotional Salience weights (V3+)
    salience_alpha: float = 0.4
    salience_beta: float = 0.3
    salience_gamma: float = 0.2
    salience_delta: float = 0.1

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "info"


settings = Settings()
