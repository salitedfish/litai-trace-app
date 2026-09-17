<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="visible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="close">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">工艺参数</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                {{ step?.procedure_name || '工序' }}
                <span v-if="step?.procedure_code" class="ml-1 font-mono">({{ step?.procedure_code }})</span>
                <span class="ml-2">产出: <code class="bg-muted px-1 py-0.5 rounded font-mono text-xs">{{ step?.qr_code }}</code></span>
              </p>
            </div>
            <div class="flex items-center gap-2">
              <button class="px-3 py-1.5 rounded-lg text-xs font-medium bg-accent text-white hover:bg-accent/90 transition-colors flex items-center gap-1.5" @click="goDeviceData">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"/></svg>
                数采数据
              </button>
              <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="close">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
          </div>
          <div class="overflow-auto flex-1 p-6">
            <div v-if="loading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-8">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              加载中...
            </div>
            <div v-else-if="error" class="text-sm text-red-500 py-4 text-center">{{ error }}</div>
            <div v-else-if="params.length === 0" class="text-sm text-muted-foreground py-8 text-center">该工单无工艺参数数据</div>
            <div v-else class="space-y-4">
              <div v-for="(item, idx) in params" :key="idx" class="rounded-lg border border-border/50 bg-muted/10 p-4">
                <div class="flex items-center justify-between mb-2 text-xs text-muted-foreground">
                  <span class="font-medium">{{ item.device_name || item.device_code }} — {{ item.procedure_name }}</span>
                  <span>{{ fmtTime(item.timestamp) }}</span>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                  <div v-for="(val, key) in item.params" :key="key" class="bg-white rounded border border-border/40 px-3 py-2">
                    <p class="text-[10px] text-muted-foreground font-mono">{{ item.param_descs?.[key] || key }}</p>
                    <p class="text-sm font-semibold text-foreground">{{ val }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, inject, watch } from 'vue'
import type { Ref } from 'vue'
import api from '../../api/trace-app'
import { showToast } from '../../utils/dialog'
import { navigateToDeviceData } from '../../composables/useDeviceDataNav'
import { fmtTime } from '../../utils/trace-format'

const props = defineProps<{
  visible: boolean
  /** 报工记录（需含 workorder_code / procedure_name / procedure_code / qr_code；
      跳数采查询还需 device_code / op_time） */
  step: any
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

const currentView = inject<Ref<string>>('currentView', ref('home'))

const params = ref<any[]>([])
const loading = ref(false)
const error = ref('')

const load = async () => {
  loading.value = true
  error.value = ''
  params.value = []
  try {
    const res = await api.queryProcessParams(props.step?.workorder_code || '')
    params.value = res.data || []
  } catch (err: any) {
    error.value = '加载失败: ' + (err?.message || '未知错误')
  } finally {
    loading.value = false
  }
}

watch(() => [props.visible, props.step], () => {
  if (!props.visible) return
  load()
})

const close = () => {
  emit('update:visible', false)
  params.value = []
  error.value = ''
}

// 跳转数采查询并携带设备 + 报工时间±5min（缺少设备或时间的记录无法跳转）
const goDeviceData = () => {
  const ok = navigateToDeviceData({
    device_code: props.step?.device_code || '',
    report_time: props.step?.op_time || '',
  })
  if (!ok) {
    showToast('该报工记录缺少设备或报工时间，无法跳转数采查询', 'warning')
    return
  }
  close()
  currentView.value = 'device_data'
}
</script>
