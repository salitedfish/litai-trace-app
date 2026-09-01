<template>
  <div class="min-h-full flex flex-col relative z-10 w-full max-w-[800px] mx-auto pt-8">
    <div class="bg-card rounded-2xl border border-border/40 p-8 shadow-sm">
      <div class="flex items-center gap-3 mb-8">
        <div class="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
          <svg class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065zM15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-foreground">智能看板2设置</h2>
          <p class="text-sm text-muted-foreground">配置智能看板2的显示内容</p>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-x-5 gap-y-6">
        <!-- 看板标题（整行） -->
        <div class="flex flex-col gap-2 col-span-2">
          <label class="text-sm font-medium text-foreground">
            看板标题 <span class="text-red-500">*</span>
          </label>
          <input v-model="title" type="text" placeholder="请输入看板标题"
            class="w-full px-4 py-2.5 rounded-lg border border-border bg-white text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
          <p class="text-xs text-muted-foreground">该标题将显示在智能看板2的顶部</p>
        </div>

        <!-- 开始日期 / 结束日期 -->
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-foreground">开始日期</label>
          <input v-model="startDate" type="date"
            class="w-full px-4 py-2.5 rounded-lg border border-border bg-white text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
          <p class="text-xs text-muted-foreground">统计的起始日期，为空则取当天</p>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-foreground">结束日期</label>
          <input v-model="endDate" type="date"
            class="w-full px-4 py-2.5 rounded-lg border border-border bg-white text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
          <p class="text-xs text-muted-foreground">统计的截止日期，为空则取当天</p>
        </div>

        <!-- 产线 / 产品型号 -->
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-foreground">产线</label>
          <CustomSelect
            v-model="workshopCode"
            :options="lineOptions"
            :disabled="lineLoading"
            variant="outline"
            placeholder="请选择产线"
          />
          <p class="text-xs text-muted-foreground">看板展示的产线，不选则看板不展示产线设备</p>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-foreground">产品型号</label>
          <MultiSelect
            v-model="productType"
            :options="productTypeOptions"
            placeholder="请选择产品型号（可多选）"
          />
          <p class="text-xs text-muted-foreground">看板展示的产品型号，可多选，不选则不限</p>
        </div>

        <!-- 保存（整行） -->
        <div class="flex items-center gap-3 pt-2 col-span-2">
          <button class="px-6 py-2.5 bg-accent text-white rounded-lg text-sm font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 flex items-center gap-2"
            :disabled="saving || !title.trim()" @click="handleSave">
            <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
            确认
          </button>

          <span v-if="saved" class="text-sm text-emerald-600 flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            保存成功
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../../api/trace-app'
import CustomSelect from '../../components/CustomSelect.vue'
import MultiSelect from '../../components/MultiSelect.vue'

const title = ref('')
const startDate = ref('')
const endDate = ref('')
const workshopCode = ref('')
const productType = ref<string[]>([])
const lineList = ref<{ workshop_code: string, workshop_name: string }[]>([])
const lineLoading = ref(false)
const productTypeList = ref<{ production_type: string, routing_code: string }[]>([])
const saving = ref(false)
const saved = ref(false)

const productTypeOptions = computed(() =>
  productTypeList.value.map(pt => ({ label: pt.production_type, value: pt.production_type }))
)

const lineOptions = computed(() =>
  lineList.value.map(line => ({ label: line.workshop_name, value: line.workshop_code }))
)

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

const loadProductTypeList = async () => {
  try {
    const res = await api.queryProductTypeList()
    productTypeList.value = res.data || []
  } catch (err: any) {
    console.error('加载产品型号列表失败:', err)
  }
}

onMounted(async () => {
  try {
    const res = await api.getDashboardConfig2()
    const cfg = res.data || {}
    title.value = cfg.title || ''
    startDate.value = cfg.start_date || ''
    endDate.value = cfg.end_date || ''
    workshopCode.value = cfg.workshop_code || ''
    productType.value = Array.isArray(cfg.product_type) ? cfg.product_type : []
  } catch (err: any) {
    console.error('加载看板2配置失败:', err)
  }
  await loadLineList()
  await loadProductTypeList()
})

const handleSave = async () => {
  if (!title.value.trim()) return
  saving.value = true
  saved.value = false
  try {
    await api.saveDashboardConfig2({
      title: title.value.trim(),
      start_date: startDate.value,
      end_date: endDate.value,
      workshop_code: workshopCode.value,
      product_type: productType.value,
    })
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (err: any) {
    console.error('保存看板2配置失败:', err)
  } finally {
    saving.value = false
  }
}
</script>
