<template>
  <div class="p-6 max-w-6xl mx-auto">
    <h2 class="text-xl font-semibold mb-4">Benchmark</h2>

    <!-- Config -->
    <div class="rounded-xl bg-slate-800 border border-slate-700 p-5 mb-4">
      <div class="flex flex-wrap gap-4 items-end">
        <div>
          <label class="text-xs text-slate-400 block mb-1">Memories to store</label>
          <input v-model.number="count" type="number" min="10" max="50000" class="w-28 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="text-xs text-slate-400 block mb-1">Batch size</label>
          <input v-model.number="batchSize" type="number" min="1" max="500" class="w-20 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="text-xs text-slate-400 block mb-1">Search queries</label>
          <input v-model.number="searchCount" type="number" min="0" max="1000" class="w-20 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm" />
        </div>
        <button
          class="px-5 py-2 bg-brand text-white rounded-lg text-sm hover:bg-brand-hover disabled:opacity-50"
          :disabled="bench.running.value"
          @click="start"
        >
          {{ bench.running.value ? 'Running...' : 'Run Benchmark' }}
        </button>
      </div>

      <!-- Progress -->
      <div v-if="bench.running.value || bench.result.value" class="mt-4">
        <div class="w-full h-6 bg-slate-700 rounded-full overflow-hidden">
          <div
            class="h-full bg-brand rounded-full transition-all duration-300 flex items-center justify-center text-xs font-semibold text-white min-w-[40px]"
            :style="{ width: Math.round(bench.progress.value * 100) + '%' }"
          >
            {{ Math.round(bench.progress.value * 100) }}%
          </div>
        </div>
        <div class="flex gap-6 mt-2 text-sm text-slate-400">
          <span>Phase: <strong class="text-slate-200">{{ bench.phase.value }}</strong></span>
          <span>Stored: <strong class="text-slate-200">{{ bench.stored.value }}</strong></span>
          <span>Searched: <strong class="text-slate-200">{{ bench.searched.value }}</strong></span>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="rounded-xl bg-slate-800 border border-slate-700 p-5">
        <div class="text-xs text-slate-400 uppercase tracking-wide mb-3">Store Latency (ms)</div>
        <div class="h-52">
          <Bar :data="storeChartData" :options="chartOptions" />
        </div>
      </div>
      <div class="rounded-xl bg-slate-800 border border-slate-700 p-5">
        <div class="text-xs text-slate-400 uppercase tracking-wide mb-3">Retrieve Latency (ms)</div>
        <div class="h-52">
          <Bar :data="retrieveChartData" :options="chartOptions" />
        </div>
      </div>
    </div>

    <!-- Result JSON -->
    <pre
      v-if="bench.result.value"
      class="mt-4 bg-slate-900 border border-slate-700 rounded-xl p-4 text-xs text-slate-300 overflow-auto max-h-60"
    >{{ JSON.stringify(bench.result.value, null, 2) }}</pre>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip } from 'chart.js'
import { useBenchmark } from '@/composables/useBenchmark'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip)

const bench = useBenchmark()
const count = ref(1000)
const batchSize = ref(50)
const searchCount = ref(100)

function start() { bench.run(count.value, batchSize.value, searchCount.value) }

const storeChartData = computed(() => ({
  labels: ['p50', 'p95', 'p99'],
  datasets: [{ data: [bench.storeLatency.value.p50, bench.storeLatency.value.p95, bench.storeLatency.value.p99], backgroundColor: '#3b82f6', borderRadius: 4 }],
}))

const retrieveChartData = computed(() => ({
  labels: ['p50', 'p95', 'p99'],
  datasets: [{ data: [bench.retrieveLatency.value.p50, bench.retrieveLatency.value.p95, bench.retrieveLatency.value.p99], backgroundColor: '#22c55e', borderRadius: 4 }],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: { beginAtZero: true, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
    x: { ticks: { color: '#94a3b8' } },
  },
  plugins: { legend: { display: false } },
}
</script>
