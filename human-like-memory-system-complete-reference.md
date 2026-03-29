# Human-Like Memory System for AI Agents
## Complete Knowledge Reference

**Purpose**: This document is the complete knowledge base for building a Human-Like Memory System for AI Agents, inspired by ACT-R Cognitive Architecture. It covers all foundational knowledge across cognitive science, infrastructure, AI/LLM integration, system design, and implementation.

**Based on**: ACT-R Cognitive Architecture (Anderson), Eysenck & Keane Cognitive Psychology (8th Ed.), and modern AI engineering practices.

---

# PHASE 1: COGNITIVE SCIENCE FOUNDATIONS

---

## 1.1 Human Memory Systems — Overview

### The Core Question: Why Does the Brain Need Multiple Memory Types?

The human brain doesn't use a single memory system — it uses at least 5 distinct but interconnected systems. Each evolved to solve a different computational problem:

**The Atkinson-Shiffrin Multi-Store Model (1968)** proposes three stages:
- **Sensory Register**: Holds raw sensory input for milliseconds (~250ms for visual, ~2-4s for auditory). Massive capacity but ultra-short duration. Only attended items pass to the next stage.
- **Short-Term Memory (STM)**: Limited capacity (7±2 items per Miller, 1956), limited duration (~15-30 seconds without rehearsal). Information here is actively being processed.
- **Long-Term Memory (LTM)**: Potentially unlimited capacity and duration. Information transfers here through encoding processes (especially deep/semantic processing).

**Evidence for Separation**:
- Patient HM (Henry Molaison): After bilateral hippocampus removal, he could not form new long-term memories but his short-term memory and pre-existing long-term memories were intact. This proves STM and LTM are separate systems.
- Double dissociation: Some patients have impaired STM but intact LTM (e.g., patient KF), while others (amnesics) have impaired LTM but intact STM.

### Baddeley's Working Memory Model (2000)

Baddeley argued STM is not a passive store but an active workspace with 4 components:

1. **Central Executive**: An attention-control system that directs processing, switches focus, and coordinates the slave systems. It has limited capacity and is the most important component.
2. **Phonological Loop**: Processes and briefly stores speech-based/acoustic information. Has two sub-components: phonological store (holds sounds for ~2 seconds) and articulatory rehearsal process (refreshes them via inner speech).
3. **Visuospatial Sketchpad**: Processes and temporarily stores visual and spatial information (images, locations, movements).
4. **Episodic Buffer**: Added in 2000. A limited-capacity store that integrates information from the other components and from long-term memory into coherent episodes. It binds information across domains (visual + verbal + temporal).

**AI System Mapping**:
- Sensory Register → Sensory Buffer (raw input, auto-decays)
- Working Memory → Active Context Window (capacity-limited, attention-gated)
- Central Executive → Retrieval Controller (decides what to attend to)
- LTM → Episodic + Semantic + Procedural stores

---

## 1.2 ACT-R Cognitive Architecture

### What is ACT-R?

ACT-R (Adaptive Control of Thought—Rational) is a cognitive architecture developed by John Anderson at Carnegie Mellon University. It provides a unified theory of cognition with mathematical equations for how memory works.

### The Activation Equation

Every memory chunk in ACT-R has an **activation level** that determines how quickly and accurately it can be retrieved. The total activation of chunk i is:

```
A_i = B_i + S_i + P_i + ε
```

Where:
- **A_i** = Total activation of chunk i
- **B_i** = Base-level activation (recency and frequency)
- **S_i** = Spreading activation from current context
- **P_i** = Partial matching penalty/bonus
- **ε** = Stochastic noise (adds randomness, like human variability)

### Base-Level Activation (B_i)

This captures the effects of practice (frequency) and recency:

```
B_i = ln(Σ(j=1 to n) t_j^(-d))
```

Where:
- **n** = number of times chunk i has been accessed
- **t_j** = time since the j-th access (in seconds)
- **d** = decay rate parameter (typically ~0.5)

**Key insight**: This produces a **power-law decay** — memories fade quickly at first, then more slowly. This matches Ebbinghaus's forgetting curve perfectly. Also, more frequently accessed memories have higher activation (the summation grows with n).

**Example**: A memory accessed 10 times in the last hour has much higher activation than one accessed once a year ago. But a memory accessed once yesterday still has more activation than one accessed once a year ago — recency matters.

### Spreading Activation (S_i)

Currently active chunks in working memory "spread" activation to related chunks in long-term memory:

```
S_i = Σ(k) W_k × S_ki
```

Where:
- **W_k** = attentional weight on source chunk k (limited total attention)
- **S_ki** = strength of association between source k and chunk i

**Key insight**: Context matters. If you're thinking about "cooking," all cooking-related memories get an activation boost, making them easier to retrieve. This is why walking into your kitchen helps you remember what you went there for.

### Partial Matching (P_i)

When the retrieval cue doesn't exactly match a chunk, there's a similarity-based penalty:

```
P_i = Σ(l) P × Match(desired_l, actual_l)
```

Where P is a mismatch penalty parameter and Match returns similarity. Perfect matches contribute 0, mismatches contribute negative values.

**Key insight**: This explains interference — similar memories compete and can be confused with each other.

### Retrieval Threshold (τ)

A chunk can only be retrieved if its activation exceeds a threshold τ:
- A_i > τ → Retrieved (the higher the activation, the faster the retrieval)
- A_i ≤ τ → Retrieval failure (the memory is "forgotten" — not deleted, just inaccessible)

### Retrieval Latency

The time to retrieve a chunk is:
```
T_i = F × e^(-A_i)
```

Where F is a scaling parameter. Higher activation = faster retrieval.

**AI System Implementation**:
```python
import math
import time

class ACTRMemory:
    def __init__(self, decay=0.5, noise_std=0.25, threshold=-1.0):
        self.decay = decay
        self.noise_std = noise_std
        self.threshold = threshold
    
    def base_level_activation(self, access_times, current_time):
        """Calculate B_i using ACT-R equation"""
        if not access_times:
            return float('-inf')
        total = 0
        for t in access_times:
            age = max(current_time - t, 0.001)  # avoid division by zero
            total += age ** (-self.decay)
        return math.log(max(total, 1e-10))
    
    def spreading_activation(self, chunk, context_chunks, association_strengths):
        """Calculate S_i from current context"""
        n = len(context_chunks)
        if n == 0:
            return 0
        W = 1.0 / n  # Equal attention weight
        total = 0
        for ctx in context_chunks:
            key = (ctx.id, chunk.id)
            S_ki = association_strengths.get(key, 0)
            total += W * S_ki
        return total
    
    def total_activation(self, chunk, context, associations, current_time):
        """Calculate total activation A_i"""
        B = self.base_level_activation(chunk.access_times, current_time)
        S = self.spreading_activation(chunk, context, associations)
        noise = random.gauss(0, self.noise_std)
        return B + S + noise
    
    def can_retrieve(self, activation):
        """Check if activation exceeds threshold"""
        return activation > self.threshold
```

---

## 1.3 Memory Consolidation & Sleep

### Complementary Learning Systems Theory (McClelland et al., 1995)

The brain has two learning systems that work together:

1. **Hippocampus** (fast learner): Rapidly encodes new episodic memories. But it has limited capacity and memories stored here are fragile.
2. **Neocortex** (slow learner): Gradually acquires structured knowledge (semantic memory). It learns slowly to avoid catastrophic interference (new learning destroying old knowledge).

**The Transfer Process**: During sleep (especially Slow-Wave Sleep / SWS), the hippocampus "replays" recent experiences to the neocortex, gradually transferring and integrating them into the existing knowledge structure. This is **consolidation**.

### Sleep Phases and Memory

- **SWS (Slow-Wave Sleep)**: Primarily consolidates declarative memories (facts and events). Hippocampal replay occurs here.
- **REM Sleep**: Primarily consolidates procedural memories and emotional processing. Also involved in creative problem-solving (forming novel associations).

### Synaptic Homeostasis Hypothesis (Tononi & Cirelli)

During waking, synapses are strengthened through learning (potentiation). During sleep, there's a global downscaling of synaptic strength. This means:
- Weak connections (unimportant memories) fall below threshold → forgotten
- Strong connections (important/repeated memories) survive the downscaling → consolidated
- Overall metabolic cost is reduced → the brain is "refreshed"

### Memory Replay

During SWS, neural patterns from waking experiences are reactivated at high speed (compressed replay). This serves to:
1. Strengthen important memories
2. Extract statistical regularities (patterns)
3. Integrate new information with existing knowledge
4. Transform episodic memories into semantic knowledge

**AI System Implementation**:
```python
class ConsolidationEngine:
    def __init__(self, schedule="0 */6 * * *"):  # Every 6 hours
        self.schedule = schedule
    
    async def run_cycle(self):
        """4-phase consolidation cycle"""
        # Phase 1: REPLAY — Reactivate and strengthen high-salience memories
        recent_episodes = await self.get_recent_episodes(hours=6)
        for ep in recent_episodes:
            if ep.salience > 0.6:
                ep.activation += REPLAY_BOOST
                await self.store.update(ep)
        
        # Phase 2: EXTRACT — Find patterns, create semantic knowledge
        clusters = await self.cluster_similar_episodes(recent_episodes)
        for cluster in clusters:
            if len(cluster) >= MIN_PATTERN_SIZE:
                semantic = self.abstract_to_knowledge(cluster)
                await self.semantic_store.upsert(semantic)
        
        # Phase 3: PRUNE — Apply global downscaling (synaptic homeostasis)
        all_memories = await self.store.get_all_active()
        for mem in all_memories:
            mem.activation *= DOWNSCALE_FACTOR  # e.g., 0.9
            if mem.activation < FORGET_THRESHOLD:
                await self.store.archive(mem)  # Soft delete
        
        # Phase 4: COMPILE — Convert repeated successful patterns to skills
        patterns = self.find_repeated_action_patterns(recent_episodes)
        for pattern in patterns:
            if pattern.success_rate > 0.8 and pattern.count >= 3:
                skill = self.compile_to_procedural(pattern)
                await self.procedural_store.add(skill)
```

---

## 1.4 Forgetting: Theories & Mechanisms

### Why Forgetting is a Feature, Not a Bug

Forgetting is an adaptive mechanism. Without it:
- Retrieval would be overwhelmed (too many competing memories)
- Irrelevant information would interfere with relevant information
- The system would waste resources maintaining useless data

### Ebbinghaus Forgetting Curve (1885)

Ebbinghaus found that forgetting follows a **power law** — rapid initial forgetting, then gradual leveling off:
```
R = e^(-t/S)
```
Where R is retention, t is time, and S is memory strength.

After 1 hour: ~56% forgotten. After 1 day: ~67% forgotten. After 1 week: ~75% forgotten. After 1 month: ~79% forgotten. But it levels off — old memories that survive become increasingly stable.

### Interference Theory

Two types of interference cause forgetting:

1. **Proactive Interference**: Old memories interfere with new learning. Example: You learned Spanish first, now learning French — Spanish words keep intruding when you try to speak French.
2. **Retroactive Interference**: New learning interferes with old memories. Example: After learning your new phone number, you struggle to remember your old one.

### Retrieval-Induced Forgetting (Anderson et al., 1994)

Practicing retrieval of some memories actively suppresses competing memories. If you have memories A, B, C all associated with cue X, repeatedly retrieving A when given X will weaken B and C.

**Key insight**: This is not passive decay — it's active inhibition. The brain suppresses competitors to make retrieval more efficient.

### Bjork's New Theory of Disuse

Bjork distinguishes between:
- **Storage strength**: How well-encoded a memory is (only increases, never decreases)
- **Retrieval strength**: How accessible a memory is right now (fluctuates based on recency/context)

A memory can have high storage strength but low retrieval strength — it's there, you just can't access it right now. The right cue can bring it back.

### Directed/Strategic Forgetting

The brain can intentionally suppress memories:
- **Item-method**: When told to forget a specific item immediately after seeing it, people show reduced memory for it.
- **List-method**: When told to forget an entire list, people show reduced memory for that list but improved memory for subsequently learned material.

**AI System Forgetting Types**:
```python
class ForgettingEngine:
    def temporal_decay(self, memory, current_time):
        """Power-law decay based on ACT-R"""
        age = current_time - memory.last_accessed
        memory.activation *= (age + 1) ** (-memory.decay_rate)
    
    def interference(self, memory, similar_memories):
        """New similar memories weaken old ones"""
        for similar in similar_memories:
            if similar.created_at > memory.created_at:
                overlap = self.compute_similarity(memory, similar)
                memory.activation -= overlap * INTERFERENCE_PENALTY
    
    def retrieval_induced(self, retrieved_memory, competitors):
        """Retrieving one memory suppresses competitors"""
        for comp in competitors:
            if comp.id != retrieved_memory.id:
                comp.activation -= RIF_PENALTY
    
    def strategic_prune(self, memories, current_goals):
        """Goal-directed forgetting — remove irrelevant memories"""
        for mem in memories:
            relevance = self.compute_goal_relevance(mem, current_goals)
            if relevance < RELEVANCE_THRESHOLD:
                mem.activation *= PRUNE_FACTOR
    
    def capacity_overflow(self, store, max_capacity):
        """When store is full, remove weakest memories"""
        if len(store) > max_capacity:
            store.sort(key=lambda m: m.activation)
            to_remove = store[:len(store) - max_capacity]
            for mem in to_remove:
                store.archive(mem)
```

---

## 1.5 Emotion & Memory — The Amygdala Effect

### Valence-Arousal Model (Russell's Circumplex Model)

Emotions can be described along two dimensions:
- **Valence**: Positive ↔ Negative (pleasure vs. displeasure)
- **Arousal**: High ↔ Low (excitement vs. calm)

This creates a 2D space where any emotion can be plotted:
- Happy: positive valence, moderate arousal
- Excited: positive valence, high arousal
- Angry: negative valence, high arousal
- Sad: negative valence, low arousal
- Calm: positive valence, low arousal

### How Emotions Strengthen Memory

The **amygdala** (emotion center) modulates the **hippocampus** (memory encoding center):
1. Emotional events trigger amygdala activation
2. The amygdala releases noradrenaline, which enhances hippocampal encoding
3. This results in stronger, more vivid, more durable memories
4. Both positive and negative high-arousal events benefit — but negative slightly more

### Flashbulb Memories

Extremely emotional events (e.g., 9/11, personal trauma) create vivid, seemingly photographic memories. However, research shows these memories are not necessarily more accurate — they just feel more vivid and are more confidently held.

**AI System Implementation**:
```python
class EmotionalSalience:
    def __init__(self, alpha=0.4, beta=0.3, gamma=0.2, delta=0.1):
        self.alpha = alpha  # valence weight
        self.beta = beta    # arousal weight
        self.gamma = gamma  # goal relevance weight
        self.delta = delta  # novelty weight
    
    def compute(self, event):
        """Compute emotional salience score (0-1)"""
        emotional = (
            self.alpha * abs(event.valence) +
            self.beta * event.arousal
        )
        contextual = (
            self.gamma * event.goal_relevance +
            self.delta * (1.0 if event.is_novel else 0.0)
        )
        return min(1.0, emotional + contextual)
    
    def modify_decay_rate(self, base_decay, salience):
        """High-salience memories decay slower"""
        protection_factor = 1.0 + salience * 2.0
        return base_decay / protection_factor
    
    def compute_retrieval_boost(self, salience):
        """High-salience memories get retrieval bonus"""
        return salience * EMOTION_BOOST_FACTOR
```

---

# PHASE 2: INFRASTRUCTURE — DATABASES & VECTOR SEARCH

---

## 2.1 Vector Embeddings & Similarity Search

### What Are Embeddings?

An embedding is a dense numerical vector representation of data (text, image, etc.) in a high-dimensional space (typically 384-1536 dimensions). Semantically similar items have vectors that are close together.

### How Embeddings Work

1. A neural network (e.g., sentence-transformer) processes input text
2. It outputs a fixed-size vector (e.g., 768 dimensions for all-MiniLM-L6-v2)
3. Similar meanings produce similar vectors, regardless of exact wording
4. "I love programming" and "Coding is my passion" → vectors close together

### Similarity Metrics

- **Cosine Similarity**: Measures the angle between vectors. Range: -1 to 1. Most common for text.
  ```
  cos(A, B) = (A · B) / (||A|| × ||B||)
  ```
- **Dot Product**: Like cosine but also considers magnitude. Faster to compute.
- **L2 (Euclidean) Distance**: Straight-line distance between vectors. Lower = more similar.

### Approximate Nearest Neighbor (ANN)

Exact nearest neighbor search is O(n) — too slow for millions of vectors. ANN algorithms trade accuracy for speed:

- **HNSW (Hierarchical Navigable Small World)**: Graph-based. Best overall accuracy/speed tradeoff. Used by Qdrant, Weaviate.
- **IVF (Inverted File Index)**: Cluster-based. Faster for very large datasets.
- **Product Quantization**: Compresses vectors. Uses less memory but lower accuracy.

### Choosing an Embedding Model

For the memory system, consider:
- **sentence-transformers/all-MiniLM-L6-v2**: 384 dims, fast, good quality, free, runs locally
- **OpenAI text-embedding-3-small**: 1536 dims, excellent quality, paid API
- **Cohere embed-v3**: Good multilingual support
- **BGE-M3**: State-of-the-art open-source, multilingual

**AI System Usage**: Every memory chunk gets embedded at creation time. The embedding enables semantic search as the first stage of retrieval, before ACT-R activation scoring refines the results.

---

## 2.2 Vector Databases

### Why Not Just PostgreSQL?

Regular databases can store vectors, but dedicated vector databases are optimized for:
- Fast ANN search over millions of vectors
- Metadata filtering combined with vector search (hybrid queries)
- Real-time updates without index rebuilding
- Scalability and sharding

### Qdrant (Recommended for this project)

**Why Qdrant**:
- Rich metadata filtering (needed for decay calculations on timestamps, salience scores, etc.)
- Excellent Python SDK
- Open source (self-hosted) or cloud managed
- Supports payload indexing (fast filter on metadata fields)
- Built-in collection management

**Key Qdrant Concepts**:
- **Collection**: A group of points (like a database table)
- **Point**: A vector + payload (metadata) + ID
- **Payload**: JSON metadata stored alongside each vector
- **Filter**: Conditions on payload fields during search

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, Range

client = QdrantClient(host="localhost", port=6333)

# Create collection for episodic memories
client.create_collection(
    collection_name="episodic_memories",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Store a memory
client.upsert(
    collection_name="episodic_memories",
    points=[PointStruct(
        id=1,
        vector=embedding_vector,  # 384-dim float array
        payload={
            "content": "User complained about slow API",
            "timestamp": 1700000000,
            "activation": 0.85,
            "salience": 0.7,
            "emotion_valence": -0.3,
            "emotion_arousal": 0.5,
            "access_count": 3,
            "type": "episodic"
        }
    )]
)

# Retrieve with combined vector similarity + metadata filter
results = client.search(
    collection_name="episodic_memories",
    query_vector=query_embedding,
    query_filter=Filter(must=[
        FieldCondition(key="activation", range=Range(gte=0.2)),  # Only active memories
        FieldCondition(key="type", match={"value": "episodic"})
    ]),
    limit=10
)
```

---

## 2.3 Knowledge Graphs — Neo4j

### Why a Knowledge Graph for Semantic Memory?

Semantic memory is inherently a graph — concepts connected by relationships:
- "Python" → [is_a] → "Programming Language"
- "Ahmed" → [works_with] → "Python"
- "Python" → [used_for] → "AI Development"

Graph databases naturally support:
- **Spreading activation**: Traverse connections to find related concepts
- **Hierarchical organization**: Superordinate/basic/subordinate categories
- **Relationship typing**: Different kinds of connections carry different meanings

### Neo4j Basics

```cypher
// Create nodes
CREATE (p:Concept {name: "Python", type: "language", activation: 0.9})
CREATE (ai:Concept {name: "AI", type: "field", activation: 0.85})
CREATE (u:Entity {name: "Ahmed", type: "user", activation: 0.95})

// Create relationships
CREATE (u)-[:USES {weight: 0.9, since: "2020"}]->(p)
CREATE (p)-[:USED_FOR {weight: 0.8}]->(ai)
CREATE (u)-[:INTERESTED_IN {weight: 0.85}]->(ai)

// Spreading activation query: Find concepts related to "Python" within 2 hops
MATCH (start:Concept {name: "Python"})-[r*1..2]-(related)
RETURN related.name, related.activation, 
       reduce(w = 1.0, rel IN r | w * rel.weight) AS spread_weight
ORDER BY spread_weight DESC
```

### Implementing Spreading Activation in Neo4j

```cypher
// Given a set of active concepts in working memory,
// find all connected concepts and compute spreading activation
UNWIND $active_concepts AS source_name
MATCH (source:Concept {name: source_name})-[r]-(target:Concept)
WITH target, 
     sum(r.weight * (1.0 / size($active_concepts))) AS spreading_activation
SET target.current_activation = target.base_activation + spreading_activation
RETURN target.name, target.current_activation
ORDER BY target.current_activation DESC
LIMIT 10
```

---

## 2.4 Time-Series Data & Temporal Queries

### The Problem

Every memory has temporal metadata:
- `created_at`: When the memory was formed
- `last_accessed`: When it was last retrieved
- `access_history`: Array of all access timestamps (needed for ACT-R B_i calculation)

Computing decay across thousands of memories needs to be efficient.

### PostgreSQL Approach

```sql
CREATE TABLE memory_metadata (
    memory_id UUID PRIMARY KEY,
    memory_type VARCHAR(20),
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    last_accessed TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 1,
    activation FLOAT DEFAULT 1.0,
    salience FLOAT DEFAULT 0.5,
    emotion_valence FLOAT DEFAULT 0.0,
    emotion_arousal FLOAT DEFAULT 0.3,
    decay_rate FLOAT DEFAULT 0.5,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE access_history (
    memory_id UUID REFERENCES memory_metadata(memory_id),
    accessed_at TIMESTAMP WITH TIME ZONE,
    context TEXT
);

-- Index for efficient temporal queries
CREATE INDEX idx_memory_activation ON memory_metadata(activation) WHERE status = 'active';
CREATE INDEX idx_memory_last_accessed ON memory_metadata(last_accessed);
CREATE INDEX idx_access_history ON access_history(memory_id, accessed_at);

-- Batch decay calculation
UPDATE memory_metadata
SET activation = LN(
    GREATEST(
        (SELECT SUM(POWER(EXTRACT(EPOCH FROM NOW() - ah.accessed_at) + 1, -decay_rate))
         FROM access_history ah WHERE ah.memory_id = memory_metadata.memory_id),
        0.0001
    )
),
status = CASE 
    WHEN activation < -2.0 THEN 'decayed' 
    ELSE 'active' 
END
WHERE status = 'active';
```

---

## 2.5 Background Jobs & Task Scheduling

### The Consolidation Scheduler

The consolidation engine runs as a periodic background job, similar to how sleep consolidation happens on a cycle.

### Celery + Redis Implementation

```python
from celery import Celery
from celery.schedules import crontab

app = Celery('memory_system', broker='redis://localhost:6379')

app.conf.beat_schedule = {
    'consolidation-cycle': {
        'task': 'memory.consolidation.run_full_cycle',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'decay-update': {
        'task': 'memory.decay.batch_update',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'capacity-check': {
        'task': 'memory.capacity.prune_overflow',
        'schedule': crontab(minute=0, hour='*/1'),  # Hourly
    },
}

@app.task
def run_full_cycle():
    engine = ConsolidationEngine()
    engine.replay()      # Phase 1
    engine.extract()     # Phase 2
    engine.prune()       # Phase 3
    engine.compile()     # Phase 4
```

---

# PHASE 3: AI & LLM LAYER

---

## 3.1 LLM APIs & Prompt Engineering

### Context Window as Working Memory

The LLM's context window IS the working memory — it has limited capacity and everything in it is "active." The memory system's job is to select what goes into this window.

### Memory-Augmented Prompting

```python
def build_prompt(user_query, retrieved_memories, agent_instructions):
    """Construct prompt with memory-augmented context"""
    
    # Sort memories by activation (highest first)
    sorted_memories = sorted(retrieved_memories, key=lambda m: m.activation, reverse=True)
    
    # Take top 7±2 (working memory capacity)
    working_set = sorted_memories[:7]
    
    # Build context section
    memory_context = "\n".join([
        f"[{m.type.upper()} | Activation: {m.activation:.2f} | "
        f"Age: {format_age(m.last_accessed)}] {m.content}"
        for m in working_set
    ])
    
    prompt = f"""
{agent_instructions}

## Relevant Memories (sorted by importance):
{memory_context}

## Current Query:
{user_query}

Respond using the relevant memories above as context. If memories contradict, 
prefer more recent and higher-activation ones.
"""
    return prompt
```

---

## 3.2 RAG — Retrieval Augmented Generation

### Standard RAG Pipeline

1. User query → Embed query → Search vector DB → Get top-K results → Inject into prompt → LLM generates response

### Why Standard RAG is Not Enough

Standard RAG treats all stored documents equally. A document from 3 years ago has the same retrieval chance as one from yesterday. There's no learning, no forgetting, no adaptation.

### Memory-Enhanced RAG (Our Approach)

Replace simple cosine similarity ranking with ACT-R activation:

```python
async def memory_enhanced_retrieve(query, context, top_k=10):
    # Step 1: Embed query
    query_embedding = embed(query)
    
    # Step 2: Broad vector search (cast wide net)
    candidates = await vector_db.search(query_embedding, limit=top_k * 3)
    
    # Step 3: Compute full ACT-R activation for each candidate
    current_time = time.time()
    for mem in candidates:
        B = actr.base_level_activation(mem.access_times, current_time)
        S = actr.spreading_activation(mem, context.active_chunks)
        P = actr.partial_match(mem, query)
        emotion_boost = mem.salience * EMOTION_FACTOR
        noise = random.gauss(0, NOISE_STD)
        mem.total_activation = B + S + P + emotion_boost + noise
    
    # Step 4: Filter by retrieval threshold
    retrievable = [m for m in candidates if m.total_activation > THRESHOLD]
    
    # Step 5: Sort by activation and take top-K
    retrievable.sort(key=lambda m: m.total_activation, reverse=True)
    result = retrievable[:top_k]
    
    # Step 6: Update access metadata (retrieval strengthens memory)
    for mem in result:
        await update_access(mem, current_time)
    
    return result
```

---

## 3.3 AI Agents — Architecture

### The Agent Loop

An AI agent operates in a continuous loop:
```
Perceive → Remember → Plan → Act → Learn → Repeat
```

The memory system plugs into "Remember" and "Learn":

```python
class MemoryAugmentedAgent:
    def __init__(self, llm, memory_system):
        self.llm = llm
        self.memory = memory_system
    
    async def process(self, user_input):
        # 1. PERCEIVE — Sensory input
        sensory = self.memory.sensory_buffer.add(user_input)
        
        # 2. ATTEND — Attention gate to working memory
        if self.attention_gate(sensory):
            self.memory.working_memory.add(sensory)
        
        # 3. REMEMBER — Retrieve relevant memories
        context = self.memory.working_memory.get_active()
        retrieved = await self.memory.retrieve(user_input, context)
        
        # 4. PLAN — Use LLM with memory context
        prompt = build_prompt(user_input, retrieved, self.instructions)
        response = await self.llm.generate(prompt)
        
        # 5. ACT — Deliver response
        yield response
        
        # 6. LEARN — Encode new memories
        episode = self.memory.encode_episode(
            input=user_input,
            output=response,
            context=context,
            emotion=self.detect_emotion(user_input)
        )
        await self.memory.episodic_store.add(episode)
```

---

## 3.4 Sentiment Analysis & Emotion Detection

### For Emotional Salience Scoring

```python
from transformers import pipeline

emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)

def detect_emotion(text):
    """Detect emotion and map to valence-arousal"""
    results = emotion_classifier(text)
    
    # Map emotion labels to valence-arousal
    emotion_map = {
        "joy":      {"valence": 0.8,  "arousal": 0.6},
        "surprise": {"valence": 0.3,  "arousal": 0.8},
        "anger":    {"valence": -0.7, "arousal": 0.8},
        "sadness":  {"valence": -0.6, "arousal": 0.3},
        "fear":     {"valence": -0.7, "arousal": 0.9},
        "disgust":  {"valence": -0.5, "arousal": 0.5},
        "neutral":  {"valence": 0.0,  "arousal": 0.2},
    }
    
    # Weighted average based on classifier confidence
    valence = sum(r["score"] * emotion_map[r["label"]]["valence"] for r in results[0])
    arousal = sum(r["score"] * emotion_map[r["label"]]["arousal"] for r in results[0])
    
    return {"valence": valence, "arousal": arousal}
```

---

## 3.5 LLM for Summarization & Abstraction

### Episodic → Semantic Conversion

```python
async def extract_semantic_knowledge(episodes: list[Episode]) -> list[SemanticFact]:
    """Use LLM to extract general knowledge from specific episodes"""
    
    episode_texts = "\n".join([
        f"- [{ep.timestamp}] {ep.content}" for ep in episodes
    ])
    
    prompt = f"""Analyze these related events and extract general knowledge/facts/patterns:

Events:
{episode_texts}

Extract:
1. General facts that are true across multiple events
2. Patterns or regularities
3. Causal relationships
4. User preferences or tendencies

Return as JSON array of {{fact, confidence, source_count}}"""
    
    response = await llm.generate(prompt, response_format="json")
    facts = json.loads(response)
    
    return [
        SemanticFact(
            content=f["fact"],
            confidence=f["confidence"],
            source_episodes=[ep.id for ep in episodes],
            activation=0.8 * f["confidence"]
        )
        for f in facts
    ]
```

---

# PHASE 4: SYSTEM DESIGN & INTEGRATION

---

## 4.1 Event-Driven Architecture

### Memory Event Flow

```
UserInput 
  → SensoryInputEvent 
    → AttentionGateEvent (pass/reject)
      → WorkingMemoryLoadEvent
        → EpisodicEncodeEvent
          → EmotionTagEvent
            → StorageCompleteEvent

RetrievalRequest
  → CandidateSearchEvent
    → ActivationComputeEvent
      → ThresholdFilterEvent
        → RetrievalCompleteEvent
          → AccessUpdateEvent (strengthens memory)

ConsolidationTrigger
  → ReplayPhaseEvent
    → ExtractionPhaseEvent
      → PrunePhaseEvent
        → CompilePhaseEvent
          → ConsolidationCompleteEvent
```

---

## 4.2 API Design

### Core API Surface

```python
class MemorySystemAPI:
    # === STORAGE ===
    async def store(self, content, type, emotion=None, metadata=None) -> MemoryID
    async def store_episode(self, input, output, context, emotion) -> EpisodeID
    
    # === RETRIEVAL ===
    async def retrieve(self, query, context=None, top_k=7, types=None) -> List[Memory]
    async def recall(self, memory_id) -> Memory  # Direct access by ID
    
    # === FORGETTING ===
    async def forget(self, memory_id) -> bool  # Strategic forget
    async def decay(self, memory_ids=None) -> int  # Apply temporal decay
    
    # === CONSOLIDATION ===
    async def consolidate(self, force=False) -> ConsolidationReport
    
    # === INSPECTION ===
    async def inspect(self, memory_id) -> MemoryDetail  # Full metadata
    async def stats() -> MemoryStats  # System-wide statistics
    async def search_graph(self, concept, depth=2) -> GraphResult
```

---

## 4.3 Testing & Evaluation

### Benchmarks to Prove the System Works

1. **Retrieval Precision/Recall**: Compare retrieved memories against ground truth relevant memories
2. **Temporal Relevance**: Does the system prefer recent memories when appropriate?
3. **Personalization Score**: After N interactions, does the system's responses become more personalized?
4. **Forgetting Efficiency**: Does strategic forgetting improve retrieval speed and accuracy?
5. **Consolidation Quality**: Are extracted semantic facts accurate?
6. **A/B vs Standard RAG**: Direct comparison on the same tasks

---

## 4.4 Concurrency & Performance

### Performance Targets

- Retrieval latency: < 100ms (p95)
- Storage latency: < 50ms
- Consolidation: Background, no impact on retrieval
- Decay updates: Batch, every 30 minutes

### Architecture

```
[FastAPI] → [Redis Cache] → [Qdrant] (vectors)
                          → [Neo4j] (graph)
                          → [PostgreSQL] (metadata)
           → [Celery Workers] → Consolidation jobs
                               → Decay calculations
                               → Skill compilation
```

---

# PHASE 5: IMPLEMENTATION ROADMAP

---

## 5.1 MVP: Episodic + Decay

**Scope**: Episodic Memory Store with ACT-R Temporal Decay
**Stack**: Python + FastAPI + Qdrant + PostgreSQL
**Duration**: ~1 week

Core features:
- Store events with embeddings + metadata
- Retrieve using vector similarity + ACT-R activation
- Apply temporal decay on a schedule
- Track access history for frequency-based activation

## 5.2 V2: + Semantic Memory + Consolidation

Add Knowledge Graph (Neo4j) and basic consolidation:
- Store extracted facts as graph nodes
- Implement spreading activation for retrieval
- Periodic consolidation: episode clustering → semantic extraction

## 5.3 V3: + Emotional Salience + Working Memory

Add emotion detection and working memory management:
- Score emotions on input using sentiment model
- Modify decay rates based on salience
- Implement 7±2 capacity limit for context injection

## 5.4 V4: + Procedural Memory + Strategic Forgetting

Full system with all 5 memory types:
- Procedural store for compiled skills
- 5 forgetting modes: decay, interference, RIF, strategic, overflow
- Full consolidation cycle: replay → extract → prune → compile

---

# APPENDIX: KEY EQUATIONS

```
ACT-R Total Activation:     A_i = B_i + S_i + P_i + ε
Base-Level Activation:      B_i = ln(Σ t_j^(-d))
Spreading Activation:       S_i = Σ W_k × S_ki
Retrieval Probability:      P(retrieve) = 1 / (1 + e^(-(A_i - τ)/s))
Retrieval Latency:          T = F × e^(-A_i)
Emotional Salience:         Sal = α|val| + β·aro + γ·rel + δ·nov
Forgetting Score:           F = (1 - activation) × (1 - salience) × age_factor
Ebbinghaus Curve:           R = e^(-t/S)
```

---

**Document Version**: 1.0
**Last Updated**: March 2026
**For**: Human-Like Memory System Project — AI Agent Reference
