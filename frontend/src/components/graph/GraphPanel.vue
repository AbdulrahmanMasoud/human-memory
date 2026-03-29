<template>
  <div class="p-6 max-w-6xl mx-auto">
    <h2 class="text-xl font-semibold mb-4">Knowledge Graph</h2>

    <div v-if="error" class="rounded-lg bg-blue-900/20 border border-blue-800 p-4 text-blue-300 text-sm mb-4">
      {{ error }}
      <button class="ml-2 underline" @click="load">Retry</button>
    </div>

    <div v-else class="relative rounded-xl bg-slate-800 border border-slate-700 overflow-hidden">
      <svg ref="svgRef" class="w-full" style="height: 500px"></svg>

      <!-- Detail sidebar -->
      <Transition name="slide">
        <div v-if="selectedNode" class="absolute top-3 right-3 w-72 bg-slate-900 border border-slate-700 rounded-xl p-4">
          <div class="flex justify-between items-start mb-2">
            <h3 class="text-brand font-semibold">{{ selectedNode.name }}</h3>
            <button class="text-slate-500 hover:text-slate-300" @click="selectedNode = null">✕</button>
          </div>
          <div class="text-xs text-slate-400 mb-2">Type: {{ selectedNode.type }} | Activation: {{ selectedNode.activation?.toFixed(3) }}</div>
          <div v-if="spreadResults.length" class="mt-3">
            <div class="text-xs text-slate-400 font-semibold mb-1">Spreading Activation:</div>
            <div v-for="s in spreadResults" :key="s.name" class="text-xs text-slate-300 flex justify-between">
              <span>{{ s.name }}</span>
              <span class="text-yellow-400">{{ s.path_weight.toFixed(3) }}</span>
            </div>
          </div>
        </div>
      </Transition>

      <div v-if="graph.nodes.length === 0 && !loading" class="absolute inset-0 flex items-center justify-center text-slate-500 text-sm">
        No concepts yet. Create some via the API.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import * as d3 from 'd3'
import { useGraph } from '@/composables/useGraph'
import type { GraphNode } from '@/api/types'

const { graph, loading, error, spreadResults, load, spreadingActivation } = useGraph()
const svgRef = ref<SVGSVGElement>()
const selectedNode = ref<GraphNode | null>(null)

const TYPE_COLORS: Record<string, string> = {
  language: '#3b82f6', tool: '#22c55e', field: '#f59e0b',
  framework: '#a78bfa', concept: '#6b7280', entity: '#e94560',
  fact: '#ec4899', test: '#06b6d4',
}

function renderGraph() {
  if (!svgRef.value || !graph.value.nodes.length) return

  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()

  const width = svgRef.value.clientWidth
  const height = 500
  svg.attr('viewBox', [0, 0, width, height] as any)

  const nodes = graph.value.nodes.map(d => ({ ...d }))
  const edges = graph.value.edges.map(d => ({ ...d }))

  const sim = d3.forceSimulation(nodes as any)
    .force('link', d3.forceLink(edges as any).id((d: any) => d.name).distance(120))
    .force('charge', d3.forceManyBody().strength(-250))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide(35))

  const g = svg.append('g')
  svg.call(d3.zoom<SVGSVGElement, unknown>().on('zoom', (e) => g.attr('transform', e.transform)) as any)

  const link = g.selectAll('.link').data(edges).join('line')
    .attr('stroke', '#334155').attr('stroke-width', (d: any) => Math.max(1, (d.weight ?? 0.5) * 3))

  const linkLabel = g.selectAll('.link-label').data(edges).join('text')
    .attr('text-anchor', 'middle').attr('fill', '#64748b').attr('font-size', '9px')
    .text((d: any) => d.relation_type)

  const node = g.selectAll('.node').data(nodes).join('g')
    .call(d3.drag<any, any>()
      .on('start', (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
      .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y })
      .on('end', (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null }))

  node.append('circle')
    .attr('r', (d: any) => Math.max(8, (d.activation ?? 0.5) * 18))
    .attr('fill', (d: any) => TYPE_COLORS[d.type] || '#6b7280')
    .attr('stroke', '#1e293b').attr('stroke-width', 2)
    .attr('cursor', 'pointer')

  node.append('text')
    .attr('dy', -14).attr('text-anchor', 'middle').attr('fill', '#e2e8f0').attr('font-size', '11px')
    .text((d: any) => d.name)

  node.on('click', async (_: any, d: any) => {
    selectedNode.value = d
    await spreadingActivation([d.name])
  })

  sim.on('tick', () => {
    link.attr('x1', (d: any) => d.source.x).attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x).attr('y2', (d: any) => d.target.y)
    linkLabel.attr('x', (d: any) => (d.source.x + d.target.x) / 2).attr('y', (d: any) => (d.source.y + d.target.y) / 2)
    node.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
  })
}

onMounted(async () => { await load(); renderGraph() })
watch(() => graph.value, renderGraph, { deep: true })
</script>
