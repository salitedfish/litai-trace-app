<template>
  <div class="tech-panel reason-pie-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9 9 0 1021 13a9 9 0 00-9-9v.001zM13 11V3.055A9.001 9.001 0 0021 13h-8z" />
        </svg>
        不合格原因占比
      </h3>
      <div class="header-right-group">
        <!-- 生效筛选（产线 / 产品型号），缩略展示、悬停看全量 -->
        <span class="filter-chip" :title="'产线：' + lineLabel">产线：{{ lineLabel }}</span>
        <span class="filter-chip" :title="'产品型号：' + typeLabel">型号：{{ typeLabel }}</span>
        <span class="tech-badge" :class="loaded ? 'live' : ''">
          <span class="tech-dot"></span>
          {{ loading ? '加载中' : loaded ? '已更新' : '未加载' }}
        </span>
      </div>
    </div>

    <!-- 首次加载 / 失败 / 空态 -->
    <div v-if="!loaded && loading" class="tech-placeholder">
      <span class="placeholder-blink">▮</span>&nbsp;加载中...
    </div>
    <div v-else-if="!loaded && error" class="tech-placeholder">{{ error }}</div>
    <div v-else-if="total == 0" class="tech-placeholder">
      <span class="placeholder-blink">▮</span>&nbsp;暂无不合格原因
    </div>

    <!-- 圆环 + 图例 -->
    <div v-else class="pie-body">
      <div class="donut-wrap">
        <svg class="donut" viewBox="0 0 120 120">
          <!-- 底环轨道 -->
          <circle cx="60" cy="60" r="48" fill="none" stroke="rgba(148, 184, 255, 0.1)" stroke-width="13" />
          <!-- 各原因扇区（每段一条整圆虚线，旋转定位，从 12 点方向开始顺时针） -->
          <circle
            v-for="seg in donutSegments"
            :key="seg.key"
            cx="60" cy="60" r="48" fill="none"
            :stroke="seg.color"
            stroke-width="13"
            :stroke-dasharray="seg.dasharray"
            :stroke-dashoffset="seg.offset"
            transform="rotate(-90 60 60)"
          />
        </svg>
        <div class="donut-center">
          <span class="donut-total">{{ total }}</span>
          <span class="donut-label">不合格原因</span>
        </div>
      </div>

      <!-- 右侧列表：表头固定 + SeamlessScroll 单步循环滚动（表头/表体拆成两表，列宽用 col-* 对齐） -->
      <div class="pie-list">
        <table class="pie-table">
          <thead>
            <tr>
              <th class="col-name">原因</th>
              <th class="col-count">次数</th>
              <th class="col-percent">占比</th>
            </tr>
          </thead>
        </table>

        <SeamlessScroll class="pie-list-scroll">
          <table class="pie-table">
            <tbody>
              <tr v-for="seg in donutSegments" :key="seg.key">
                <td class="cell-name col-name" :title="seg.reason_name">
                  <i class="legend-swatch" :style="{ background: seg.color, boxShadow: `0 0 5px ${seg.color}` }"></i>
                  {{ seg.reason_name }}
                </td>
                <td class="cell-count col-count">{{ seg.count }}</td>
                <td class="cell-percent col-percent">{{ seg.percent }}%</td>
              </tr>
            </tbody>
          </table>
        </SeamlessScroll>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue'
import api from '../../../api/trace-app'
import SeamlessScroll from '../../../components/ui/SeamlessScroll.vue'

interface PieParams {
  start_date?: string
  end_date?: string
  workshop_code?: string
  product_types?: string[]
}

interface PieSegment {
  key: string
  reason_name: string
  count: number
  percent: number
  color: string
  dasharray: string
  offset: string
}

const props = defineProps<{ workshopName?: string }>()

// ========== 数据与请求状态（进看板由父组件调用 load()，不自行 onMounted 查） ==========
const reasons = ref<{ reason_name: string, count: number }[]>([])
const loading = ref(false)
const loaded = ref(false)
const error = ref('')
// 最近一次请求参数（60s 自动刷新沿用）
const recentParams = ref<PieParams>({})
const recentTypes = ref<string[]>([])
let timer: number | null = null

// 扇区色板（科技风，深色底高对比）；超出条数合并为「其他」灰
const PALETTE = ['#38bdf8', '#a78bfa', '#f472b6', '#34d399', '#fbbf24', '#fb7185', '#f97316', '#e879f9', '#22d3ee']
const OTHER_COLOR = '#5b6b8c'
const TOP_N = 9

// 头部筛选标签（产线名由父组件解析传入，缺省显示全部）
const lineLabel = computed(() => props.workshopName || '全部')
const typeLabel = computed(() => recentTypes.value.length ? recentTypes.value.join('、') : '全部')

// 勾选原因总次数（饼图样本总数，用于算占比与扇区弧长）
const total = computed(() => reasons.value.reduce((s, it) => s + it.count, 0))

// 圆环扇区：取被勾选次数降序前 N 条 + 其余合并“其他”，算好占比与 SVG 虚线段
const donutSegments = computed<PieSegment[]>(() => {
  const rows: PieSegment[] = []
  let otherCount = 0
  for (let i = 0; i < reasons.value.length; i++) {
    const it = reasons.value[i]
    if (i < TOP_N) {
      rows.push({
        key: 'seg' + i,
        reason_name: it.reason_name,
        count: it.count,
        percent: 0,
        color: PALETTE[i % PALETTE.length],
        dasharray: '',
        offset: '',
      })
    } else {
      otherCount += it.count
    }
  }
  if (otherCount > 0) {
    rows.push({ key: 'seg_other', reason_name: '其他', count: otherCount, percent: 0, color: OTHER_COLOR, dasharray: '', offset: '' })
  }

  const R = 48
  const C = 2 * Math.PI * R
  const totalN = total.value
  let cum = 0
  for (const row of rows) {
    const frac = totalN ? row.count / totalN : 0
    row.percent = Math.round(frac * 1000) / 10
    const segLen = C * frac
    row.dasharray = segLen + ' ' + C
    row.offset = -cum + ''
    cum += segLen
  }
  return rows
})

/** 供父组件进看板时调用：保存最近参数并立即查询，之后按 60s 自动刷新 */
function load(params: PieParams) {
  const p = params || {}
  recentParams.value = { ...p }
  recentTypes.value = Array.isArray(p.product_types) ? p.product_types.slice() : []
  if (timer != null) {
    clearInterval(timer)
    timer = null
  }
  doFetch()
  timer = window.setInterval(doFetch, 60000)
}

async function doFetch() {
  loading.value = true
  try {
    const res = await api.queryUnqualifiedReasonPie(recentParams.value)
    const data = Array.isArray(res.data) ? res.data : []
    reasons.value = data
      .map((it: any) => ({
        reason_name: String(it.reason_name || it.reason_code || ''),
        count: Number(it.count) || 0,
      }))
      .filter(it => it.count > 0)
    loaded.value = true
    error.value = ''
  } catch (err: any) {
    console.error('加载不合格原因占比失败:', err)
    error.value = '数据加载失败'
  } finally {
    loading.value = false
  }
}

defineExpose({ load })

onUnmounted(() => {
  if (timer != null) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped>
.reason-pie-panel {
  @apply p-3 flex flex-col;
  min-height: 0;
}

/* 压缩面板头间距（覆盖全局默认，与历史数据卡一致） */
.reason-pie-panel .tech-panel-header {
  margin-bottom: 5px;
  padding-bottom: 4px;
}

.reason-pie-panel .tech-panel-title {
  font-size: 12px;
}

.reason-pie-panel .tech-badge {
  font-size: 10px;
  padding: 1px 6px;
  letter-spacing: 0.04em;
}

.header-right-group {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

/* 生效筛选标签（产线 / 产品型号） */
.filter-chip {
  display: inline-flex;
  align-items: center;
  max-width: 96px;
  padding: 1px 6px;
  border-radius: 999px;
  font-size: 10px;
  letter-spacing: 0.04em;
  color: rgba(148, 184, 255, 0.85);
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.22);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ========== 主体：左圆环 + 右图例 ========== */
.pie-body {
  @apply flex-1 flex items-center gap-2 min-h-0;
  padding: 2px 0;
}

.donut-wrap {
  position: relative;
  width: 132px;
  height: 132px;
  flex-shrink: 0;
}

.donut {
  width: 100%;
  height: 100%;
}

.donut-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  pointer-events: none;
}

.donut-total {
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
  color: #f0f4ff;
  text-shadow: 0 0 12px rgba(56, 189, 248, 0.55);
}

.donut-label {
  font-size: 10px;
  letter-spacing: 0.18em;
  color: rgba(148, 184, 255, 0.6);
}

/* ========== 右侧列表：表头固定 + SeamlessScroll 明细滚动（参照工序加工情况卡） ========== */
.pie-list {
  @apply flex-1 min-w-0 min-h-0;
  align-self: stretch;
  display: flex;
  flex-direction: column;
}

/* 滚动区交给通用 SeamlessScroll，这里只约束布局高度 */
.pie-list-scroll {
  @apply flex-1 min-h-0;
}

/* 表格：表头/表体拆成两表，列宽用 col-* 在 th/td 共用保证对齐 */
.pie-table {
  width: 100%;
  table-layout: fixed;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 10px;
}

.pie-table thead th {
  line-height: 14px; /* 行高须为整数（line-height 固定整数 px），配合 SeamlessScroll 单步滚动不抖动 */
  padding: 4px 6px;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: rgba(176, 205, 255, 0.9);
  background: linear-gradient(180deg, #0d2148 0%, #0a1a3d 100%);
  border-bottom: 1px solid rgba(56, 189, 248, 0.25);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: middle;
}

.pie-table tbody td {
  line-height: 14px; /* 行高须为整数，配合 SeamlessScroll 单步滚动不抖动 */
  padding: 3px 6px;
  border-bottom: 1px solid rgba(56, 189, 248, 0.06);
  text-align: center;
  vertical-align: middle;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: background 0.15s ease;
}

.pie-table tbody tr:hover td {
  background: rgba(59, 130, 246, 0.08);
}

/* 列宽：原因偏宽左对齐，次数/占比较窄居中 */
.col-name { width: 52%; }
.col-count { width: 20%; }
.col-percent { width: 28%; }

.pie-table thead th.col-name,
.pie-table tbody td.col-name {
  text-align: left;
  padding-left: 8px;
}

/* 原因名称文本颜色（表格 td 不设色会继承到页面默认黑，参照工序名称 prod-name） */
.pie-table tbody td.cell-name {
  color: rgba(200, 218, 255, 0.88);
}

/* 原因色块 */
.legend-swatch {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 2px;
  margin-right: 5px;
  vertical-align: middle;
}

/* 数值列：等宽数字 */
.pie-table tbody td.col-count {
  color: #f0f4ff;
  font-family: 'Consolas', 'Courier New', monospace;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.pie-table tbody td.col-percent {
  color: #7dd3fc;
  font-family: 'Consolas', 'Courier New', monospace;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.placeholder-blink {
  color: #38bdf8;
  animation: techPulse 1.2s ease-in-out infinite;
}
</style>
