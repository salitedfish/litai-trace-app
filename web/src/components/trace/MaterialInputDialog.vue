<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="visible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="close">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">投入物料明细</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                {{ step?.procedure_name || '工序' }}
                <span v-if="step?.procedure_code" class="ml-1 font-mono">({{ step?.procedure_code }})</span>
                <span class="ml-2">产出: <code class="bg-muted px-1 py-0.5 rounded font-mono text-xs">{{ step?.qr_code }}</code></span>
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
            <div v-else-if="inputs.length === 0" class="text-sm text-muted-foreground py-8 text-center">该次报工无投入记录</div>
            <div v-else>
              <table class="w-full text-left border-collapse text-sm">
                <thead>
                  <tr class="border-b border-border/50 text-xs text-muted-foreground">
                    <th class="px-3 py-2.5 font-medium w-[120px]">物料编码</th>
                    <th class="px-3 py-2.5 font-medium w-20">物料类型</th>
                    <th class="px-3 py-2.5 font-medium">条码</th>
                    <th class="px-3 py-2.5 font-medium w-12 text-center">数量</th>
                    <th class="px-3 py-2.5 font-medium w-36">操作时间</th>
                    <th class="px-3 py-2.5 font-medium w-24 text-center">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border/30">
                  <tr v-for="(input, i) in inputs" :key="i" class="hover:bg-muted/30">
                    <td class="px-3 py-2.5 font-mono text-xs">{{ input.material_code }}</td>
                    <td class="px-3 py-2.5"><material-type-tag :type="input.material_type" /></td>
                    <td class="px-3 py-2.5 font-mono text-xs max-w-[200px] truncate" :title="input.qr_code">{{ input.qr_code }}</td>
                    <td class="px-3 py-2.5 text-center">{{ input.require_num }}</td>
                    <td class="px-3 py-2.5 text-xs text-muted-foreground">{{ fmtTime(input.op_time) }}</td>
                    <td class="px-3 py-2.5 text-center">
                      <button class="px-2 py-1 rounded text-xs font-medium bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200 transition-colors"
                        @click="emitTraceCode(input.qr_code)">追溯此码</button>
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
import { fmtTime } from '../../utils/trace-format'
import MaterialTypeTag from './MaterialTypeTag'

const props = defineProps<{
  visible: boolean
  /** 报工记录（需含 workorder_code / procedure_name / procedure_code / qr_code） */
  step: any
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  /** 点「追溯此码」：把投入码交给父组件跳转追溯查询 */
  (e: 'trace-code', code: string): void
}>()

const inputs = ref<any[]>([])
const loading = ref(false)
const error = ref('')

const load = async () => {
  loading.value = true
  error.value = ''
  inputs.value = []
  try {
    const res = await api.queryInputs(props.step?.workorder_code || '')
    inputs.value = res.data || []
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
  inputs.value = []
  error.value = ''
}

const emitTraceCode = (code: string) => {
  close()
  emit('trace-code', code)
}
</script>
