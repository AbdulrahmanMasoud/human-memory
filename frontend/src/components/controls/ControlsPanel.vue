<template>
  <div class="p-6 max-w-6xl mx-auto">
    <h2 class="text-xl font-semibold mb-4">Decay & Consolidation Controls</h2>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Decay -->
      <div class="rounded-xl bg-slate-800 border border-slate-700 p-5">
        <div class="text-xs text-slate-400 uppercase tracking-wide mb-2">Temporal Decay</div>
        <p class="text-xs text-slate-500 mb-3">Recalculate activation using ACT-R B_i equation for all active memories.</p>
        <button class="w-full px-4 py-2 bg-brand text-white rounded-lg text-sm hover:bg-brand-hover" @click="runDecay">
          Run Decay
        </button>
        <pre v-if="decayResult" class="mt-3 bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-slate-300 overflow-auto max-h-40">{{ decayResult }}</pre>
      </div>

      <!-- Consolidation -->
      <div class="rounded-xl bg-slate-800 border border-slate-700 p-5">
        <div class="text-xs text-slate-400 uppercase tracking-wide mb-2">Consolidation Cycle</div>
        <p class="text-xs text-slate-500 mb-3">Run the 4-phase cycle: Replay → Extract → Prune → Compile.</p>
        <button class="w-full px-4 py-2 bg-brand text-white rounded-lg text-sm hover:bg-brand-hover" @click="runConsolidation">
          Run Consolidation
        </button>
        <pre v-if="consolResult" class="mt-3 bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-slate-300 overflow-auto max-h-40">{{ consolResult }}</pre>
      </div>

      <!-- Forgetting -->
      <div class="rounded-xl bg-slate-800 border border-slate-700 p-5">
        <div class="text-xs text-slate-400 uppercase tracking-wide mb-2">Strategic Forgetting</div>
        <p class="text-xs text-slate-500 mb-3">Apply a forgetting strategy to weaken irrelevant memories.</p>
        <select v-model="strategy" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm mb-2">
          <option value="strategic_prune">Strategic Prune</option>
          <option value="capacity_overflow">Capacity Overflow</option>
        </select>
        <input
          v-model="goals"
          placeholder="Goals (comma separated)"
          class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm mb-2"
        />
        <button class="w-full px-4 py-2 bg-brand text-white rounded-lg text-sm hover:bg-brand-hover" @click="runForget">
          Apply
        </button>
        <pre v-if="forgetResult" class="mt-3 bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-slate-300 overflow-auto max-h-40">{{ forgetResult }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from '@/api/client'
import { toast } from '@/composables/useToast'
import type { DecayResponse, ConsolidationReport, ForgetStrategyResponse } from '@/api/types'

const decayResult = ref('')
const consolResult = ref('')
const forgetResult = ref('')
const strategy = ref('strategic_prune')
const goals = ref('')

async function runDecay() {
  try {
    const r = await api<DecayResponse>('/v1/memories/decay', { method: 'POST' })
    decayResult.value = JSON.stringify(r, null, 2)
    toast.success(`Decay: ${r.memories_processed} processed, ${r.memories_decayed} decayed`)
  } catch (e: any) { toast.error(`Decay failed: ${e.message}`) }
}

async function runConsolidation() {
  try {
    const r = await api<ConsolidationReport>('/v1/graph/consolidate', { method: 'POST' })
    consolResult.value = JSON.stringify(r, null, 2)
    toast.success(`Consolidation: ${r.facts_extracted} facts extracted, ${r.memories_pruned} pruned`)
  } catch (e: any) { toast.error(`Consolidation failed: ${e.message}`) }
}

async function runForget() {
  try {
    const params: Record<string, unknown> = {}
    if (strategy.value === 'strategic_prune' && goals.value) {
      params.goals = goals.value.split(',').map(s => s.trim()).filter(Boolean)
    }
    const r = await api<ForgetStrategyResponse>('/v1/memories/forget-strategy', {
      method: 'POST',
      body: JSON.stringify({ strategy: strategy.value, params }),
    })
    forgetResult.value = JSON.stringify(r, null, 2)
    toast.success(`Forgetting: ${r.memories_affected} memories affected`)
  } catch (e: any) { toast.error(`Forgetting failed: ${e.message}`) }
}
</script>
