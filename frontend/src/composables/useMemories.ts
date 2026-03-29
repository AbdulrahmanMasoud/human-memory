import { ref } from 'vue'
import { api } from '@/api/client'
import type { MemoryListItem, MemoryDetail, MemorySearchResult } from '@/api/types'

export function useMemories() {
  const memories = ref<MemoryListItem[]>([])
  const searchResults = ref<MemorySearchResult[]>([])
  const selected = ref<MemoryDetail | null>(null)
  const loading = ref(false)
  const isSearchMode = ref(false)
  let offset = 0

  async function load(reset = true) {
    if (reset) { offset = 0; memories.value = [] }
    loading.value = true
    isSearchMode.value = false
    try {
      const data = await api<{ memories: MemoryListItem[] }>(`/v1/memories?offset=${offset}&limit=50`)
      if (reset) memories.value = data.memories
      else memories.value = [...memories.value, ...data.memories]
    } finally { loading.value = false }
  }

  async function loadMore() {
    offset += 50
    await load(false)
  }

  async function search(query: string) {
    if (!query.trim()) return load()
    loading.value = true
    isSearchMode.value = true
    try {
      const data = await api<{ results: MemorySearchResult[]; count: number }>(
        '/v1/memories/search',
        { method: 'POST', body: JSON.stringify({ query, top_k: 50 }) },
      )
      searchResults.value = data.results
    } finally { loading.value = false }
  }

  async function inspect(id: string) {
    const data = await api<MemoryDetail>(`/v1/memories/${id}/inspect`)
    selected.value = data
  }

  function clearSelected() { selected.value = null }

  return { memories, searchResults, selected, loading, isSearchMode, load, loadMore, search, inspect, clearSelected }
}
