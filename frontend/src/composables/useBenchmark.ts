import { ref } from 'vue'
import type { BenchmarkEvent } from '@/api/types'

export function useBenchmark() {
  const running = ref(false)
  const phase = ref<string>('idle')
  const progress = ref(0)
  const stored = ref(0)
  const searched = ref(0)
  const storeLatency = ref({ p50: 0, p95: 0, p99: 0 })
  const retrieveLatency = ref({ p50: 0, p95: 0, p99: 0 })
  const result = ref<BenchmarkEvent | null>(null)

  async function run(count: number, batchSize: number, searchCount: number) {
    running.value = true
    result.value = null
    progress.value = 0
    stored.value = 0
    searched.value = 0
    phase.value = 'starting'

    const res = await fetch('/v1/benchmark/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ count, batch_size: batchSize, search_count: searchCount }),
    })

    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()!

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const ev: BenchmarkEvent = JSON.parse(line.slice(6))

        if (ev.phase === 'store') {
          phase.value = 'Storing'
          progress.value = ev.progress ?? 0
          stored.value = ev.total_stored ?? 0
          storeLatency.value = { p50: ev.p50 ?? 0, p95: ev.p95 ?? 0, p99: ev.p99 ?? 0 }
        } else if (ev.phase === 'retrieve') {
          phase.value = 'Searching'
          searched.value = ev.total_searched ?? 0
          retrieveLatency.value = { p50: ev.p50 ?? 0, p95: ev.p95 ?? 0, p99: ev.p99 ?? 0 }
        } else if (ev.phase === 'complete') {
          phase.value = 'Complete'
          progress.value = 1
          result.value = ev
        }
      }
    }
    running.value = false
  }

  return { running, phase, progress, stored, searched, storeLatency, retrieveLatency, result, run }
}
