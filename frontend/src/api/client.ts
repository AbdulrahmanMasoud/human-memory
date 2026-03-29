const BASE = import.meta.env.VITE_API_URL || ''

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status}: ${text}`)
  }
  return res.json()
}

export function streamApi(path: string, body: object): ReadableStream<BenchmarkChunk> {
  return new ReadableStream({
    async start(controller) {
      const res = await fetch(`${BASE}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
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
          if (line.startsWith('data: ')) {
            controller.enqueue(JSON.parse(line.slice(6)))
          }
        }
      }
      controller.close()
    },
  })
}

interface BenchmarkChunk {
  phase: string
  [key: string]: unknown
}
