<template>
  <div class="p-6 max-w-6xl mx-auto">
    <h2 class="text-xl font-semibold mb-4">Memory Explorer</h2>

    <!-- Search -->
    <div class="flex gap-2 mb-4">
      <input
        v-model="query"
        type="text"
        placeholder="Search memories..."
        class="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-brand"
        @keydown.enter="doSearch"
      />
      <button class="px-4 py-2 bg-brand text-white rounded-lg text-sm hover:bg-brand-hover" @click="doSearch">Search</button>
      <button class="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg text-sm hover:bg-slate-600" @click="doLoad">Refresh</button>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="text-left text-xs text-slate-400 border-b border-slate-700">
            <th class="pb-2 pr-4">Content</th>
            <th class="pb-2 pr-4">Activation</th>
            <th class="pb-2 pr-4">Status</th>
            <th class="pb-2 pr-4">Type</th>
            <th class="pb-2">Accesses</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="m in displayList"
            :key="m.memory_id"
            class="border-b border-slate-800/50 hover:bg-white/[0.02] cursor-pointer transition-colors"
            @click="doInspect(m.memory_id)"
          >
            <td class="py-2 pr-4 max-w-[400px] truncate text-sm">{{ m.content }}</td>
            <td class="py-2 pr-4"><ActivationBar :activation="m.activation" :status="'status' in m ? (m as any).status : 'active'" /></td>
            <td class="py-2 pr-4"><Badge :status="'status' in m ? (m as any).status : 'active'" /></td>
            <td class="py-2 pr-4 text-xs text-slate-400">{{ 'memory_type' in m ? (m as any).memory_type : '—' }}</td>
            <td class="py-2 text-sm">{{ m.access_count }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="!isSearchMode" class="mt-4 text-center">
      <button class="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg text-sm hover:bg-slate-600" @click="loadMore">Load More</button>
    </div>

    <!-- Detail Drawer -->
    <Transition name="slide">
      <div v-if="selected" class="fixed top-0 right-0 h-full w-96 bg-slate-800 border-l border-slate-700 shadow-2xl z-40 overflow-y-auto p-6">
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-brand font-semibold">Memory Detail</h3>
          <button class="text-slate-500 hover:text-slate-300" @click="clearSelected">✕</button>
        </div>
        <div class="space-y-3 text-sm">
          <div><span class="text-slate-400 w-32 inline-block">ID</span> <span class="text-xs break-all">{{ selected.memory_id }}</span></div>
          <div><span class="text-slate-400 w-32 inline-block">Content</span> {{ selected.content }}</div>
          <div><span class="text-slate-400 w-32 inline-block">Status</span> <Badge :status="selected.status" /></div>
          <div><span class="text-slate-400 w-32 inline-block">Activation</span> {{ selected.activation.toFixed(4) }}</div>
          <div><span class="text-slate-400 w-32 inline-block">Salience</span> {{ selected.salience.toFixed(4) }}</div>
          <div><span class="text-slate-400 w-32 inline-block">Emotion</span> val: {{ selected.emotion_valence.toFixed(2) }}, aro: {{ selected.emotion_arousal.toFixed(2) }}</div>
          <div><span class="text-slate-400 w-32 inline-block">Decay Rate</span> {{ selected.decay_rate }}</div>
          <div><span class="text-slate-400 w-32 inline-block">Access Count</span> {{ selected.access_count }}</div>
          <div><span class="text-slate-400 w-32 inline-block">Created</span> {{ new Date(selected.created_at).toLocaleString() }}</div>
          <div><span class="text-slate-400 w-32 inline-block">Last Accessed</span> {{ new Date(selected.last_accessed).toLocaleString() }}</div>
          <div class="pt-2 border-t border-slate-700">
            <div class="text-slate-400 mb-1">Access History ({{ selected.access_history.length }})</div>
            <div v-for="(a, i) in selected.access_history.slice(0, 20)" :key="i" class="text-xs text-slate-500">
              {{ new Date(a.accessed_at).toLocaleString() }} {{ a.context ? `— ${a.context}` : '' }}
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMemories } from '@/composables/useMemories'
import Badge from '@/components/shared/Badge.vue'
import ActivationBar from '@/components/shared/ActivationBar.vue'

const { memories, searchResults, selected, isSearchMode, load, loadMore, search, inspect, clearSelected } = useMemories()
const query = ref('')

const displayList = computed(() => isSearchMode.value ? searchResults.value : memories.value)

function doSearch() { search(query.value) }
function doLoad() { query.value = ''; load() }
function doInspect(id: string) { inspect(id) }

onMounted(() => load())
</script>
