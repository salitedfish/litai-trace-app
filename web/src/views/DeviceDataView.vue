<template>
  <div class="h-full flex flex-col relative z-10 w-full max-w-[1400px] mx-auto pt-4">
    <!-- 搜索区 -->
    <div class="bg-card rounded-xl border border-border/40 p-4 shadow-sm mb-3 shrink-0">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-3 items-end">
        <div class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-muted-foreground">设备</span>
          <CustomSelect
            v-model="selectedDevice"
            :options="deviceOptions"
            placeholder="请选择设备"
            variant="outline"
            :disabled="deviceLoading"
            searchable
          />
        </div>
        <div class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-muted-foreground">点位</span>
          <CustomSelect
            v-model="selectedPoint"
            :options="pointOptions"
            placeholder="全部点位"
            variant="outline"
            :disabled="!selectedDevice || pointLoading"
            searchable
          />
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
            :disabled="queryLoading || !selectedDevice || !startTime || !endTime" @click="handleQuery">
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
            未找到数采数据
          </template>
        </span>
      </div>

      <div v-if="total == 0 && !queryError" class="py-8 text-center text-muted-foreground shrink-0">
        <svg class="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p>该条件下无数采数据</p>
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
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">信号编码</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">信号值</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">采集时间</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/50 text-sm">
            <tr v-for="(item, idx) in dataList" :key="item.code + '-' + idx" class="hover:bg-accent/5 transition-colors">
              <td class="px-3 py-2.5 text-center text-muted-foreground">{{ (page - 1) * pageSize + idx + 1 }}</td>
              <td class="px-3 py-2.5 font-mono text-xs max-w-[300px] break-all" :title="item.code">{{ item.code }}</td>
              <td class="px-3 py-2.5 font-mono text-sm font-semibold" :class="valueColorClass(item.value)">{{ item.value }}</td>
              <td class="px-3 py-2.5 text-muted-foreground text-xs">{{ fmtTime(item.timestamp) }}</td>
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
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api/trace-app'
import CustomSelect from '../components/CustomSelect.vue'
import { useDeviceDataNav, formatDatetimeLocal } from '../composables/useDeviceDataNav'

// 追溯查询跳转预填状态（TraceQueryView 写入）
const { state: deviceDataNavState } = useDeviceDataNav()

// 设备列表
const selectedDevice = ref('')
const deviceOptions = ref<{ label: string, value: string }[]>([])
const deviceLoading = ref(false)

// 点位列表
const selectedPoint = ref('')
const pointOptions = ref<{ label: string, value: string }[]>([])
const pointLoading = ref(false)


// 切换设备时重新加载点位
watch(selectedDevice, () => {
  selectedPoint.value = ''
  pointOptions.value = []
  loadDevicePoints()
})

// 时间范围
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

// ========== 初始化 ==========
onMounted(async () => {
  await loadDeviceList()
  // 默认时间范围：最近一周
  const now = new Date()
  const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  startTime.value = formatDatetimeLocal(oneWeekAgo)
  endTime.value = formatDatetimeLocal(now)
})

// ========== 设备列表 ==========
const loadDeviceList = async () => {
  deviceLoading.value = true
  try {
    const res = await api.queryDeviceList()
    const list = res.data || []
    deviceOptions.value = list.map((d: any) => ({
      label: `${d.name} (${d.code})`,
      value: d.code,
    }))
  } catch (err: any) {
    console.error('加载设备列表失败:', err)
  } finally {
    deviceLoading.value = false
  }
}

// ========== 点位列表 ==========
const loadDevicePoints = async () => {
  if (!selectedDevice.value) {
    pointOptions.value = []
    return
  }
  pointLoading.value = true
  try {
    const res = await api.queryDevicePoints(selectedDevice.value)
    const list = res.data || []
    pointOptions.value = list.map((p: any) => ({
      label: `${p.name} (${p.code})`,
      value: p.code,
    }))
  } catch (err: any) {
    console.error('加载点位列表失败:', err)
    pointOptions.value = []
  } finally {
    pointLoading.value = false
  }
}

// ========== 查询 ==========
const handleQuery = async () => {
  if (!selectedDevice.value || !startTime.value || !endTime.value) return

  page.value = 1
  await doQuery()
}

const doQuery = async () => {
  queryLoading.value = true
  queryError.value = ''
  searched.value = true
  try {
    // 将 datetime-local 格式转为 ISO 8601
    const st = new Date(startTime.value).toISOString()
    const et = new Date(endTime.value).toISOString()

    const res = await api.queryDeviceData({
      device_code: selectedDevice.value,
      point_code: selectedPoint.value || undefined,
      start_time: st,
      end_time: et,
      page: page.value,
      page_size: pageSize.value,
    })
    const data = res.data || {}
    dataList.value = data.list || []
    total.value = data.total || 0
  } catch (err: any) {
    console.error('查询数采数据失败:', err)
    dataList.value = []
    total.value = 0
    queryError.value = '查询失败，请检查网络或稍后重试'
  } finally {
    queryLoading.value = false
  }
}

// ========== 接收追溯查询跳转预填（工艺参数 → 数采数据） ==========
// TraceQueryView 写入 deviceDataNavState.pending=true 后，填充搜索栏并自动查询
watch(() => deviceDataNavState.pending, async (pending) => {
  if (!pending) return
  try {
    // 设备列表尚未加载则先加载（正常进入页面时 onMounted 已加载）
    if (deviceOptions.value.length == 0) {
      await loadDeviceList()
    }
    if (deviceDataNavState.device_code) {
      selectedDevice.value = deviceDataNavState.device_code
      startTime.value = deviceDataNavState.start_time
      endTime.value = deviceDataNavState.end_time
      // 点位清空，查询该设备全部点位
      selectedPoint.value = ''
      pointOptions.value = []
      await handleQuery()
    }
  } catch (err) {
    console.error('应用数采查询预填失败:', err)
  } finally {
    deviceDataNavState.pending = false
  }
})

// ========== 分页 ==========
const goPage = (p: number) => {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  doQuery()
}

// ========== 工具 ==========
const fmtTime = (t: string) => t ? t.replace(/\.\d+/, '').replace('T', ' ') : '-'

const valueColorClass = (v: string) => {
  if (!v || v == '-') return ''
  // 数值型信号值根据大小给颜色
  const n = Number(v)
  if (!isNaN(n)) {
    if (n == 0) return 'text-muted-foreground'
    if (n > 0) return 'text-emerald-600'
    return 'text-rose-600'
  }
  // 非数值（如 OK/NG）
  const lower = v.toLowerCase()
  if (lower == 'ok' || lower == '合格' || lower == '正常') return 'text-emerald-600'
  if (lower == 'ng' || lower == '不合格' || lower == '异常') return 'text-rose-600'
  return ''
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #E2E8F0; border-radius: 20px; }
</style>
