<template>
  <div class="p-6 max-w-6xl mx-auto">
    <h2 class="text-xl font-semibold mb-4">
      System Overview
      <span class="text-xs text-slate-500 ml-2">Auto-refreshing</span>
    </h2>

    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
      <StatCard label="Total" :value="stats.total" color="blue" />
      <StatCard label="Active" :value="stats.active" color="green" />
      <StatCard label="Decayed" :value="stats.decayed" color="red" />
      <StatCard label="Deleted" :value="stats.deleted" color="gray" />
      <StatCard label="Avg Activation" :value="stats.avg_activation" color="yellow" format="decimal" />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Readiness -->
      <div class="rounded-xl bg-slate-800 border border-slate-700 p-5">
        <div class="text-xs text-slate-400 uppercase tracking-wide mb-3">System Readiness</div>
        <div class="flex flex-wrap gap-4 text-sm">
          <span v-for="(v, k) in ready.checks" :key="k">
            {{ k }}:
            <strong :class="v === 'ok' ? 'text-green-400' : 'text-red-400'">{{ v }}</strong>
          </span>
        </div>
      </div>

      <!-- Memory type breakdown -->
      <div class="rounded-xl bg-slate-800 border border-slate-700 p-5">
        <div class="text-xs text-slate-400 uppercase tracking-wide mb-3">Memory Distribution</div>
        <div class="h-48">
          <Doughnut v-if="stats.total > 0" :data="chartData" :options="chartOptions" />
          <div v-else class="flex items-center justify-center h-full text-slate-500 text-sm">No memories yet</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import StatCard from '@/components/shared/StatCard.vue'
import type { MemoryStats, ReadyResponse } from '@/api/types'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{ stats: MemoryStats; ready: ReadyResponse }>()

const chartData = computed(() => ({
  labels: ['Active', 'Decayed', 'Deleted'],
  datasets: [{
    data: [props.stats.active, props.stats.decayed, props.stats.deleted],
    backgroundColor: ['#22c55e', '#ef4444', '#6b7280'],
    borderWidth: 0,
  }],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' as const, labels: { color: '#94a3b8' } } },
}
</script>
