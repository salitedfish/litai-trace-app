<template>
  <div v-if="show" class="filter-overlay" @click.self="emit('close')">
    <div class="filter-modal">
      <div class="filter-modal-header">
        <span class="filter-modal-title">
          <i class="filter-title-bar"></i>
          更多操作
        </span>
        <button class="filter-modal-close" @click="emit('close')">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="filter-modal-body">
        <div class="filter-field">
          <label class="filter-label">开始日期</label>
          <input type="date" class="filter-input" :value="startDate" @change="onStartDateChange" />
        </div>
        <div class="filter-field">
          <label class="filter-label">结束日期</label>
          <input type="date" class="filter-input" :value="endDate" @change="onEndDateChange" />
        </div>
        <div class="filter-field">
          <label class="filter-label">产线</label>
          <DarkSelect
            :model-value="selectedLine"
            :options="lineOptions"
            :disabled="lineLoading"
            placeholder="请选择产线"
            searchable
            @update:model-value="(v) => emit('lineChange', String(v))"
          />
        </div>
      </div>
      <div class="filter-modal-footer">
        <button class="filter-btn-primary" @click="emit('close')">确认</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '../../../api/trace-app'
import DarkSelect from '../../../components/DarkSelect.vue'

defineProps<{
  show: boolean
  startDate: string
  endDate: string
  selectedLine: string
}>()

// ========== 产线列表（组件自管理） ==========
const lineList = ref<{ workshop_code: string, workshop_name: string }[]>([])
const lineLoading = ref(false)

const lineOptions = computed(() => {
  return lineList.value.map(item => ({ label: item.workshop_name, value: item.workshop_code }))
})

const loadLineList = async () => {
  lineLoading.value = true
  try {
    const res = await api.queryLineList()
    lineList.value = res.data || []
  } catch (err: any) {
    console.error('加载产线列表失败:', err)
  } finally {
    lineLoading.value = false
  }
}

onMounted(() => {
  loadLineList()
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'startDateChange', value: string): void
  (e: 'endDateChange', value: string): void
  (e: 'lineChange', value: string): void
}>()

function onStartDateChange(event: Event) {
  const target = event.target as HTMLInputElement
  emit('startDateChange', target.value)
}

function onEndDateChange(event: Event) {
  const target = event.target as HTMLInputElement
  emit('endDateChange', target.value)
}
</script>

<style scoped>
/* ========== 时间筛选弹窗 ========== */
.filter-overlay {
  @apply fixed inset-0 z-[10000] flex items-center justify-center;
  background: rgba(0, 0, 0, 0.6);
}

.filter-modal {
  @apply rounded-md;
  position: relative;
  width: 320px;
  background:
    linear-gradient(rgba(56, 189, 248, 0.5), rgba(56, 189, 248, 0.5)) left 8px top 8px / 18px 1px no-repeat,
    linear-gradient(rgba(56, 189, 248, 0.5), rgba(56, 189, 248, 0.5)) left 8px top 8px / 1px 18px no-repeat,
    linear-gradient(rgba(56, 189, 248, 0.5), rgba(56, 189, 248, 0.5)) right 8px top 8px / 18px 1px no-repeat,
    linear-gradient(rgba(56, 189, 248, 0.5), rgba(56, 189, 248, 0.5)) right 8px top 8px / 1px 18px no-repeat,
    linear-gradient(rgba(56, 189, 248, 0.5), rgba(56, 189, 248, 0.5)) left 8px bottom 8px / 18px 1px no-repeat,
    linear-gradient(rgba(56, 189, 248, 0.5), rgba(56, 189, 248, 0.5)) left 8px bottom 8px / 1px 18px no-repeat,
    linear-gradient(rgba(56, 189, 248, 0.5), rgba(56, 189, 248, 0.5)) right 8px bottom 8px / 18px 1px no-repeat,
    linear-gradient(rgba(56, 189, 248, 0.5), rgba(56, 189, 248, 0.5)) right 8px bottom 8px / 1px 18px no-repeat,
    linear-gradient(160deg, rgba(13, 32, 71, 0.92), rgba(6, 17, 40, 0.96)) center / 100% 100% no-repeat;
  border: 1px solid rgba(56, 189, 248, 0.25);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), inset 0 0 30px rgba(37, 99, 235, 0.08);
}

.filter-modal-header {
  @apply flex items-center justify-between;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(56, 189, 248, 0.14);
}

.filter-modal-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.14em;
  color: #dbeafe;
}

.filter-title-bar {
  width: 4px;
  height: 14px;
  background: linear-gradient(180deg, #38bdf8, #2563eb);
  box-shadow: 0 0 8px rgba(56, 189, 248, 0.6);
}

.filter-modal-close {
  @apply flex items-center justify-center rounded-full transition-colors;
  width: 28px;
  height: 28px;
  color: rgba(148, 184, 255, 0.5);
}

.filter-modal-close:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

.filter-modal-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-field {
  @apply flex flex-col gap-1.5;
}

.filter-label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(148, 184, 255, 0.6);
}

.filter-input {
  width: 100%;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid rgba(59, 130, 246, 0.15);
  background: rgba(59, 130, 246, 0.06);
  color: #93c5fd;
  font-size: 13px;
  font-family: monospace;
  outline: none;
}

.filter-input:focus {
  border-color: rgba(56, 189, 248, 0.5);
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.12);
}

.filter-input::-webkit-calendar-picker-indicator {
  filter: invert(0.7) sepia(1) hue-rotate(190deg);
  cursor: pointer;
}

.filter-modal-footer {
  padding: 10px 16px 14px;
  display: flex;
  justify-content: flex-end;
}

.filter-btn-primary {
  padding: 6px 22px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.1em;
  background: linear-gradient(135deg, #38bdf8, #2563eb);
  color: #fff;
  border: 1px solid rgba(125, 211, 252, 0.35);
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.25);
}

.filter-btn-primary:hover {
  opacity: 0.92;
  box-shadow: 0 0 18px rgba(56, 189, 248, 0.4);
}
</style>
