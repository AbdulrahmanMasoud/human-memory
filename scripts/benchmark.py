#!/usr/bin/env python3
"""Standalone CLI benchmark for the Human Memory system.

Usage:
    python scripts/benchmark.py --count 1000 --batch-size 50
    python scripts/benchmark.py --count 10000 --json
"""

import argparse
import json
import random
import sys
import time

import httpx

TOPICS = [
    "machine learning algorithms and neural networks",
    "database optimization and query performance",
    "cloud computing and container orchestration",
    "natural language processing and text analysis",
    "distributed systems and microservices architecture",
    "cybersecurity and threat detection systems",
    "data engineering and ETL pipelines",
    "frontend development with modern frameworks",
    "DevOps practices and CI/CD automation",
    "quantum computing and theoretical physics",
]

QUERIES = [
    "programming languages",
    "machine learning",
    "database systems",
    "cloud infrastructure",
    "security practices",
]


def percentiles(lats: list[float]) -> dict[str, float]:
    if not lats:
        return {"p50": 0, "p95": 0, "p99": 0}
    s = sorted(lats)
    n = len(s)
    return {
        "p50": round(s[int(n * 0.50)], 2),
        "p95": round(s[int(min(n * 0.95, n - 1))], 2),
        "p99": round(s[int(min(n * 0.99, n - 1))], 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Benchmark the Human Memory API")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--search-count", type=int, default=100)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    client = httpx.Client(base_url=args.api_url, timeout=30.0)

    # Check health
    try:
        r = client.get("/health")
        assert r.status_code == 200
    except Exception:
        print(f"ERROR: Cannot connect to {args.api_url}")
        sys.exit(1)

    print(f"Benchmark: {args.count} memories, batch={args.batch_size}, searches={args.search_count}")
    print(f"API: {args.api_url}\n")

    # Store phase
    store_lats: list[float] = []
    t_start = time.time()

    for i in range(args.count):
        topic = random.choice(TOPICS)
        content = f"Benchmark {i}: {topic} - v{random.randint(1, 9999)}"

        t0 = time.time()
        r = client.post("/v1/memories", json={"content": content})
        lat = (time.time() - t0) * 1000
        store_lats.append(lat)

        if (i + 1) % args.batch_size == 0:
            p = percentiles(store_lats)
            print(
                f"\r  Store: {i+1}/{args.count} "
                f"| p50={p['p50']:.0f}ms p95={p['p95']:.0f}ms p99={p['p99']:.0f}ms",
                end="",
                flush=True,
            )

    store_time = time.time() - t_start
    print(f"\n  Store complete: {args.count} memories in {store_time:.1f}s\n")

    # Search phase
    search_lats: list[float] = []
    t_start = time.time()

    for i in range(args.search_count):
        query = random.choice(QUERIES)
        t0 = time.time()
        client.post("/v1/memories/search", json={"query": query, "top_k": 5})
        lat = (time.time() - t0) * 1000
        search_lats.append(lat)

        if (i + 1) % 10 == 0:
            p = percentiles(search_lats)
            print(
                f"\r  Search: {i+1}/{args.search_count} "
                f"| p50={p['p50']:.0f}ms p95={p['p95']:.0f}ms p99={p['p99']:.0f}ms",
                end="",
                flush=True,
            )

    search_time = time.time() - t_start
    print(f"\n  Search complete: {args.search_count} queries in {search_time:.1f}s\n")

    # Results
    sp = percentiles(store_lats)
    rp = percentiles(search_lats)

    results = {
        "store": {
            "count": args.count,
            "total_sec": round(store_time, 1),
            **sp,
            "avg": round(sum(store_lats) / len(store_lats), 1),
        },
        "retrieve": {
            "count": args.search_count,
            "total_sec": round(search_time, 1),
            **rp,
            "avg": round(sum(search_lats) / max(len(search_lats), 1), 1),
        },
    }

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 50)
        print("RESULTS")
        print("=" * 50)
        print(f"  Store  ({args.count} memories):")
        print(f"    p50={sp['p50']:.0f}ms  p95={sp['p95']:.0f}ms  p99={sp['p99']:.0f}ms  avg={results['store']['avg']:.0f}ms")
        print(f"    Total: {store_time:.1f}s  ({args.count/store_time:.0f} ops/sec)")
        print(f"  Search ({args.search_count} queries):")
        print(f"    p50={rp['p50']:.0f}ms  p95={rp['p95']:.0f}ms  p99={rp['p99']:.0f}ms  avg={results['retrieve']['avg']:.0f}ms")
        if search_time > 0:
            print(f"    Total: {search_time:.1f}s  ({args.search_count/search_time:.0f} ops/sec)")
        print("=" * 50)

    client.close()


if __name__ == "__main__":
    main()
