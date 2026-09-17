<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="visible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="close">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">提交记录</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                {{ step?.procedure_name || '工序' }}
                <span v-if="step?.procedure_code" class="ml-1 font-mono">({{ step?.procedure_code }})</span>
                <span class="ml-2">条码: <code class="bg-muted px-1 py-0.5 rounded font-mono text-xs">{{ step?.qr_code }}</code></span>
              </p>
            </div>
            <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="close">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="overflow-auto flex-1 p-6">
            <div v-if="loading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-8">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              加载中...
            </div>
            <div v-else-if="error" class="text-sm text-red-500 py-4 text-center">{{ error }}</div>
            <div v-else-if="records.length === 0" class="text-sm text-muted-foreground py-8 text-center">无提交记录</div>
            <div v-else>
              <table class="w-full text-left border-collapse text-sm">
                <thead>
                  <tr class="border-b border-border/50 text-xs text-muted-foreground">
                    <th class="px-3 py-2.5 font-medium w-14 text-center">#</th>
                    <th class="px-3 py-2.5 font-medium">工单编码</th>
                    <th class="px-3 py-2.5 font-medium w-36">操作时间</th>
                    <th class="px-3 py-2.5 font-medium">操作人</th>
                    <th class="px-3 py-2.5 font-medium">检测结果</th>
                    <th class="px-3 py-2.5 font-medium w-44 text-center">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border/30">
                  <tr v-for="(rec, i) in records" :key="i" class="hover:bg-muted/30">
                    <td class="px-3 py-2.5 text-center text-muted-foreground">{{ i + 1 }}</td>
                    <td class="px-3 py-2.5 font-mono text-xs max-w-[250px] truncate" :title="rec.workorder_code">{{ rec.workorder_code }}</td>
                    <td class="px-3 py-2.5 text-xs text-muted-foreground">{{ fmtTime(rec.op_time) }}</td>
                    <td class="px-3 py-2.5">{{ rec.operator }}</td>
                    <td class="px-3 py-2.5"><span class="text-xs" :class="checkResultClass(rec.check_result)">{{ rec.check_result || '-' }}</span></td>
                    <td class="px-3 py-2.5 text-center">
                      <div class="grid grid-cols-2 gap-1.5">
                        <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-accent/10 text-accent hover:bg-accent/20 transition-colors" @click="openDetail('input', rec)">查看投入</button>
                        <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200 transition-colors" @click="openDetail('param', rec)">工艺参数</button>
                        <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-50 text-emerald-600 hover:bg-emerald-100 border border-emerald-200 transition-colors" @click="openDetail('inspection', rec)">检验单</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import api from '../../api/trace-app'
import { fmtTime, checkResultClass } from '../../utils/trace-format'

const props = defineProps<{
  visible: boolean
  /** 报工记录（需含 qr_code / procedure_code / device_code / procedure_name） */
  step: any
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  /**
   * 行内按钮点击：父组件负责先关本弹窗、再开目标弹窗（避免 z-index 遮挡）。
   * 父组件用 payload.step 组装目标弹窗需要的报工记录。
   */
  (e: 'open-detail', payload: { kind: 'input' | 'param' | 'inspection', record: any, step: any }): void
}>()

const records = ref<any[]>([])
const loading = ref(false)
const error = ref('')

const load = async () => {
  loading.value = true
  error.value = ''
  records.value = []
  try {
    const res = await api.querySubmissionRecords(
      props.step?.qr_code || '', props.step?.procedure_code || '', props.step?.device_code || '')
    records.value = res.data || []
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
  records.value = []
  error.value = ''
}

const openDetail = (kind: 'input' | 'param' | 'inspection', record: any) => {
  emit('open-detail', { kind, record, step: props.step })
  close()
}
</script>
