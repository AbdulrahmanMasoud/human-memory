<template>
  <div class="rounded-xl bg-slate-800 border border-slate-700 p-5 transition-all hover:border-slate-600">
    <div class="text-xs text-slate-400 uppercase tracking-wide mb-1">{{ label }}</div>
    <div class="text-3xl font-bold" :class="colorClass">{{ formatted }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  value: number
  color?: 'green' | 'red' | 'blue' | 'yellow' | 'gray'
  format?: 'number' | 'decimal'
}>()

const colorClass = computed(() => {
  const map = { green: 'text-green-400', red: 'text-red-400', blue: 'text-blue-400', yellow: 'text-yellow-400', gray: 'text-slate-400' }
  return map[props.color ?? 'blue']
})

const formatted = computed(() => {
  if (props.format === 'decimal') return props.value.toFixed(3)
  return props.value.toLocaleString()
})
</script>
