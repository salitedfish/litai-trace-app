<template>
  <div class="h-full flex flex-col relative z-10 w-full max-w-[1800px] mx-auto pt-4">
    <!-- 条件栏：8 个条件收在弹窗里，此处只留入口 + 已选条件回显，把纵向空间让给列表 -->
    <div class="bg-card rounded-xl border border-border/40 px-4 py-2.5 shadow-sm mb-3 shrink-0 flex items-center gap-3 flex-wrap">
      <button
        class="px-3 py-2 rounded-lg text-sm font-medium border border-border bg-white text-foreground hover:border-accent/50 transition-colors flex items-center gap-1.5 shrink-0"
        @click="filterVisible = true">
        <svg class="w-4 h-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
        </svg>
        查询条件
        <span v-if="activeChips.length" class="px-1.5 py-0.5 rounded-full bg-accent text-white text-[10px] font-bold leading-none">{{ activeChips.length }}</span>
      </button>

      <div class="flex items-center gap-1.5 flex-wrap flex-1 min-w-0">
        <span v-for="chip in activeChips" :key="chip.key"
          class="inline-flex items-center gap-1 max-w-[240px] pl-2 pr-0.5 py-1 rounded-md bg-accent/10 text-accent text-xs">
          <span class="truncate" :title="`${chip.label}：${chip.text}`">{{ chip.text }}</span>
          <button class="shrink-0 hover:bg-accent/20 rounded p-0.5 transition-colors" :title="`清除${chip.label}`" @click="clearChip(chip.key)">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </span>
        <span v-if="!activeChips.length" class="text-xs text-muted-foreground">全部条件不限</span>
      </div>

      <button class="px-5 py-2 bg-accent text-white rounded-lg text-sm font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shrink-0"
        :disabled="queryLoading || !startTime || !endTime" @click="handleQuery">
        <svg v-if="queryLoading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
        <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        查询
      </button>
    </div>

    <!-- 结果区 -->
    <div v-show="searched" class="bg-card rounded-xl border border-border/40 shadow-sm flex flex-col flex-1 min-h-0">
      <div class="px-4 py-2 border-b border-border/40 bg-muted/20 flex items-center justify-between shrink-0">
        <span class="text-sm text-muted-foreground">
          <template v-if="total > 0">
            共 <strong class="text-foreground">{{ total }}</strong> 条报工记录
          </template>
          <template v-else>
            未找到报工记录
          </template>
        </span>
      </div>

      <div v-if="total == 0 && !queryError" class="py-8 text-center text-muted-foreground shrink-0">
        <svg class="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p>该条件下无报工记录</p>
      </div>

      <div v-if="queryError" class="py-8 text-center shrink-0">
        <svg class="w-12 h-12 mx-auto mb-3 text-red-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-red-500 font-medium">{{ queryError }}</p>
      </div>

      <div v-else-if="total > 0" class="overflow-auto flex-1 min-h-0">
        <table class="w-full text-left border-collapse">
          <thead class="sticky top-0 bg-card z-10">
            <tr class="border-b border-border text-xs uppercase tracking-wider text-muted-foreground">
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap w-12 text-center">#</th>
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap">工单号</th>
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap">产品</th>
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap">工序编码</th>
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap">工序名称</th>
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap">物料编码</th>
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap">物料类型</th>
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap">条码</th>
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap">操作时间</th>
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap">设备名称</th>
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap">检测结果</th>
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap">操作人</th>
              <th class="px-2 py-2.5 font-semibold whitespace-nowrap min-w-[230px] text-center">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/50 text-sm">
            <tr v-for="(item, idx) in dataList" :key="item.id" class="hover:bg-accent/5 transition-colors">
              <td class="px-2 py-2.5 text-center text-muted-foreground">{{ (page - 1) * pageSize + idx + 1 }}</td>
              <td class="px-2 py-2.5 font-mono text-xs max-w-[150px] truncate" :title="item.workorder_code">{{ item.workorder_code || '-' }}</td>
              <td class="px-2 py-2.5 text-sm whitespace-nowrap">{{ item.product_type || '-' }}</td>
              <td class="px-2 py-2.5 font-mono text-xs whitespace-nowrap">{{ item.procedure_code || '-' }}</td>
              <td class="px-2 py-2.5 text-sm whitespace-nowrap">{{ item.procedure_name || '-' }}</td>
              <td class="px-2 py-2.5 font-mono text-xs whitespace-nowrap">{{ item.material_code || '-' }}</td>
              <td class="px-2 py-2.5"><material-type-tag :type="item.material_type" /></td>
              <td class="px-2 py-2.5 font-mono text-xs max-w-[150px] truncate" :title="item.qr_code">{{ item.qr_code || '-' }}</td>
              <td class="px-2 py-2.5 text-muted-foreground text-xs whitespace-nowrap">{{ fmtTime(item.op_time) }}</td>
              <td class="px-2 py-2.5 text-xs text-muted-foreground whitespace-nowrap">{{ item.device_name || item.device_code || '-' }}</td>
              <td class="px-2 py-2.5 whitespace-nowrap"><span :class="checkResultClass(item.check_result)">{{ item.check_result || '-' }}</span></td>
              <td class="px-2 py-2.5 text-sm whitespace-nowrap">{{ item.operator || '-' }}</td>
              <td class="px-2 py-2.5 text-center">
                <div class="grid grid-cols-2 gap-1.5">
                  <button class="px-2.5 py-1 rounded-md text-xs font-medium whitespace-nowrap bg-accent/10 text-accent hover:bg-accent/20 transition-colors" @click="openInput(item)">查看投入</button>
                  <button class="px-2.5 py-1 rounded-md text-xs font-medium whitespace-nowrap bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200 transition-colors" @click="openParam(item)">工艺参数</button>
                  <button class="px-2.5 py-1 rounded-md text-xs font-medium whitespace-nowrap bg-emerald-50 text-emerald-600 hover:bg-emerald-100 border border-emerald-200 transition-colors" @click="openInspection(item)">检验单</button>
                  <button class="px-2.5 py-1 rounded-md text-xs font-medium whitespace-nowrap bg-purple-50 text-purple-600 hover:bg-purple-100 border border-purple-200 transition-colors" @click="openSubmission(item)">提交记录</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="total > pageSize" class="px-4 py-3 border-t border-border/40 bg-muted/10 flex items-center justify-between shrink-0">
        <span class="text-xs text-muted-foreground">
          第 {{ (page - 1) * pageSize + 1 }}-{{ Math.min(page * pageSize, total) }} 条，共 {{ total }} 条
        </span>
        <div class="flex items-center gap-2">
          <button class="px-3 py-1.5 rounded-lg text-xs font-medium border border-border bg-white text-foreground hover:bg-muted transition-colors disabled:opacity-40"
            :disabled="page <= 1" @click="goPage(page - 1)">
            上一页
          </button>
          <span class="text-xs text-muted-foreground px-2">{{ page }} / {{ totalPages }}</span>
          <button class="px-3 py-1.5 rounded-lg text-xs font-medium border border-border bg-white text-foreground hover:bg-muted transition-colors disabled:opacity-40"
            :disabled="page >= totalPages" @click="goPage(page + 1)">
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 报工详情四个弹窗（与追溯查询页共用组件，弹窗内自取数据） -->
    <MaterialInputDialog v-model:visible="inputVisible" :step="inputStep" @trace-code="traceInputCode" />
    <ProcessParamDialog v-model:visible="paramVisible" :step="paramStep" />
    <InspectionDialog v-model:visible="inspectionVisible" :step="inspectionStep" />
    <SubmissionDialog v-model:visible="submissionVisible" :step="submissionStep" @open-detail="openDetailFromSubmission" />

    <!-- 查询条件弹窗（Teleport 到 body，见 CLAUDE.md「弹窗层级」） -->
    <Teleport to="body">
      <transition name="modal-fade">
        <div v-if="filterVisible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/40 p-4"
          @click.self="filterVisible = false">
          <div class="bg-white rounded-xl shadow-2xl w-full max-w-3xl border border-border flex flex-col">
            <div class="px-5 py-3 border-b border-border/40 flex items-center justify-between shrink-0">
              <h3 class="text-base font-semibold text-foreground">查询条件</h3>
              <button class="text-muted-foreground hover:text-foreground transition-colors" @click="filterVisible = false">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>

            <div class="p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <div class="flex flex-col gap-1.5">
                <span class="text-xs font-medium text-muted-foreground">产品</span>
                <CustomSelect v-model="productType" :options="productOptions" placeholder="全部产品" variant="outline"
                  searchable clearable @change="onProductChange" />
              </div>
              <div class="flex flex-col gap-1.5">
                <span class="text-xs font-medium text-muted-foreground">工艺路线</span>
                <CustomSelect v-model="routingCode" :options="routingOptions" placeholder="全部工艺路线" variant="outline"
                  searchable clearable @change="onRoutingChange" />
              </div>
              <div class="flex flex-col gap-1.5">
                <span class="text-xs font-medium text-muted-foreground">工序</span>
                <CustomSelect v-model="processCode" :options="processOptions" placeholder="全部工序" variant="outline"
                  searchable clearable />
              </div>
              <div class="flex flex-col gap-1.5">
                <span class="text-xs font-medium text-muted-foreground">人员</span>
                <CustomSelect v-model="operatorId" :options="operatorOptions" placeholder="全部人员" variant="outline"
                  searchable clearable />
              </div>
              <div class="flex flex-col gap-1.5">
                <span class="text-xs font-medium text-muted-foreground">结果</span>
                <CustomSelect v-model="checkResult" :options="checkResultOptions" placeholder="全部结果" variant="outline"
                  clearable />
              </div>
              <div class="flex flex-col gap-1.5">
                <span class="text-xs font-medium text-muted-foreground">设备</span>
                <CustomSelect v-model="deviceCode" :options="deviceOptions" placeholder="全部设备" variant="outline"
                  searchable clearable />
              </div>
              <div class="flex flex-col gap-1.5">
                <span class="text-xs font-medium text-muted-foreground">开始时间</span>
                <input v-model="startTime" type="datetime-local"
                  class="w-full px-3 py-2 rounded-lg border border-border bg-white text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
              </div>
              <div class="flex flex-col gap-1.5">
                <span class="text-xs font-medium text-muted-foreground">结束时间</span>
                <input v-model="endTime" type="datetime-local"
                  class="w-full px-3 py-2 rounded-lg border border-border bg-white text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
              </div>
            </div>

            <div class="px-5 py-3 border-t border-border/40 bg-muted/10 flex items-center justify-end gap-2 shrink-0">
              <button class="px-4 py-2 rounded-lg text-sm font-medium border border-border bg-white text-foreground hover:bg-muted transition-colors"
                @click="resetFilters">重置</button>
              <button class="px-5 py-2 bg-accent text-white rounded-lg text-sm font-medium hover:bg-accent/90 transition-colors disabled:opacity-50"
                :disabled="queryLoading || !startTime || !endTime" @click="applyQuery">查询</button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, inject, onMounted } from 'vue'
import type { Ref } from 'vue'
import api from '../api/trace-app'
import { useReportDialogs } from '../composables/useReportDialogs'
import { useProductRoutingProcess } from '../composables/useProductRoutingProcess'
import { setPendingTraceCode } from '../composables/useTraceNav'
import { fmtTime, checkResultClass } from '../utils/trace-format'
import CustomSelect from '../components/CustomSelect.vue'
import MaterialTypeTag from '../components/trace/MaterialTypeTag'
import MaterialInputDialog from '../components/trace/MaterialInputDialog.vue'
import ProcessParamDialog from '../components/trace/ProcessParamDialog.vue'
import InspectionDialog from '../components/trace/InspectionDialog.vue'
import SubmissionDialog from '../components/trace/SubmissionDialog.vue'

// 投入物料弹窗点「追溯此码」需切到追溯查询视图（应用无 router，视图由 currentView 控制 v-show）
const currentView = inject<Ref<string>>('currentView', ref('home'))

// 产品 / 工艺路线 / 工序 三级联动（与报工不合格原因页共用）
const {
  productType, routingCode, processCode,
  productOptions, routingOptions, processOptions,
  loadBaseOptions, onProductChange, onRoutingChange, buildFilter,
} = useProductRoutingProcess()

// 人员 / 设备候选（取自报工记录里出现过的值）
const operatorId = ref('')
const deviceCode = ref('')
const operatorOptions = ref<{ label: string, value: string }[]>([])
const deviceOptions = ref<{ label: string, value: string }[]>([])

// 检测结果：与列表「检测结果」列显示值一致的四档
const checkResult = ref('')
const checkResultOptions = [
  { label: '一次合格', value: '一次合格' },
  { label: '返工合格', value: '返工合格' },
  { label: '复投合格', value: '复投合格' },
  { label: '不合格', value: '不合格' },
]

const startTime = ref('')
const endTime = ref('')

const queryLoading = ref(false)
const searched = ref(false)
const queryError = ref('')

const dataList = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

// 四个报工详情弹窗的开关与当前行（与追溯查询页共用同一份协调逻辑）
const {
  inputVisible, inputStep,
  paramVisible, paramStep,
  inspectionVisible, inspectionStep,
  submissionVisible, submissionStep,
  openInput, openParam, openInspection, openSubmission,
  openDetailFromSubmission,
} = useReportDialogs()

// ========== 初始化：默认查当天 ==========
const setTodayRange = () => {
  const now = new Date()
  startTime.value = formatDatetimeLocal(new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0))
  endTime.value = formatDatetimeLocal(new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59))
}

onMounted(async () => {
  setTodayRange()
  await Promise.all([loadBaseOptions(), loadFilterOptions()])
  handleQuery()
})

// datetime-local 格式（YYYY-MM-DDTHH:mm）→ 后端可比较的本地时间字符串（YYYY-MM-DD HH:mm:ss）
const toTimeString = (value: string) => {
  if (!value) return ''
  return value.replace('T', ' ') + (value.length == 16 ? ':00' : '')
}

const formatDatetimeLocal = (date: Date) => {
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const loadFilterOptions = async () => {
  try {
    const res = await api.queryReportFilterOptions()
    const data = res.data || {}
    operatorOptions.value = data.operators || []
    deviceOptions.value = data.devices || []
  } catch (err: any) {
    console.error('加载人员/设备候选失败:', err)
  }
}

// ========== 查询 ==========
const handleQuery = async () => {
  page.value = 1
  await doQuery()
}

const doQuery = async () => {
  queryLoading.value = true
  queryError.value = ''
  searched.value = true
  try {
    const res = await api.queryReportRecords({
      ...buildFilter(),
      operator: operatorId.value || undefined,
      check_result: checkResult.value || undefined,
      device_code: deviceCode.value || undefined,
      start_time: toTimeString(startTime.value),
      end_time: toTimeString(endTime.value),
      page: page.value,
      page_size: pageSize.value,
    })
    const data = res.data || {}
    dataList.value = data.list || []
    total.value = data.total || 0
  } catch (err: any) {
    console.error('查询报工记录失败:', err)
    dataList.value = []
    total.value = 0
    queryError.value = '查询失败，请检查网络或稍后重试'
  } finally {
    queryLoading.value = false
  }
}

// ========== 分页 ==========
const goPage = (p: number) => {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  doQuery()
}

// ========== 查询条件弹窗 ==========
const filterVisible = ref(false)

const labelOf = (opts: { label: string, value: string }[], value: string) =>
  opts.find(o => o.value == value)?.label || value

// 已选条件回显。时间范围不在其中——它是必填项，语义上不属「不限」的条件
const activeChips = computed(() => {
  const chips: { key: string, label: string, text: string }[] = []
  if (productType.value) chips.push({ key: 'product', label: '产品', text: labelOf(productOptions.value, productType.value) })
  if (routingCode.value) chips.push({ key: 'routing', label: '工艺路线', text: labelOf(routingOptions.value, routingCode.value) })
  if (processCode.value) chips.push({ key: 'process', label: '工序', text: labelOf(processOptions.value, processCode.value) })
  if (operatorId.value) chips.push({ key: 'operator', label: '人员', text: labelOf(operatorOptions.value, operatorId.value) })
  if (checkResult.value) chips.push({ key: 'check_result', label: '结果', text: checkResult.value })
  if (deviceCode.value) chips.push({ key: 'device', label: '设备', text: labelOf(deviceOptions.value, deviceCode.value) })
  return chips
})

// 清条件只改状态、不自动重查：清「产品」会连带清路线与工序，逐项确认完再点「查询」更省事
// 注意产品自己的值来自 v-model，onProductChange() 只清下级，故本级要显式清
const clearChip = async (key: string) => {
  if (key == 'product') { productType.value = ''; await onProductChange() }
  else if (key == 'routing') { routingCode.value = ''; await onRoutingChange() }
  else if (key == 'process') processCode.value = ''
  else if (key == 'operator') operatorId.value = ''
  else if (key == 'check_result') checkResult.value = ''
  else if (key == 'device') deviceCode.value = ''
}

const resetFilters = async () => {
  productType.value = ''
  await onProductChange()
  operatorId.value = ''
  checkResult.value = ''
  deviceCode.value = ''
  setTodayRange()
}

const applyQuery = async () => {
  filterVisible.value = false
  await handleQuery()
}

// ========== 投入物料弹窗「追溯此码」：本页无追溯入口，投码后切到追溯查询视图 ==========
const traceInputCode = (qrCode: string) => {
  setPendingTraceCode(qrCode)
  currentView.value = 'history'
}
</script>
