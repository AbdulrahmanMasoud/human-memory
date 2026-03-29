import { ref } from 'vue'
import { api } from '@/api/client'
import type { GraphExport, GraphSearchResult } from '@/api/types'

export function useGraph() {
  const graph = ref<GraphExport>({ nodes: [], edges: [] })
  const loading = ref(false)
  const error = ref('')
  const spreadResults = ref<GraphSearchResult[]>([])

  async function load() {
    loading.value = true
    error.value = ''
    try {
      graph.value = await api<GraphExport>('/v1/graph/export')
    } catch (e: any) {
      error.value = e.message?.includes('503') ? 'Neo4j not connected' : String(e)
    } finally { loading.value = false }
  }

  async function spreadingActivation(concepts: string[]) {
    const data = await api<GraphSearchResult[]>('/v1/graph/search', {
      method: 'POST',
      body: JSON.stringify({ active_concepts: concepts, depth: 2, limit: 10 }),
    })
    spreadResults.value = data
    return data
  }

  return { graph, loading, error, spreadResults, load, spreadingActivation }
}
