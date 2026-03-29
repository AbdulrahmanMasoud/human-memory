<template>
  <div class="flex items-center gap-2">
    <div class="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
      <div class="h-full rounded-full transition-all duration-300" :style="{ width: pct + '%', backgroundColor: barColor }"></div>
    </div>
    <span class="text-xs text-slate-400">{{ activation.toFixed(2) }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ activation: number; status?: string }>()
const pct = computed(() => Math.max(0, Math.min(100, ((props.activation + 2) / 4) * 100)))
const barColor = computed(() => {
  if (props.status === 'decayed') return '#ef4444'
  if (props.status === 'deleted') return '#6b7280'
  return '#22c55e'
})
</script>
