// Mirrors Pydantic models from src/memory_system/models/

export interface MemoryStats {
  total: number
  active: number
  decayed: number
  deleted: number
  avg_activation: number
}

export interface ReadyResponse {
  status: string
  checks: Record<string, string>
}

export interface MemoryCreateResponse {
  memory_id: string
  activation: number
  created_at: string
}

export interface MemoryResponse {
  memory_id: string
  content: string
  activation: number
  memory_type: string
  created_at: string
  last_accessed: string
  access_count: number
}

export interface MemorySearchResult {
  memory_id: string
  content: string
  activation: number
  similarity: number
  last_accessed: string
  access_count: number
}

export interface MemorySearchResponse {
  results: MemorySearchResult[]
  count: number
}

export interface AccessRecord {
  accessed_at: string
  context: string | null
}

export interface MemoryDetail {
  memory_id: string
  content: string
  memory_type: string
  created_at: string
  last_accessed: string
  access_count: number
  activation: number
  salience: number
  emotion_valence: number
  emotion_arousal: number
  decay_rate: number
  status: string
  access_history: AccessRecord[]
}

export interface MemoryListItem {
  memory_id: string
  content: string
  memory_type: string
  activation: number
  salience: number
  status: string
  access_count: number
  created_at: string
  last_accessed: string
}

export interface MemoryListResponse {
  memories: MemoryListItem[]
  offset: number
  limit: number
}

export interface DecayResponse {
  memories_processed: number
  memories_decayed: number
}

export interface ConsolidationReport {
  episodes_replayed: number
  facts_extracted: number
  memories_pruned: number
  memories_downscaled: number
  phase_4_compiled: number
}

export interface ForgetStrategyResponse {
  strategy: string
  memories_affected: number
}

export interface ConceptResponse {
  name: string
  type: string
  activation: number
  relationships: RelationResponse[]
}

export interface RelationResponse {
  source: string
  target: string
  relation_type: string
  weight: number
}

export interface GraphSearchResult {
  name: string
  activation: number
  path_weight: number
}

export interface GraphExport {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface GraphNode {
  name: string
  type: string
  activation: number
}

export interface GraphEdge {
  source: string
  target: string
  relation_type: string
  weight: number
}

export interface BenchmarkEvent {
  phase: 'store' | 'retrieve' | 'complete'
  progress?: number
  total_stored?: number
  total_searched?: number
  batch_avg_ms?: number
  p50?: number
  p95?: number
  p99?: number
  total_memories?: number
  total_time_ms?: number
  store?: { count: number; p50: number; p95: number; p99: number; avg_ms: number }
  retrieve?: { count: number; p50: number; p95: number; p99: number; avg_ms: number }
}
