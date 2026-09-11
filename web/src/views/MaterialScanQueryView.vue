<template>
  <div class="h-full flex flex-col relative z-10 w-full max-w-[1400px] mx-auto pt-4">
    <!-- 搜索区 -->
    <div class="bg-card rounded-xl border border-border/40 p-4 shadow-sm mb-3 shrink-0">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
        <div class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-muted-foreground">码值</span>
          <input v-model="searchCode" @keydown.enter="handleQuery" type="text" placeholder="输入码值（模糊匹配）"
            class="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
        </div>
        <div class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-muted-foreground">开始时间</span>
          <input v-model="startTime" type="datetime-local"
            class="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
        </div>
        <div class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-muted-foreground">结束时间</span>
          <input v-model="endTime" type="datetime-local"
            class="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
        </div>
        <div class="flex items-end gap-2">
          <button class="flex-1 px-4 py-2 bg-accent text-white rounded-lg text-sm font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            :disabled="queryLoading || !startTime || !endTime" @click="handleQuery">
            <svg v-if="queryLoading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            查询
          </button>
        </div>
      </div>
    </div>

    <!-- 结果区 -->
    <div v-show="searched" class="bg-card rounded-xl border border-border/40 shadow-sm flex flex-col flex-1 min-h-0">
      <div class="px-4 py-2 border-b border-border/40 bg-muted/20 flex items-center justify-between shrink-0">
        <span class="text-sm text-muted-foreground">
          <template v-if="total > 0">
            共 <strong class="text-foreground">{{ total }}</strong> 条记录
          </template>
          <template v-else>
            未找到扫码登料记录
          </template>
        </span>
      </div>

      <div v-if="total == 0 && !queryError" class="py-8 text-center text-muted-foreground shrink-0">
        <svg class="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p>该条件下无扫码登料记录</p>
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
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap w-12 text-center">#</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">产品</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">工序</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">物料</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">码值</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">操作人</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">操作时间</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap w-28">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/50 text-sm">
            <tr v-for="(item, idx) in dataList" :key="item.id" class="hover:bg-accent/5 transition-colors">
              <td class="px-3 py-2.5 text-center text-muted-foreground">{{ (page - 1) * pageSize + idx + 1 }}</td>
              <td class="px-3 py-2.5">
                <p class="font-medium text-foreground max-w-[180px] truncate" :title="item.product_name">{{ item.product_name || item.product_code || '-' }}</p>
                <p class="text-xs text-muted-foreground font-mono max-w-[180px] truncate" :title="item.product_code">{{ item.product_code || '-' }}</p>
              </td>
              <td class="px-3 py-2.5">
                <p class="font-medium text-foreground max-w-[160px] truncate" :title="item.process_name">{{ item.process_name || item.process_code || '-' }}</p>
                <p class="text-xs text-muted-foreground font-mono max-w-[160px] truncate" :title="item.process_code">{{ item.process_code || '-' }}</p>
              </td>
              <td class="px-3 py-2.5">
                <p class="font-medium text-foreground max-w-[180px] truncate" :title="item.material_name">{{ item.material_name || item.material_code || '-' }}</p>
                <p class="text-xs text-muted-foreground font-mono max-w-[180px] truncate" :title="item.material_code">{{ item.material_code || '-' }}</p>
              </td>
              <td class="px-3 py-2.5 font-mono text-xs max-w-[280px] break-all" :title="item.code">{{ item.code }}</td>
              <td class="px-3 py-2.5 font-mono">{{ item.operator || '-' }}</td>
              <td class="px-3 py-2.5 text-muted-foreground text-xs whitespace-nowrap">{{ fmtTime(item.op_time) }}</td>
              <td class="px-3 py-2.5">
                <button type="button" @click="goDeviceData(item)"
                  class="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium border border-border bg-white text-foreground hover:bg-accent/10 hover:text-accent hover:border-accent/30 transition-colors whitespace-nowrap"
                  :title="item.device_code ? `查看设备 ${item.device_code} 的数采数据` : '该记录没有设备，无法跳转数采查询'">
                  <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                  数采数据
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, inject, onMounted } from 'vue'
import type { Ref } from 'vue'
import api from '../api/trace-app'
import { showToast } from '../utils/dialog'
import { navigateToDeviceData } from '../composables/useDeviceDataNav'

// 跳转数采查询需切换顶层视图（应用无 router，视图由 currentView 控制 v-show）
const currentView = inject<Ref<string>>('currentView', ref('home'))

// 查询条件
const searchCode = ref('')
const startTime = ref('')
const endTime = ref('')

// 查询状态
const queryLoading = ref(false)
const searched = ref(false)
const queryError = ref('')

// 分页数据
const dataList = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

// ========== 初始化：默认查当天 ==========
onMounted(() => {
  const now = new Date()
  startTime.value = formatDatetimeLocal(new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0))
  endTime.value = formatDatetimeLocal(new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59))
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
    const res = await api.queryMaterialScanRecords({
      code: searchCode.value.trim() || undefined,
      start_time: toTimeString(startTime.value),
      end_time: toTimeString(endTime.value),
      page: page.value,
      page_size: pageSize.value,
    })
    const data = res.data || {}
    dataList.value = data.list || []
    total.value = data.total || 0
  } catch (err: any) {
    console.error('查询扫码登料记录失败:', err)
    dataList.value = []
    total.value = 0
    queryError.value = '查询失败，请检查网络或稍后重试'
  } finally {
    queryLoading.value = false
  }
}

// ========== 数采数据：跳转数采查询并携带设备 + 操作时间±5min ==========
const goDeviceData = (item: any) => {
  const ok = navigateToDeviceData({
    device_code: item.device_code || '',
    report_time: item.op_time || '',
  })
  if (!ok) {
    showToast('该记录缺少设备或操作时间，无法跳转数采查询', 'warning')
    return
  }
  currentView.value = 'device_data'
}

// ========== 分页 ==========
const goPage = (p: number) => {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  doQuery()
}

// ========== 工具 ==========
const fmtTime = (t: string) => t ? t.replace(/\.\d+/, '').replace('T', ' ') : '-'
</script>
