<template>
  <div class="min-h-screen bg-slate-900 text-slate-200">
    <AppNav :active="activeTab" @select="activeTab = $event" @toggle-theme="toggleTheme" />
    <AppToast />

    <main>
      <OverviewPanel v-if="activeTab === 'overview'" :stats="stats" :ready="ready" />
      <GraphPanel v-if="activeTab === 'graph'" />
      <ExplorerPanel v-if="activeTab === 'explorer'" />
      <ControlsPanel v-if="activeTab === 'controls'" />
      <BenchmarkPanel v-if="activeTab === 'benchmark'" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useStats } from '@/composables/useStats'
import { useTheme } from '@/composables/useTheme'
import AppNav from '@/components/layout/AppNav.vue'
import AppToast from '@/components/layout/AppToast.vue'
import OverviewPanel from '@/components/overview/OverviewPanel.vue'
import GraphPanel from '@/components/graph/GraphPanel.vue'
import ExplorerPanel from '@/components/explorer/ExplorerPanel.vue'
import ControlsPanel from '@/components/controls/ControlsPanel.vue'
import BenchmarkPanel from '@/components/benchmark/BenchmarkPanel.vue'

const activeTab = ref('overview')
const { stats, ready } = useStats()
const { toggle: toggleTheme } = useTheme()

// Keyboard shortcuts
function onKeyDown(e: KeyboardEvent) {
  if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return
  const tabs = ['overview', 'graph', 'explorer', 'controls', 'benchmark']
  const num = parseInt(e.key)
  if (num >= 1 && num <= 5) activeTab.value = tabs[num - 1]
  if (e.key === '/') {
    e.preventDefault()
    activeTab.value = 'explorer'
    setTimeout(() => {
      const input = document.querySelector<HTMLInputElement>('input[placeholder*="Search"]')
      input?.focus()
    }, 100)
  }
}

onMounted(() => window.addEventListener('keydown', onKeyDown))
onUnmounted(() => window.removeEventListener('keydown', onKeyDown))
</script>
