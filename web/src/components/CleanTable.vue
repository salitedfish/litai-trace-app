<template>
  <div class="w-full bg-white rounded-2xl shadow-sm border border-border/50 overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-muted/50 border-b border-border text-xs uppercase tracking-wider text-muted-foreground font-mono">
            <th v-if="selectable" class="px-6 py-4 w-12 text-center">
              <input type="checkbox" class="accent-accent w-4 h-4 rounded border-gray-300 focus:ring-accent cursor-pointer" @change="toggleAll" :checked="isAllSelected">
            </th>
            <th v-for="col in columns" :key="col.prop" class="px-6 py-4 font-semibold whitespace-nowrap">
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border/50 text-sm font-sans text-foreground">
          <tr v-if="data.length === 0">
            <td :colspan="columns.length + (selectable ? 1 : 0)" class="px-6 py-16 text-center text-muted-foreground">
              <div class="flex flex-col items-center justify-center gap-3">
                <svg class="w-10 h-10 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
                <span class="tracking-wide">暂无数据</span>
              </div>
            </td>
          </tr>
          <tr v-for="(row, index) in data" :key="row.id || index"
              class="hover:bg-accent/5 transition-colors duration-200 cursor-pointer group"
              @dblclick="$emit('row-dblclick', row)">
            <td v-if="selectable" class="px-6 py-4 text-center">
              <input type="checkbox" class="accent-accent w-4 h-4 rounded border-gray-300 focus:ring-accent cursor-pointer" :value="row" v-model="selectedRows">
            </td>
            <td v-for="col in columns" :key="col.prop" class="px-6 py-4 align-top">
              <template v-if="col.slot">
                <slot :name="col.slot" :row="row"></slot>
              </template>
              <template v-else>
                {{ row[col.prop] }}
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps({
  data: { type: Array as () => any[], default: () => [] },
  columns: { type: Array as () => any[], required: true },
  selectable: { type: Boolean, default: true }
})

const emit = defineEmits(['selection-change', 'row-dblclick'])

const selectedRows = ref<any[]>([])

const isAllSelected = computed(() => {
  return props.data.length > 0 && selectedRows.value.length === props.data.length
})

const toggleAll = (e: Event) => {
  if ((e.target as HTMLInputElement).checked) {
    selectedRows.value = [...props.data]
  } else {
    selectedRows.value = []
  }
}

watch(selectedRows, (newVal) => {
  emit('selection-change', newVal)
}, { deep: true })
</script>
