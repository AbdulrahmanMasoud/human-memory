<template>
  <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 w-80">
    <TransitionGroup name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="rounded-lg px-4 py-3 text-sm shadow-lg border"
        :class="{
          'bg-green-900/80 border-green-700 text-green-200': t.type === 'success',
          'bg-red-900/80 border-red-700 text-red-200': t.type === 'error',
          'bg-blue-900/80 border-blue-700 text-blue-200': t.type === 'info',
        }"
      >
        {{ t.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { toast } from '@/composables/useToast'
const { toasts } = toast
</script>
