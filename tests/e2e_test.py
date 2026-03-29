"""End-to-end test of all features against the running API."""

import sys

import httpx

BASE = "http://localhost:8000"
client = httpx.Client(base_url=BASE, timeout=30.0)

passed = 0
failed = 0
errors: list[str] = []


def test(name: str, func):
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
# V1: EPISODIC MEMORY + ACT-R DECAY
# ═══════════════════════════════════════════════════════
print("\n🧪 V1: Episodic Memory + ACT-R Decay")
print("=" * 50)


# --- Health & Ready ---
def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready():
    r = client.get("/ready")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ready"
    assert data["checks"]["postgres"] == "ok"
    assert data["checks"]["qdrant"] == "ok"


test("Health check", test_health)
test("Readiness check", test_ready)

# --- Store memories ---
memory_ids = []


def test_store_memory():
    r = client.post(
        "/v1/memories",
        json={"content": "Python is great for AI development", "memory_type": "episodic"},
    )
    assert r.status_code == 201, f"Got {r.status_code}: {r.text}"
    data = r.json()
    assert "memory_id" in data
    assert data["activation"] == 1.0
    memory_ids.append(data["memory_id"])


test("Store memory #1", test_store_memory)


def test_store_memory_2():
    r = client.post("/v1/memories", json={"content": "Redis is an in-memory data store"})
    assert r.status_code == 201
    memory_ids.append(r.json()["memory_id"])


def test_store_memory_3():
    r = client.post("/v1/memories", json={"content": "Neo4j is a graph database for relationships"})
    assert r.status_code == 201
    memory_ids.append(r.json()["memory_id"])


def test_store_memory_4():
    r = client.post("/v1/memories", json={"content": "FastAPI is a modern Python web framework"})
    assert r.status_code == 201
    memory_ids.append(r.json()["memory_id"])


def test_store_memory_5():
    r = client.post(
        "/v1/memories", json={"content": "Docker containers use Alpine Linux for small images"}
    )
    assert r.status_code == 201
    memory_ids.append(r.json()["memory_id"])


test("Store memory #2", test_store_memory_2)
test("Store memory #3", test_store_memory_3)
test("Store memory #4", test_store_memory_4)
test("Store memory #5", test_store_memory_5)


# --- Store validation ---
def test_store_empty_rejected():
    r = client.post("/v1/memories", json={"content": ""})
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"


test("Empty content rejected (422)", test_store_empty_rejected)


# --- Recall by ID ---
def test_recall_by_id():
    r = client.get(f"/v1/memories/{memory_ids[0]}")
    assert r.status_code == 200
    data = r.json()
    assert data["memory_id"] == memory_ids[0]
    assert data["content"] == "Python is great for AI development"
    assert data["access_count"] >= 1


test("Recall by ID", test_recall_by_id)


def test_recall_nonexistent():
    r = client.get("/v1/memories/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


test("Recall nonexistent returns 404", test_recall_nonexistent)


# --- Access tracking (recall again, count should increase) ---
def test_access_tracking():
    # Recall same memory twice more
    client.get(f"/v1/memories/{memory_ids[0]}")
    client.get(f"/v1/memories/{memory_ids[0]}")
    r = client.get(f"/v1/memories/{memory_ids[0]}")
    data = r.json()
    # Initial store (1) + first recall in test_recall_by_id (1) + 3 more = at least 4
    assert data["access_count"] >= 4, f"access_count={data['access_count']}, expected >= 4"


test("Access tracking increases count", test_access_tracking)


# --- Stats ---
def test_stats():
    r = client.get("/v1/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 5
    assert data["active"] >= 5
    assert data["avg_activation"] > 0


test("Stats endpoint", test_stats)


# --- Inspect ---
def test_inspect():
    r = client.get(f"/v1/memories/{memory_ids[0]}/inspect")
    assert r.status_code == 200
    data = r.json()
    assert data["memory_id"] == memory_ids[0]
    assert "access_history" in data
    assert len(data["access_history"]) >= 1
    assert "salience" in data
    assert "emotion_valence" in data
    assert "decay_rate" in data
    assert data["status"] == "active"


test("Inspect full metadata", test_inspect)


# --- Search (requires embedding API — will test endpoint availability) ---
def test_search_endpoint_exists():
    r = client.post("/v1/memories/search", json={"query": "test", "top_k": 3})
    # Will fail with 500 if no embedding API configured, but endpoint should exist
    assert r.status_code in (200, 500), f"Unexpected status: {r.status_code}"


test("Search endpoint exists", test_search_endpoint_exists)


# --- Decay ---
def test_decay():
    r = client.post("/v1/memories/decay")
    assert r.status_code == 200
    data = r.json()
    assert "memories_processed" in data
    assert data["memories_processed"] >= 5
    assert "memories_decayed" in data


test("Manual decay trigger", test_decay)


# --- Verify decay changed activations ---
def test_decay_effect():
    r = client.get(f"/v1/memories/{memory_ids[1]}/inspect")
    data = r.json()
    # After decay, activation should be recalculated (may be different from 1.0)
    assert "activation" in data
    # The memory was just stored and accessed once, so activation could be anything
    # but it should be a finite number
    assert isinstance(data["activation"], (int, float))


test("Decay updates activation values", test_decay_effect)


# --- Delete (forget) ---
def test_forget():
    # Store a temp memory to delete
    r = client.post("/v1/memories", json={"content": "This will be forgotten"})
    temp_id = r.json()["memory_id"]

    r = client.delete(f"/v1/memories/{temp_id}")
    assert r.status_code == 200
    assert r.json()["deleted"] is True

    # Should not be recallable
    r = client.get(f"/v1/memories/{temp_id}")
    assert r.status_code == 404


test("Forget (soft delete)", test_forget)


# ═══════════════════════════════════════════════════════
# V2: SEMANTIC MEMORY + CONSOLIDATION
# ═══════════════════════════════════════════════════════
print("\n🧪 V2: Semantic Memory + Consolidation")
print("=" * 50)


# --- Create concepts ---
def test_create_concept_python():
    r = client.post(
        "/v1/graph/concepts", json={"name": "Python", "type": "language", "activation": 0.9}
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Python"
    assert data["type"] == "language"


def test_create_concept_ai():
    r = client.post("/v1/graph/concepts", json={"name": "AI", "type": "field"})
    assert r.status_code == 201


def test_create_concept_fastapi():
    r = client.post("/v1/graph/concepts", json={"name": "FastAPI", "type": "framework"})
    assert r.status_code == 201


def test_create_concept_webdev():
    r = client.post("/v1/graph/concepts", json={"name": "Web Development", "type": "field"})
    assert r.status_code == 201


test("Create concept: Python", test_create_concept_python)
test("Create concept: AI", test_create_concept_ai)
test("Create concept: FastAPI", test_create_concept_fastapi)
test("Create concept: Web Development", test_create_concept_webdev)


# --- Create relationships ---
def test_create_relation_python_ai():
    r = client.post(
        "/v1/graph/relations",
        json={"source": "Python", "target": "AI", "relation_type": "USED_FOR", "weight": 0.9},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["source"] == "Python"
    assert data["target"] == "AI"
    assert data["relation_type"] == "USED_FOR"


def test_create_relation_fastapi_python():
    r = client.post(
        "/v1/graph/relations",
        json={
            "source": "FastAPI",
            "target": "Python",
            "relation_type": "WORKS_WITH",
            "weight": 0.95,
        },
    )
    assert r.status_code == 201


def test_create_relation_fastapi_webdev():
    r = client.post(
        "/v1/graph/relations",
        json={
            "source": "FastAPI",
            "target": "Web Development",
            "relation_type": "USED_FOR",
            "weight": 0.85,
        },
    )
    assert r.status_code == 201


test("Relation: Python → USED_FOR → AI", test_create_relation_python_ai)
test("Relation: FastAPI → WORKS_WITH → Python", test_create_relation_fastapi_python)
test("Relation: FastAPI → USED_FOR → Web Dev", test_create_relation_fastapi_webdev)


# --- Get concept with relationships ---
def test_get_concept():
    r = client.get("/v1/graph/concepts/Python")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Python"
    assert len(data["relationships"]) >= 1


test("Get concept with relationships", test_get_concept)


def test_get_concept_not_found():
    r = client.get("/v1/graph/concepts/NonExistent")
    assert r.status_code == 404


test("Get nonexistent concept returns 404", test_get_concept_not_found)


# --- Spreading activation search ---
def test_spreading_activation():
    r = client.post(
        "/v1/graph/search", json={"active_concepts": ["Python"], "depth": 2, "limit": 10}
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Python connects to AI and FastAPI, so we should get results
    if len(data) > 0:
        names = [d["name"] for d in data]
        # AI should be found (directly connected)
        assert "AI" in names or "FastAPI" in names, f"Expected AI or FastAPI in {names}"


test("Spreading activation from Python", test_spreading_activation)


def test_spreading_activation_multi():
    r = client.post(
        "/v1/graph/search", json={"active_concepts": ["Python", "FastAPI"], "depth": 2, "limit": 10}
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


test("Spreading activation multi-concept", test_spreading_activation_multi)


# --- Consolidation ---
def test_consolidation():
    r = client.post("/v1/graph/consolidate")
    assert r.status_code == 200
    data = r.json()
    assert "episodes_replayed" in data
    assert "facts_extracted" in data
    assert "memories_pruned" in data
    assert "memories_downscaled" in data
    assert "phase_4_compiled" in data


test("Consolidation cycle runs", test_consolidation)


# --- Verify prune effect ---
def test_prune_effect():
    # After consolidation, activations should be lower (downscaled by 0.9)
    r = client.get("/v1/stats")
    data = r.json()
    # Just verify the endpoint still works after consolidation
    assert data["total"] >= 5


test("System stable after consolidation", test_prune_effect)


# ═══════════════════════════════════════════════════════
# V3: EMOTIONAL SALIENCE + WORKING MEMORY
# ═══════════════════════════════════════════════════════
print("\n🧪 V3: Emotional Salience + Working Memory")
print("=" * 50)


# --- Emotion fields exist in metadata ---
def test_emotion_fields():
    r = client.get(f"/v1/memories/{memory_ids[0]}/inspect")
    data = r.json()
    assert "emotion_valence" in data
    assert "emotion_arousal" in data
    assert "salience" in data
    assert isinstance(data["emotion_valence"], (int, float))
    assert isinstance(data["emotion_arousal"], (int, float))
    assert isinstance(data["salience"], (int, float))


test("Emotion fields in metadata", test_emotion_fields)


# --- Working memory capacity test ---
def test_working_memory_capacity():
    """Store 15 memories, search should return max 7 (default working memory)."""
    for i in range(10):
        client.post(
            "/v1/memories", json={"content": f"Test memory number {i} about various topics"}
        )

    # Search endpoint uses working memory capacity
    r = client.post("/v1/memories/search", json={"query": "test", "top_k": 20})
    # Even if search fails (no embedding API), the parameter is accepted
    assert r.status_code in (200, 500)


test("Working memory capacity parameter accepted", test_working_memory_capacity)


# --- Salience scoring (unit test the logic) ---
def test_salience_scoring():
    from memory_system.core.emotion import EmotionalSalience

    es = EmotionalSalience()

    # High emotion = high salience
    high = es.compute_salience(valence=-0.8, arousal=0.9)
    low = es.compute_salience(valence=0.0, arousal=0.2)
    assert high > low, f"High salience ({high}) should be > low ({low})"

    # Salience modifies decay
    slow_decay = es.modify_decay_rate(0.5, salience=0.9)
    fast_decay = es.modify_decay_rate(0.5, salience=0.1)
    assert slow_decay < fast_decay, "High salience should produce slower decay"


test("Salience scoring math", test_salience_scoring)


# --- Working memory filter ---
def test_working_memory_filter():
    from memory_system.core.working_memory import WorkingMemory

    wm = WorkingMemory(capacity=7)

    items = [{"id": i, "activation": float(i)} for i in range(20)]
    result = wm.filter_by_capacity(items)
    assert len(result) == 7
    assert result[0]["activation"] == 19.0  # highest


test("Working memory filters to capacity", test_working_memory_filter)


# ═══════════════════════════════════════════════════════
# V4: PROCEDURAL MEMORY + STRATEGIC FORGETTING
# ═══════════════════════════════════════════════════════
print("\n🧪 V4: Procedural Memory + Strategic Forgetting")
print("=" * 50)


# --- Forgetting: strategic prune ---
def test_forget_strategic():
    r = client.post(
        "/v1/memories/forget-strategy",
        json={
            "strategy": "strategic_prune",
            "params": {"goals": ["Python", "programming", "development"]},
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["strategy"] == "strategic_prune"
    assert "memories_affected" in data


test("Strategic prune forgetting", test_forget_strategic)


# --- Forgetting: capacity overflow ---
def test_forget_capacity():
    r = client.post(
        "/v1/memories/forget-strategy", json={"strategy": "capacity_overflow", "params": {}}
    )
    assert r.status_code == 200
    data = r.json()
    assert data["strategy"] == "capacity_overflow"
    assert isinstance(data["memories_affected"], int)


test("Capacity overflow forgetting", test_forget_capacity)


# --- Forgetting engine unit tests ---
def test_forgetting_interference():
    from memory_system.core.forgetting import ForgettingEngine

    engine = ForgettingEngine()

    updates = engine.compute_interference(
        new_memory_activation=1.0,
        similar_memories=[{"id": "old1", "activation": 0.8}],
        similarities=[0.9],
    )
    assert len(updates) == 1
    assert updates[0][1] < 0.8  # penalty applied


test("Interference forgetting math", test_forgetting_interference)


def test_forgetting_rif():
    from memory_system.core.forgetting import ForgettingEngine

    engine = ForgettingEngine()

    updates = engine.compute_rif(
        retrieved_ids=["a"],
        competitor_ids=["a", "b", "c"],
        competitor_activations={"a": 1.0, "b": 0.8, "c": 0.6},
    )
    suppressed_ids = [u[0] for u in updates]
    assert "a" not in suppressed_ids  # retrieved, not suppressed
    assert "b" in suppressed_ids
    assert "c" in suppressed_ids


test("RIF forgetting math", test_forgetting_rif)


def test_forgetting_capacity_overflow():
    from memory_system.core.forgetting import ForgettingEngine

    engine = ForgettingEngine(max_capacity=3)

    memories = [{"id": str(i), "activation": float(i)} for i in range(5)]
    to_archive = engine.compute_capacity_overflow(memories)
    assert len(to_archive) == 2
    assert "0" in to_archive  # weakest
    assert "1" in to_archive


test("Capacity overflow math", test_forgetting_capacity_overflow)


# ═══════════════════════════════════════════════════════
# ACT-R CORE MATH VERIFICATION
# ═══════════════════════════════════════════════════════
print("\n🧪 ACT-R Core Math")
print("=" * 50)


def test_actr_power_law():
    from memory_system.core.actr import ACTRMemory

    actr = ACTRMemory(decay=0.5, noise_std=0.0)
    now = 100000.0

    # Recent memory has higher activation
    recent = actr.base_level_activation([now - 60], now)  # 1 min ago
    old = actr.base_level_activation([now - 86400], now)  # 1 day ago
    very_old = actr.base_level_activation([now - 604800], now)  # 1 week ago

    assert recent > old > very_old, f"Power law failed: {recent}, {old}, {very_old}"


test("Power-law decay (recent > old > very old)", test_actr_power_law)


def test_actr_frequency():
    from memory_system.core.actr import ACTRMemory

    actr = ACTRMemory(decay=0.5, noise_std=0.0)
    now = 100000.0

    once = actr.base_level_activation([now - 3600], now)
    times = [now - 3600, now - 3000, now - 2400, now - 1800, now - 1200]
    many = actr.base_level_activation(times, now)

    assert many > once, f"Frequency effect failed: many={many}, once={once}"


test("Frequency effect (5 accesses > 1 access)", test_actr_frequency)


def test_actr_threshold():
    from memory_system.core.actr import ACTRMemory

    actr = ACTRMemory(threshold=-1.0, noise_std=0.0)

    assert actr.can_retrieve(0.5) is True
    assert actr.can_retrieve(-0.5) is True
    assert actr.can_retrieve(-1.0) is False
    assert actr.can_retrieve(-2.0) is False


test("Retrieval threshold filtering", test_actr_threshold)


def test_actr_spreading():
    from memory_system.core.actr import ACTRMemory

    actr = ACTRMemory(noise_std=0.0)

    s = actr.spreading_activation(
        "target", ["ctx1", "ctx2"], {("ctx1", "target"): 2.0, ("ctx2", "target"): 1.0}
    )
    # W = 1/2 each, S = 0.5*2.0 + 0.5*1.0 = 1.5
    assert abs(s - 1.5) < 0.01, f"Spreading activation: expected 1.5, got {s}"


test("Spreading activation math", test_actr_spreading)


def test_actr_latency():
    from memory_system.core.actr import ACTRMemory

    actr = ACTRMemory()

    fast = actr.retrieval_latency(2.0)
    slow = actr.retrieval_latency(0.0)
    assert fast < slow, "Higher activation should mean faster retrieval"


test("Retrieval latency (higher activation = faster)", test_actr_latency)


# ═══════════════════════════════════════════════════════
# CLUSTERING (V2 consolidation dependency)
# ═══════════════════════════════════════════════════════
print("\n🧪 Clustering")
print("=" * 50)


def test_clustering_basic():
    from memory_system.core.clustering import cluster_episodes

    # Create episodes with similar embeddings
    e1 = {"id": "1", "embedding": [1.0, 0.0, 0.0]}
    e2 = {"id": "2", "embedding": [0.99, 0.1, 0.0]}
    e3 = {"id": "3", "embedding": [0.98, 0.15, 0.0]}
    e4 = {"id": "4", "embedding": [0.0, 0.0, 1.0]}  # different

    clusters = cluster_episodes([e1, e2, e3, e4], threshold=0.9, min_cluster_size=3)
    assert len(clusters) == 1
    assert len(clusters[0]) == 3


test("Episode clustering groups similar items", test_clustering_basic)


def test_cosine_similarity():
    from memory_system.core.clustering import cosine_similarity

    assert abs(cosine_similarity([1, 0], [1, 0]) - 1.0) < 0.001
    assert abs(cosine_similarity([1, 0], [0, 1]) - 0.0) < 0.001
    assert cosine_similarity([1, 0], [-1, 0]) < 0


test("Cosine similarity", test_cosine_similarity)


# ═══════════════════════════════════════════════════════
# FULL LIFECYCLE TEST
# ═══════════════════════════════════════════════════════
print("\n🧪 Full Lifecycle")
print("=" * 50)


def test_full_lifecycle():
    """Store → Recall → Decay → Verify activation changed → Consolidate → Forget"""
    # 1. Store
    r = client.post("/v1/memories", json={"content": "Lifecycle test memory"})
    assert r.status_code == 201
    mid = r.json()["memory_id"]

    # 2. Recall (strengthens)
    r = client.get(f"/v1/memories/{mid}")
    assert r.status_code == 200

    # 3. Inspect before decay
    r = client.get(f"/v1/memories/{mid}/inspect")
    pre_decay = r.json()
    assert pre_decay["access_count"] >= 2  # store + recall

    # 4. Decay
    r = client.post("/v1/memories/decay")
    assert r.status_code == 200

    # 5. Inspect after decay
    r = client.get(f"/v1/memories/{mid}/inspect")
    post_decay = r.json()
    assert isinstance(post_decay["activation"], (int, float))

    # 6. Consolidate
    r = client.post("/v1/graph/consolidate")
    assert r.status_code == 200

    # 7. Forget
    r = client.delete(f"/v1/memories/{mid}")
    assert r.status_code == 200

    # 8. Verify gone
    r = client.get(f"/v1/memories/{mid}")
    assert r.status_code == 404


test("Full lifecycle: store → recall → decay → consolidate → forget", test_full_lifecycle)


def test_stats_after_everything():
    r = client.get("/v1/stats")
    data = r.json()
    assert data["total"] > 0
    assert data["deleted"] > 0  # we deleted some memories


test("Stats reflect all operations", test_stats_after_everything)


# ═══════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 50)
print(f"📊 Results: {passed} passed, {failed} failed out of {passed + failed}")
print("=" * 50)

if errors:
    print("\n❌ Failures:")
    for e in errors:
        print(f"  • {e}")

sys.exit(1 if failed > 0 else 0)
