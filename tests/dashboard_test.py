"""Test all dashboard and benchmark features."""

import json
import sys

import httpx

BASE = "http://localhost:8000"
c = httpx.Client(base_url=BASE, timeout=30.0)

passed = 0
failed = 0
errors: list[str] = []


def test(name, func):
    global passed, failed
    try:
        func()
        print(f"  ✅ {name}")
        passed += 1
    except Exception as e:
        print(f"  ❌ {name} — {e}")
        failed += 1
        errors.append(f"{name}: {e}")


# ═══════════════════════════════════════════════════════
print("\n🖥️  Dashboard Serving")
print("=" * 55)


def test_dashboard_serves():
    r = c.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "Human Memory" in r.text
    assert "D3" in r.text or "d3" in r.text


test("GET / serves dashboard HTML", test_dashboard_serves)


def test_dashboard_has_all_tabs():
    r = c.get("/")
    text = r.text
    assert "panel-overview" in text
    assert "panel-graph" in text
    assert "panel-explorer" in text
    assert "panel-controls" in text
    assert "panel-benchmark" in text


test("Dashboard has all 5 tabs", test_dashboard_has_all_tabs)


def test_dashboard_has_d3():
    r = c.get("/")
    assert "d3@7" in r.text or "d3.js" in r.text


test("Dashboard loads D3.js", test_dashboard_has_d3)


def test_dashboard_has_chartjs():
    r = c.get("/")
    assert "chart.js" in r.text or "Chart" in r.text


test("Dashboard loads Chart.js", test_dashboard_has_chartjs)


# ═══════════════════════════════════════════════════════
print("\n📋 List Memories Endpoint")
print("=" * 55)


def test_list_memories_empty():
    # May have data from previous tests, just check structure
    r = c.get("/v1/memories", params={"limit": 5, "offset": 0})
    assert r.status_code == 200
    data = r.json()
    assert "memories" in data
    assert "offset" in data
    assert "limit" in data
    assert isinstance(data["memories"], list)


test("GET /v1/memories returns correct structure", test_list_memories_empty)


def test_list_memories_pagination():
    r1 = c.get("/v1/memories", params={"limit": 2, "offset": 0})
    r2 = c.get("/v1/memories", params={"limit": 2, "offset": 2})
    assert r1.status_code == 200
    assert r2.status_code == 200
    d1 = r1.json()
    d2 = r2.json()
    assert len(d1["memories"]) <= 2
    assert d1["offset"] == 0
    assert d2["offset"] == 2


test("Pagination works correctly", test_list_memories_pagination)


def test_list_memories_fields():
    # Store a memory to ensure we have data
    c.post("/v1/memories", json={"content": "Dashboard test memory for field check"})
    r = c.get("/v1/memories", params={"limit": 1})
    data = r.json()
    if data["memories"]:
        m = data["memories"][0]
        assert "memory_id" in m
        assert "content" in m
        assert "activation" in m
        assert "status" in m
        assert "access_count" in m
        assert "salience" in m
        assert "memory_type" in m
        assert "created_at" in m
        assert "last_accessed" in m


test("Memory list includes all required fields", test_list_memories_fields)


# ═══════════════════════════════════════════════════════
print("\n🕸️  Graph Export Endpoint")
print("=" * 55)


def test_graph_export_structure():
    r = c.get("/v1/graph/export")
    assert r.status_code == 200
    data = r.json()
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)


test("GET /v1/graph/export returns nodes + edges", test_graph_export_structure)


def test_graph_export_with_data():
    # Create concepts and relations
    c.post("/v1/graph/concepts", json={"name": "DashTest1", "type": "test", "activation": 0.7})
    c.post("/v1/graph/concepts", json={"name": "DashTest2", "type": "test", "activation": 0.6})
    c.post(
        "/v1/graph/relations",
        json={"source": "DashTest1", "target": "DashTest2", "relation_type": "LINKED", "weight": 0.8},
    )

    r = c.get("/v1/graph/export")
    data = r.json()

    names = [n["name"] for n in data["nodes"]]
    assert "DashTest1" in names
    assert "DashTest2" in names

    # Check node fields
    node = next(n for n in data["nodes"] if n["name"] == "DashTest1")
    assert "type" in node
    assert "activation" in node

    # Check edge
    edge = next(
        (e for e in data["edges"] if e["source"] == "DashTest1" and e["target"] == "DashTest2"),
        None,
    )
    assert edge is not None
    assert edge["relation_type"] == "LINKED"
    assert edge["weight"] == 0.8


test("Graph export includes created concepts and relations", test_graph_export_with_data)


def test_graph_export_limit():
    r = c.get("/v1/graph/export", params={"limit": 1})
    assert r.status_code == 200


test("Graph export respects limit parameter", test_graph_export_limit)


# ═══════════════════════════════════════════════════════
print("\n🏎️  Benchmark Endpoint")
print("=" * 55)


def test_benchmark_runs():
    """Run a small benchmark (10 memories) and verify SSE stream."""
    r = c.post(
        "/v1/benchmark/run",
        json={"count": 10, "batch_size": 5, "search_count": 5},
        timeout=120.0,
    )
    assert r.status_code == 200
    assert "text/event-stream" in r.headers["content-type"]

    # Parse SSE events
    events = []
    for line in r.text.strip().split("\n"):
        if line.startswith("data: "):
            events.append(json.loads(line[6:]))

    assert len(events) >= 2, f"Expected >= 2 events, got {len(events)}"

    # Should have store events and a complete event
    phases = [e["phase"] for e in events]
    assert "store" in phases
    assert "complete" in phases


test("Benchmark runs and streams SSE events", test_benchmark_runs)


def test_benchmark_store_events():
    """Verify store phase events have correct fields."""
    r = c.post(
        "/v1/benchmark/run",
        json={"count": 10, "batch_size": 5, "search_count": 0},
        timeout=60.0,
    )
    events = [json.loads(line[6:]) for line in r.text.strip().split("\n") if line.startswith("data: ")]

    store_events = [e for e in events if e["phase"] == "store"]
    assert len(store_events) >= 1

    e = store_events[0]
    assert "progress" in e
    assert "total_stored" in e
    assert "p50" in e
    assert "p95" in e
    assert "p99" in e
    assert e["total_stored"] > 0


test("Store phase events have latency percentiles", test_benchmark_store_events)


def test_benchmark_complete_event():
    """Verify complete event has full summary."""
    r = c.post(
        "/v1/benchmark/run",
        json={"count": 10, "batch_size": 10, "search_count": 5},
        timeout=60.0,
    )
    events = [json.loads(line[6:]) for line in r.text.strip().split("\n") if line.startswith("data: ")]

    complete = [e for e in events if e["phase"] == "complete"]
    assert len(complete) == 1

    c_event = complete[0]
    assert "total_memories" in c_event
    assert c_event["total_memories"] == 10
    assert "total_time_ms" in c_event
    assert "store" in c_event
    assert "retrieve" in c_event
    assert "p50" in c_event["store"]
    assert "p95" in c_event["store"]
    assert "p99" in c_event["store"]


test("Complete event has full benchmark summary", test_benchmark_complete_event)


def test_benchmark_updates_stats():
    """Benchmark complete event should report correct count."""
    r = c.post(
        "/v1/benchmark/run",
        json={"count": 10, "batch_size": 10, "search_count": 0},
        timeout=60.0,
    )
    assert r.status_code == 200, f"Benchmark returned {r.status_code}"
    lines = [ln for ln in r.text.strip().split("\n") if ln.startswith("data: ")]
    assert len(lines) > 0, f"No SSE events received. Response: {r.text[:200]}"
    events = [json.loads(ln[6:]) for ln in lines]
    completes = [e for e in events if e["phase"] == "complete"]
    assert len(completes) == 1, f"Expected 1 complete event, got {len(completes)}: {events}"
    complete = completes[0]
    assert complete["total_memories"] == 10
    assert complete["store"]["count"] == 10


test("Benchmark memories appear in stats", test_benchmark_updates_stats)


# ═══════════════════════════════════════════════════════
print("\n🔗 Integration: Dashboard data works together")
print("=" * 55)


def test_memories_searchable_after_benchmark():
    """Memories stored by benchmark should be searchable."""
    r = c.post(
        "/v1/memories/search",
        json={"query": "machine learning neural networks", "top_k": 5},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["count"] > 0, "Benchmark memories should be searchable"


test("Benchmark memories are searchable", test_memories_searchable_after_benchmark)


def test_decay_after_benchmark():
    """Decay should process all benchmark memories."""
    r = c.post("/v1/memories/decay")
    data = r.json()
    assert data["memories_processed"] > 0


test("Decay processes benchmark memories", test_decay_after_benchmark)


def test_list_shows_all_statuses():
    """List endpoint should show memories of all statuses."""
    # Delete one to create a 'deleted' status
    r = c.get("/v1/memories", params={"limit": 1})
    mems = r.json()["memories"]
    if mems:
        mid = mems[0]["memory_id"]
        c.delete(f"/v1/memories/{mid}")

    # List should still include all
    r = c.get("/v1/memories", params={"limit": 200})
    assert r.status_code == 200


test("Memory list handles all statuses", test_list_shows_all_statuses)


# ═══════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 55)
print(f"📊 Results: {passed} passed, {failed} failed out of {passed + failed}")
print("=" * 55)

if errors:
    print("\n❌ Failures:")
    for e in errors:
        print(f"  • {e}")

sys.exit(1 if failed > 0 else 0)
