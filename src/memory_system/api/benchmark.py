"""FastAPI router for benchmark with SSE streaming."""

import asyncio
import json
import random
import time

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/benchmark", tags=["benchmark"])

SAMPLE_TOPICS = [
    "machine learning algorithms and neural networks",
    "database optimization and query performance",
    "cloud computing and container orchestration",
    "natural language processing and text analysis",
    "computer vision and image recognition",
    "distributed systems and microservices",
    "cybersecurity and threat detection",
    "data engineering and ETL pipelines",
    "frontend development with React and TypeScript",
    "DevOps practices and CI/CD automation",
    "blockchain technology and smart contracts",
    "quantum computing fundamentals",
    "robotics and autonomous systems",
    "bioinformatics and genomic analysis",
    "game development and physics engines",
    "mobile app development for iOS and Android",
    "embedded systems and IoT devices",
    "recommendation systems and collaborative filtering",
    "speech recognition and voice assistants",
    "augmented reality and 3D rendering",
]

SEARCH_QUERIES = [
    "programming languages",
    "machine learning",
    "database systems",
    "cloud infrastructure",
    "security best practices",
    "data processing",
    "web development",
    "artificial intelligence",
    "system architecture",
    "software testing",
]


class BenchmarkRequest(BaseModel):
    count: int = Field(default=1000, ge=10, le=50000)
    batch_size: int = Field(default=50, ge=1, le=500)
    search_count: int = Field(default=100, ge=0, le=1000)


def _percentiles(latencies: list[float]) -> dict[str, float]:
    if not latencies:
        return {"p50": 0, "p95": 0, "p99": 0}
    s = sorted(latencies)
    n = len(s)
    return {
        "p50": round(s[int(n * 0.50)], 2),
        "p95": round(s[int(min(n * 0.95, n - 1))], 2),
        "p99": round(s[int(min(n * 0.99, n - 1))], 2),
    }


@router.post("/run")
async def run_benchmark(body: BenchmarkRequest, request: Request) -> StreamingResponse:
    """Run a benchmark storing N memories and measuring latency. Streams progress via SSE."""
    service = request.app.state.memory_service

    async def generate():
        store_latencies: list[float] = []
        search_latencies: list[float] = []
        total_start = time.time()

        # --- Store phase ---
        for batch_start in range(0, body.count, body.batch_size):
            batch_end = min(batch_start + body.batch_size, body.count)
            batch_lats: list[float] = []

            for i in range(batch_start, batch_end):
                topic = random.choice(SAMPLE_TOPICS)
                content = f"Benchmark memory {i}: {topic} - variation {random.randint(1, 10000)}"

                t0 = time.time()
                try:
                    await service.store(content=content, memory_type="episodic")
                    lat = (time.time() - t0) * 1000
                    batch_lats.append(lat)
                    store_latencies.append(lat)
                except Exception:
                    batch_lats.append(-1)
                    store_latencies.append(-1)

            progress = batch_end / body.count
            valid_lats = [v for v in store_latencies if v > 0]
            event = {
                "phase": "store",
                "progress": round(progress, 3),
                "total_stored": batch_end,
                "batch_avg_ms": round(
                    sum(v for v in batch_lats if v > 0) / max(len(batch_lats), 1), 1
                ),
                **_percentiles(valid_lats),
            }
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0.01)

        # --- Search phase ---
        if body.search_count > 0:
            for i in range(body.search_count):
                query = random.choice(SEARCH_QUERIES)
                t0 = time.time()
                try:
                    await service.retrieve(query=query, top_k=5)
                    lat = (time.time() - t0) * 1000
                    search_latencies.append(lat)
                except Exception:
                    search_latencies.append(-1)

                if (i + 1) % 10 == 0 or i == body.search_count - 1:
                    valid_search = [v for v in search_latencies if v > 0]
                    event = {
                        "phase": "retrieve",
                        "progress": round((i + 1) / body.search_count, 3),
                        "total_searched": i + 1,
                        **_percentiles(valid_search),
                    }
                    yield f"data: {json.dumps(event)}\n\n"
                    await asyncio.sleep(0.01)

        # --- Complete ---
        total_time = round((time.time() - total_start) * 1000)
        valid_store = [v for v in store_latencies if v > 0]
        valid_search = [v for v in search_latencies if v > 0]
        event = {
            "phase": "complete",
            "total_memories": body.count,
            "total_time_ms": total_time,
            "store": {
                "count": len(valid_store),
                **_percentiles(valid_store),
                "avg_ms": round(sum(valid_store) / max(len(valid_store), 1), 1),
            },
            "retrieve": {
                "count": len(valid_search),
                **_percentiles(valid_search),
                "avg_ms": round(sum(valid_search) / max(len(valid_search), 1), 1),
            },
        }
        yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
