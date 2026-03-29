<template>
  <span class="px-2 py-0.5 rounded-full text-xs font-semibold" :class="classes">{{ status }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ status: string }>()
const classes = computed(() => {
  if (props.status === 'active') return 'bg-green-500/15 text-green-400'
  if (props.status === 'decayed') return 'bg-red-500/15 text-red-400'
  return 'bg-slate-500/15 text-slate-400'
})
</script>
