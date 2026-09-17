<template>
  <div class="h-full flex flex-col relative z-10 w-full max-w-[1400px] mx-auto pt-4">
    <!-- 条件栏：4 个条件（产品/工艺路线/工序/报工时间）收在弹窗里，此处只留入口 + 已选条件回显 -->
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
        <!-- 报工时间不算「可清除的条件」：弹窗里是起止两个输入框，清空即回到不限，故只做只读回显 -->
        <span class="text-xs text-muted-foreground shrink-0">
          报工时间：<span class="text-foreground">{{ timeRangeText }}</span>
        </span>
      </div>

      <button class="px-5 py-2 bg-accent text-white rounded-lg text-sm font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shrink-0"
        :disabled="queryLoading" @click="handleQuery">
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
            共 <strong class="text-foreground">{{ total }}</strong> 种不合格原因
          </template>
          <template v-else>
            未找到不合格原因
          </template>
        </span>
      </div>

      <div v-if="total == 0 && !queryError" class="py-8 text-center text-muted-foreground shrink-0">
        <svg class="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p>该条件下无不合格原因记录</p>
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
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap w-16 text-center">#</th>
              <th class="px-3 py-2.5 font-semibold">不合格原因</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap w-32 text-center">次数</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap w-32 text-center">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/50 text-sm">
            <tr v-for="(item, idx) in dataList" :key="item.reason_code || idx" class="hover:bg-accent/5 transition-colors">
              <td class="px-3 py-2.5 text-center text-muted-foreground">{{ (page - 1) * pageSize + idx + 1 }}</td>
              <td class="px-3 py-2.5">
                <span class="font-medium text-foreground">{{ item.reason_name || item.reason_code || '-' }}</span>
                <span v-if="item.reason_code" class="ml-2 font-mono text-[10px] text-muted-foreground">{{ item.reason_code }}</span>
              </td>
              <td class="px-3 py-2.5 text-center font-mono text-sm text-foreground">{{ item.count }}</td>
              <td class="px-3 py-2.5 text-center">
                <button class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium whitespace-nowrap bg-accent/10 text-accent hover:bg-accent/20 transition-colors"
                  @click="openRecords(item)">
                  <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>
                  </svg>
                  报工记录
                </button>
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

    <!-- 报工详情四个弹窗（与追溯查询/报工查询共用组件，弹窗内自取数据） -->
    <MaterialInputDialog v-model:visible="inputVisible" :step="inputStep" @trace-code="traceInputCode" />
    <ProcessParamDialog v-model:visible="paramVisible" :step="paramStep" />
    <InspectionDialog v-model:visible="inspectionVisible" :step="inspectionStep" />
    <SubmissionDialog v-model:visible="submissionVisible" :step="submissionStep" @open-detail="openDetailFromSubmission" />

    <!-- 查询条件弹窗（Teleport 到 body，见 CLAUDE.md「弹窗层级」） -->
    <Teleport to="body">
      <transition name="modal-fade">
        <div v-if="filterVisible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/40 p-4"
          @click.self="filterVisible = false">
          <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl border border-border flex flex-col">
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
                <span class="text-xs font-medium text-muted-foreground">报工时间起</span>
                <input v-model="startTime" type="datetime-local"
                  class="w-full px-3 py-2 rounded-lg border border-border bg-white text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
              </div>
              <div class="flex flex-col gap-1.5">
                <span class="text-xs font-medium text-muted-foreground">报工时间止</span>
                <input v-model="endTime" type="datetime-local"
                  class="w-full px-3 py-2 rounded-lg border border-border bg-white text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
              </div>
            </div>

            <div class="px-5 py-3 border-t border-border/40 bg-muted/10 flex items-center justify-between gap-2 shrink-0">
              <span class="text-xs text-muted-foreground">时间留空 = 不限，全量统计</span>
              <div class="flex items-center gap-2">
                <button class="px-4 py-2 rounded-lg text-sm font-medium border border-border bg-white text-foreground hover:bg-muted transition-colors"
                  @click="resetFilters">重置</button>
                <!-- 与报工查询页不同：那里日期是必填，本页留空即不限，故不禁用 -->
                <button class="px-5 py-2 bg-accent text-white rounded-lg text-sm font-medium hover:bg-accent/90 transition-colors disabled:opacity-50"
                  :disabled="queryLoading" @click="applyQuery">查询</button>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>

    <!-- 某不合格原因关联的报工记录（Teleport 到 body，见 CLAUDE.md「弹窗层级」）
         ⚠️ 层级用 z-[999] 而非主弹窗的 z-[1000]：这是一层列表弹窗，从它内部还能再开出
         上面那四个详情弹窗，详情弹窗必须盖在它上面。同 z-index 时由 DOM 顺序决定胜负，
         靠模板先后太脆（挪一下组件位置就翻车），故直接把 1000 让出去 -->
    <Teleport to="body">
      <transition name="modal-fade">
        <div v-if="recordVisible" class="fixed inset-0 z-[999] flex items-center justify-center bg-black/40 p-4"
          @click.self="recordVisible = false">
          <div class="bg-white rounded-xl shadow-2xl w-full max-w-[1500px] max-h-[90vh] border border-border flex flex-col">
            <div class="px-5 py-3 border-b border-border/40 flex items-center justify-between gap-3 shrink-0">
              <div class="flex items-baseline gap-2 min-w-0">
                <h3 class="text-base font-semibold text-foreground shrink-0">报工记录</h3>
                <span class="text-xs text-muted-foreground truncate">
                  不合格原因：<span class="font-medium text-foreground">{{ recordReason?.reason_name || recordReason?.reason_code || '-' }}</span>
                  <span v-if="recordReason?.reason_code" class="ml-1 font-mono text-[10px]">{{ recordReason.reason_code }}</span>
                  <span class="ml-2">共 <strong class="text-foreground">{{ recordTotal }}</strong> 条</span>
                </span>
              </div>
              <button class="shrink-0 p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                title="关闭" @click="recordVisible = false">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>

            <div v-if="recordError" class="py-8 text-center shrink-0">
              <p class="text-red-500 font-medium">{{ recordError }}</p>
            </div>

            <div v-else-if="recordLoading" class="py-10 text-center text-muted-foreground shrink-0">
              <svg class="animate-spin w-6 h-6 mx-auto mb-2 text-accent" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              <p class="text-sm">正在查询…</p>
            </div>

            <div v-else-if="recordTotal == 0" class="py-10 text-center text-muted-foreground shrink-0">
              <svg class="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <p>该原因暂无关联报工记录</p>
            </div>

            <div v-else class="overflow-auto flex-1 min-h-0">
              <table class="w-full text-left border-collapse">
                <thead class="sticky top-0 bg-white z-10">
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
                  <tr v-for="(item, idx) in recordList" :key="item.id" class="hover:bg-accent/5 transition-colors">
                    <td class="px-2 py-2.5 text-center text-muted-foreground">{{ (recordPage - 1) * recordPageSize + idx + 1 }}</td>
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

            <div v-if="recordTotal > recordPageSize"
              class="px-5 py-3 border-t border-border/40 bg-muted/10 flex items-center justify-between shrink-0">
              <span class="text-xs text-muted-foreground">
                第 {{ (recordPage - 1) * recordPageSize + 1 }}-{{ Math.min(recordPage * recordPageSize, recordTotal) }} 条，共 {{ recordTotal }} 条
              </span>
              <div class="flex items-center gap-2">
                <button class="px-3 py-1.5 rounded-lg text-xs font-medium border border-border bg-white text-foreground hover:bg-muted transition-colors disabled:opacity-40"
                  :disabled="recordPage <= 1 || recordLoading" @click="goRecordPage(recordPage - 1)">
                  上一页
                </button>
                <span class="text-xs text-muted-foreground px-2">{{ recordPage }} / {{ recordTotalPages }}</span>
                <button class="px-3 py-1.5 rounded-lg text-xs font-medium border border-border bg-white text-foreground hover:bg-muted transition-colors disabled:opacity-40"
                  :disabled="recordPage >= recordTotalPages || recordLoading" @click="goRecordPage(recordPage + 1)">
                  下一页
                </button>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, inject, watch } from 'vue'
import type { Ref } from 'vue'
import api from '../api/trace-app'
import { useProductRoutingProcess } from '../composables/useProductRoutingProcess'
import { useReportDialogs } from '../composables/useReportDialogs'
import { setPendingTraceCode } from '../composables/useTraceNav'
import { fmtTime, checkResultClass } from '../utils/trace-format'
import CustomSelect from '../components/CustomSelect.vue'
import MaterialTypeTag from '../components/trace/MaterialTypeTag'
import MaterialInputDialog from '../components/trace/MaterialInputDialog.vue'
import ProcessParamDialog from '../components/trace/ProcessParamDialog.vue'
import InspectionDialog from '../components/trace/InspectionDialog.vue'
import SubmissionDialog from '../components/trace/SubmissionDialog.vue'

const currentView = inject<Ref<string>>('currentView', ref('home'))

// 产品 / 工艺路线 / 工序 三级联动（与报工查询页共用）
const {
  productType, routingCode, processCode,
  productOptions, routingOptions, processOptions,
  loadBaseOptions, onProductChange, onRoutingChange, buildFilter,
} = useProductRoutingProcess()

// 查询条件弹窗
const filterVisible = ref(false)
// 报工时间范围（datetime-local 值）：留空 = 不限。
// ⚠️ 与报工查询页不同——那边日期必填、默认当天；本页是全量统计口径，留空即全量。
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

// datetime-local 格式（YYYY-MM-DDTHH:mm）→ 后端可比较的本地时间字符串（YYYY-MM-DD HH:mm:ss）
const toTimeString = (value: string) => {
  if (!value) return ''
  return value.replace('T', ' ') + (value.length == 16 ? ':00' : '')
}

// 时间范围只读回显（两个输入框在弹窗里，条件栏上得看得出当前范围）
const timeRangeText = computed(() => {
  const start = toTimeString(startTime.value)
  const end = toTimeString(endTime.value)
  if (start && end) return `${start} ~ ${end}`
  if (start) return `${start} 起`
  if (end) return `截至 ${end}`
  return '不限'
})

const labelOf = (opts: { label: string, value: string }[], value: string) =>
  opts.find(o => o.value == value)?.label || value

// 已选条件回显（不含时间：时间在条件栏上有独立的只读回显）
const activeChips = computed(() => {
  const chips: { key: string, label: string, text: string }[] = []
  if (productType.value) chips.push({ key: 'product', label: '产品', text: labelOf(productOptions.value, productType.value) })
  if (routingCode.value) chips.push({ key: 'routing', label: '工艺路线', text: labelOf(routingOptions.value, routingCode.value) })
  if (processCode.value) chips.push({ key: 'process', label: '工序', text: labelOf(processOptions.value, processCode.value) })
  return chips
})

// 清条件只改状态、不自动重查：清「产品」会连带清路线与工序，逐项确认完再点「查询」更省事
// 注意产品自己的值来自 v-model，onProductChange() 只清下级，故本级要显式清
const clearChip = async (key: string) => {
  if (key == 'product') { productType.value = ''; await onProductChange() }
  else if (key == 'routing') { routingCode.value = ''; await onRoutingChange() }
  else if (key == 'process') processCode.value = ''
}

const resetFilters = async () => {
  productType.value = ''
  await onProductChange()
  startTime.value = ''
  endTime.value = ''
}

const applyQuery = async () => {
  filterVisible.value = false
  await handleQuery()
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
    const res = await api.queryUnqualifiedReasons({
      ...buildFilter(),
      start_time: toTimeString(startTime.value),
      end_time: toTimeString(endTime.value),
      page: page.value,
      page_size: pageSize.value,
    })
    const data = res.data || {}
    dataList.value = data.list || []
    total.value = data.total || 0
  } catch (err: any) {
    console.error('查询不合格原因失败:', err)
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

// ========== 「报工记录」弹窗：某原因关联的报工记录（行结构与报工查询一致） ==========
const recordVisible = ref(false)
const recordReason = ref<any>(null)
const recordList = ref<any[]>([])
const recordTotal = ref(0)
const recordPage = ref(1)
const recordPageSize = ref(20)
const recordLoading = ref(false)
const recordError = ref('')

const recordTotalPages = computed(() => Math.max(1, Math.ceil(recordTotal.value / recordPageSize.value)))

// 四个报工详情弹窗的开关与当前行（与追溯查询/报工查询共用同一份协调逻辑）
const {
  inputVisible, inputStep,
  paramVisible, paramStep,
  inspectionVisible, inspectionStep,
  submissionVisible, submissionStep,
  openInput, openParam, openInspection, openSubmission,
  openDetailFromSubmission,
} = useReportDialogs()

const loadRecords = async () => {
  recordLoading.value = true
  recordError.value = ''
  try {
    const res = await api.queryUnqualifiedReasonRecords({
      ...buildFilter(),
      // 页面上的条件一并带上，保证弹窗里的记录与左侧统计的次数出自同一批检验单
      reason_code: recordReason.value?.reason_code || undefined,
      reason_name: recordReason.value?.reason_name || undefined,
      start_time: toTimeString(startTime.value),
      end_time: toTimeString(endTime.value),
      page: recordPage.value,
      page_size: recordPageSize.value,
    })
    const data = res.data || {}
    recordList.value = data.list || []
    recordTotal.value = data.total || 0
  } catch (err: any) {
    console.error('查询不合格原因关联报工记录失败:', err)
    recordList.value = []
    recordTotal.value = 0
    recordError.value = '查询失败，请检查网络或稍后重试'
  } finally {
    recordLoading.value = false
  }
}

const openRecords = async (row: any) => {
  recordReason.value = row
  recordPage.value = 1
  recordVisible.value = true
  await loadRecords()
}

const goRecordPage = (p: number) => {
  if (p < 1 || p > recordTotalPages.value) return
  recordPage.value = p
  loadRecords()
}

// 弹窗内「追溯此码」：本页无追溯入口，收掉弹窗后切到追溯查询视图（与报工查询页同一处理）
const traceInputCode = (qrCode: string) => {
  recordVisible.value = false
  setPendingTraceCode(qrCode)
  currentView.value = 'history'
}

// 条件都不选即为全表统计（时间留空 = 不限），开销不小，
// 故不在应用启动时预查（所有视图常驻挂载，onMounted 会在用户还没进这页时先跑一次），
// 改为「首次进入本页」时查一次；immediate 兜住「上次退出时正停在本页」的情况。
loadBaseOptions()
watch(currentView, (view) => {
  if (view == 'unqualified_reason' && !searched.value && !queryLoading.value) {
    handleQuery()
  }
}, { immediate: true })
</script>
