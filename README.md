# human-memory

A human-like memory system for AI agents based on the **ACT-R cognitive architecture**. Instead of treating all stored data equally, this system mimics how the human brain actually works — memories that are used often get stronger, unused ones fade away, emotional events stick longer, and general knowledge is extracted from repeated experiences.

## How it works

```
Store → Embed → Retrieve (ACT-R ranked) → Strengthen on access → Decay over time → Consolidate → Forget
```

Every memory has an **activation level** computed by the ACT-R equation:

```
A = B + S + P + ε
```

- **B** — Base-level: recent and frequently accessed memories score higher (power-law decay)
- **S** — Spreading activation: context from the knowledge graph boosts related memories
- **P** — Partial matching: similar but imperfect matches get a penalty
- **ε** — Noise: randomness, like real human recall

Memories below the activation threshold become inaccessible — forgotten but not deleted.

## 5 Memory Types

| Type | What it stores | Backend |
|------|---------------|---------|
| **Episodic** | Events and experiences | Qdrant + PostgreSQL |
| **Semantic** | General knowledge (concepts, facts) | Neo4j graph |
| **Procedural** | Compiled skills from repeated patterns | PostgreSQL |
| **Working** | Active context (7±2 items max) | In-memory |
| **Emotional** | Valence/arousal scores that slow decay | PostgreSQL |

## 5 Forgetting Modes

1. **Temporal decay** — memories weaken over time (power-law, every 30 min)
2. **Interference** — new similar memories weaken old ones
3. **Retrieval-induced** — retrieving A suppresses competitors B, C
4. **Strategic prune** — goal-directed: irrelevant memories weakened
5. **Capacity overflow** — weakest archived when store is full

## Consolidation (every 6 hours)

Like sleep, the system periodically:
1. **Replays** high-importance recent memories (strengthens them)
2. **Extracts** general facts from episode clusters via LLM
3. **Prunes** all activations globally (weak ones archived)
4. **Compiles** repeated patterns into procedural skills

## Quick Start

```bash
# Clone
git clone https://github.com/<you>/human-memory.git
cd human-memory

# Configure
cp .env.example .env
# Edit .env — set EMBEDDING_API_KEY (OpenAI, or any compatible API)

# Run
docker compose up -d

# Create tables
docker compose exec app alembic upgrade head

# Verify
curl http://localhost:8000/ready
```

## API

### Memories
```
POST   /v1/memories              — Store a memory
POST   /v1/memories/search       — Semantic search (ACT-R ranked)
GET    /v1/memories/{id}         — Recall by ID (strengthens it)
DELETE /v1/memories/{id}         — Forget (soft delete)
POST   /v1/memories/decay        — Trigger decay manually
GET    /v1/memories/{id}/inspect — Full metadata + access history
POST   /v1/memories/forget-strategy — Apply a forgetting mode
```

### Knowledge Graph
```
POST   /v1/graph/concepts        — Create a concept
GET    /v1/graph/concepts/{name} — Get concept + relations
POST   /v1/graph/relations       — Create a relationship
POST   /v1/graph/search          — Spreading activation search
POST   /v1/graph/consolidate     — Trigger consolidation
```

### System
```
GET    /v1/stats                 — Memory statistics
GET    /health                   — Liveness check
GET    /ready                    — Readiness (checks all backends)
GET    /docs                     — Swagger UI
```

### Example

```bash
# Store
curl -X POST http://localhost:8000/v1/memories \
  -H "Content-Type: application/json" \
  -d '{"content": "Python is great for AI development"}'

# Search (ranked by ACT-R activation, not just similarity)
curl -X POST http://localhost:8000/v1/memories/search \
  -H "Content-Type: application/json" \
  -d '{"query": "programming languages for machine learning", "top_k": 5}'

# Build knowledge graph
curl -X POST http://localhost:8000/v1/graph/concepts \
  -H "Content-Type: application/json" \
  -d '{"name": "Python", "type": "language"}'

curl -X POST http://localhost:8000/v1/graph/relations \
  -H "Content-Type: application/json" \
  -d '{"source": "Python", "target": "AI", "relation_type": "USED_FOR", "weight": 0.9}'
```

## Architecture

```
┌──────────────────────────────────────────────┐
│              FastAPI (15 endpoints)           │
├──────────────────────────────────────────────┤
│  ACT-R Engine  │  Emotion  │  Forgetting     │
│  Consolidation │  Working Memory │  Clustering│
├──────────────────────────────────────────────┤
│  Qdrant     │  PostgreSQL  │  Neo4j  │ Redis │
│  (vectors)  │  (metadata)  │ (graph) │(cache)│
└──────────────────────────────────────────────┘
        ↕               ↕
   Celery Worker    Celery Beat
   (decay/consol)   (scheduler)
```

## Docker Services

| Service | Image | Port |
|---------|-------|------|
| App | python:3.13-alpine (255MB) | 8000 |
| Worker | same | — |
| Beat | same | — |
| PostgreSQL | postgres:17-alpine | 5432 |
| Qdrant | qdrant/qdrant | 6333 |
| Redis | redis:7-alpine | 6379 |
| Neo4j | neo4j:5-community | 7474, 7687 |

## Tests

```bash
# Unit tests (56 tests, no Docker needed)
uv run --extra dev -- pytest tests/unit/ -v

# End-to-end (requires running services)
PYTHONPATH=src uv run --extra dev -- python tests/e2e_test.py

# Deep memory logic verification
PYTHONPATH=src uv run --extra dev -- python tests/memory_logic_test.py
```

## Configuration

All settings via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_API_BASE` | `https://api.openai.com/v1` | Embedding endpoint |
| `EMBEDDING_API_KEY` | — | API key (required for search) |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Model name |
| `EMBEDDING_DIM` | `1536` | Vector dimensions |
| `ACTR_DECAY_RATE` | `0.5` | ACT-R decay parameter (d) |
| `ACTR_RETRIEVAL_THRESHOLD` | `-1.0` | Minimum activation for retrieval (τ) |
| `WORKING_MEMORY_CAPACITY` | `7` | Max items in working memory |

## Based on

- **ACT-R** (Anderson, Carnegie Mellon) — activation equations
- **Ebbinghaus forgetting curve** — power-law decay
- **Baddeley's working memory model** — 7±2 capacity
- **Complementary Learning Systems** (McClelland) — consolidation
- **Russell's Circumplex Model** — valence-arousal emotion mapping

## License

MIT
