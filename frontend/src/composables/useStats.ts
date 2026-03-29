import { ref, onUnmounted } from 'vue'
import { api } from '@/api/client'
import type { MemoryStats, ReadyResponse } from '@/api/types'

export function useStats(intervalMs = 5000) {
  const stats = ref<MemoryStats>({ total: 0, active: 0, decayed: 0, deleted: 0, avg_activation: 0 })
  const ready = ref<ReadyResponse>({ status: 'unknown', checks: {} })
  const loading = ref(true)

  let timer: ReturnType<typeof setInterval> | null = null
  let ws: WebSocket | null = null

  async function refresh() {
    try {
      const [s, r] = await Promise.all([
        api<MemoryStats>('/v1/stats'),
        api<ReadyResponse>('/ready'),
      ])
      stats.value = s
      ready.value = r
      loading.value = false
    } catch { /* ignore */ }
  }

  function connectWebSocket() {
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    ws = new WebSocket(`${proto}//${location.host}/ws/stats`)
    ws.onmessage = (e) => {
      stats.value = JSON.parse(e.data)
      loading.value = false
    }
    ws.onclose = () => {
      ws = null
      // Fallback to polling
      if (!timer) timer = setInterval(refresh, intervalMs)
    }
    ws.onerror = () => ws?.close()
    // Stop polling if WS connects
    if (timer) { clearInterval(timer); timer = null }
  }

  // Try WebSocket first, fall back to polling
  refresh()
  try { connectWebSocket() } catch { /* ignore */ }
  timer = setInterval(refresh, intervalMs)

  onUnmounted(() => {
    if (timer) clearInterval(timer)
    ws?.close()
  })

  return { stats, ready, loading, refresh }
}
