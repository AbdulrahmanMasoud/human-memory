<template>
  <nav class="flex bg-slate-800 border-b border-slate-700">
    <div class="px-5 py-3 font-bold text-brand text-lg">🧠 Human Memory</div>
    <button
      v-for="tab in tabs"
      :key="tab.id"
      class="px-5 py-3 text-sm transition-colors border-b-2"
      :class="active === tab.id
        ? 'text-brand border-brand'
        : 'text-slate-400 border-transparent hover:text-slate-200 hover:bg-white/[0.03]'"
      @click="$emit('select', tab.id)"
    >
      {{ tab.icon }} {{ tab.label }}
    </button>
    <div class="flex-1" />
    <button class="px-4 text-slate-500 text-sm hover:text-slate-300" @click="$emit('toggleTheme')">
      🌓
    </button>
  </nav>
</template>

<script setup lang="ts">
defineProps<{ active: string }>()
defineEmits<{ select: [id: string]; toggleTheme: [] }>()

const tabs = [
  { id: 'overview', label: 'Overview', icon: '📊' },
  { id: 'graph', label: 'Knowledge Graph', icon: '🕸️' },
  { id: 'explorer', label: 'Memory Explorer', icon: '🔍' },
  { id: 'controls', label: 'Controls', icon: '⚙️' },
  { id: 'benchmark', label: 'Benchmark', icon: '🏎️' },
]
</script>
