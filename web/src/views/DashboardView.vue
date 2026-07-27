<template>
  <div class="dashboard-container">
    <!-- 背景装饰 -->
    <div class="bg-decorations">
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
      <div class="bg-orb bg-orb-3"></div>
      <div class="grid-lines"></div>
    </div>

    <!-- 顶栏 -->
    <header class="dashboard-header">
      <div class="header-left">
        <div class="header-left-inner">
          <div class="status-badge">
            <span class="status-dot"></span>
            <span>系统运行中</span>
          </div>
          <button class="exit-btn" @click="emit('exit')" title="退出看板">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span>退出</span>
          </button>
        </div>
      </div>
      <div class="header-center">
        <h1 class="header-title">{{ pageTitle }}</h1>
      </div>
      <div class="header-right">
        <div class="datetime-display">
          <span class="datetime-date">{{ currentDate }}</span>
          <span class="datetime-time">{{ currentTime }}</span>
        </div>
      </div>
    </header>

    <!-- 主体 - flex-1 撑满剩余高度 -->
    <main class="dashboard-main">
      <!-- KPI 卡片行 -->
      <section class="kpi-row">
        <div class="kpi-card" v-for="(kpi, idx) in kpiList" :key="idx" :style="{ animationDelay: `${idx * 0.1}s` }">
          <div class="kpi-icon" :style="{ background: kpi.iconBg }">
            <svg class="w-5 h-5" :style="{ color: kpi.iconColor }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="kpi.iconPath" />
            </svg>
          </div>
          <div class="kpi-info">
            <span class="kpi-label">{{ kpi.label }}</span>
            <div class="kpi-value-row">
              <span class="kpi-value" ref="kpiRefs">{{ formatKpiValue(kpi) }}</span>
              <span class="kpi-unit">{{ kpi.unit }}</span>
            </div>
            <div class="kpi-trend" :class="kpi.trend > 0 ? 'trend-up' : 'trend-down'">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path v-if="kpi.trend > 0" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
              <span>{{ Math.abs(kpi.trend) }}%</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 图表行 — flex-1 撑满剩余，内部再等分 -->
      <section class="charts-row">
        <!-- 产量趋势图 -->
        <div class="chart-card chart-card-wide">
          <div class="chart-header">
            <h3 class="chart-title">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
              近7日产量趋势
            </h3>
            <span class="chart-badge">周同比 +8.3%</span>
          </div>
          <div class="chart-body fill">
            <div class="bar-chart">
              <div class="bar-group" v-for="(bar, idx) in productionData" :key="idx" :style="{ animationDelay: `${idx * 0.08}s` }">
                <div class="bar-container">
                  <div class="bar-fill" :style="{ height: bar.percent + '%' }">
                    <div class="bar-glow"></div>
                  </div>
                </div>
                <span class="bar-value">{{ bar.value }}</span>
                <span class="bar-label">{{ bar.label }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 良品率 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              质量概览
            </h3>
          </div>
          <div class="chart-body fill flex-center">
            <div class="donut-container">
              <svg class="donut-svg" viewBox="0 0 120 120">
                <circle class="donut-track" cx="60" cy="60" r="50" fill="none" stroke-width="12"/>
                <circle class="donut-segment donut-segment-1" cx="60" cy="60" r="50" fill="none" stroke-width="12"
                  stroke-dasharray="251.2" stroke-dashoffset="0" style="animation-delay: 0.3s"/>
                <circle class="donut-segment donut-segment-2" cx="60" cy="60" r="50" fill="none" stroke-width="12"
                  stroke-dasharray="31.4" stroke-dashoffset="-251.2" style="animation-delay: 0.5s"/>
                <circle class="donut-segment donut-segment-3" cx="60" cy="60" r="50" fill="none" stroke-width="12"
                  stroke-dasharray="31.4" stroke-dashoffset="-282.6" style="animation-delay: 0.7s"/>
              </svg>
              <div class="donut-center">
                <span class="donut-center-value">98.2%</span>
                <span class="donut-center-label">良品率</span>
              </div>
            </div>
            <div class="donut-legend">
              <div class="legend-item"><span class="legend-dot dot-green"></span>良品 <span class="legend-num">12,580</span></div>
              <div class="legend-item"><span class="legend-dot dot-yellow"></span>返工 <span class="legend-num">168</span></div>
              <div class="legend-item"><span class="legend-dot dot-red"></span>废品 <span class="legend-num">62</span></div>
            </div>
          </div>
        </div>

        <!-- 设备稼动率 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
              设备稼动率
            </h3>
          </div>
          <div class="chart-body fill flex-center">
            <div class="gauge-wrapper">
              <svg class="gauge-svg" viewBox="0 0 200 120">
                <path class="gauge-track" d="M20,100 A80,80 0 0,1 180,100" fill="none" stroke-width="14" stroke-linecap="round"/>
                <path class="gauge-fill" d="M20,100 A80,80 0 0,1 180,100" fill="none" stroke-width="14" stroke-linecap="round"
                  stroke-dasharray="276" stroke-dashoffset="55.2" style="animation-delay: 0.3s"/>
              </svg>
              <div class="gauge-center">
                <span class="gauge-value">87.6%</span>
                <span class="gauge-label">稼动率</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 底部行 -->
      <section class="bottom-row">
        <!-- 设备状态 -->
        <div class="info-card">
          <div class="info-card-header">
            <h3 class="chart-title">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
              设备运行状态
            </h3>
            <span class="device-summary">运行 {{ deviceStats.running }} / 停机 {{ deviceStats.stopped }} / 待机 {{ deviceStats.standby }}</span>
          </div>
          <div class="device-grid">
            <div class="device-item" v-for="(dev, idx) in deviceList" :key="idx">
              <div class="device-indicator" :class="'status-' + dev.status"></div>
              <div class="device-info">
                <span class="device-name">{{ dev.name }}</span>
              </div>
              <div class="device-status-tag" :class="'tag-' + dev.status">{{ dev.statusText }}</div>
            </div>
          </div>
        </div>

        <!-- 实时报警 -->
        <div class="info-card">
          <div class="info-card-header">
            <h3 class="chart-title">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              实时报警
            </h3>
            <span class="alarm-badge">{{ alarmList.length }} 条未处理</span>
          </div>
          <div class="alarm-list">
            <div class="alarm-item" v-for="(alarm, idx) in alarmList" :key="idx" :style="{ animationDelay: `${idx * 0.15}s` }">
              <div class="alarm-level" :class="'level-' + alarm.level">
                <span class="alarm-dot"></span>
              </div>
              <div class="alarm-content">
                <span class="alarm-msg">{{ alarm.message }}</span>
                <span class="alarm-time">{{ alarm.time }}</span>
              </div>
              <div class="alarm-device">{{ alarm.device }}</div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 底部装饰线 -->
    <div class="footer-line"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '../api/trace-app'

const emit = defineEmits<{ (e: 'exit'): void }>()

const pageTitle = ref('智能生产看板')

// ========== 时钟 ==========
const currentDate = ref('')
const currentTime = ref('')

const updateClock = () => {
  const now = new Date()
  const days = ['日', '一', '二', '三', '四', '五', '六']
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  const day = days[now.getDay()]
  currentDate.value = `${y}年${m}月${d}日 星期${day}`
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false })
}

let clockTimer: number

onMounted(async () => {
  updateClock()
  clockTimer = window.setInterval(updateClock, 1000)
  loadDevices()
  try {
    const res = await api.getDashboardConfig()
    if (res.data?.title) {
      pageTitle.value = res.data.title
    }
  } catch (_) {
    // 使用默认标题
  }
})

onUnmounted(() => {
  clearInterval(clockTimer)
})

// ========== KPI 数据 ==========
const kpiList = ref([
  {
    label: '今日产量',
    value: '12842',
    displayValue: 0,
    targetValue: 12842,
    unit: '件',
    trend: 12.5,
    iconBg: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
    iconColor: '#fff',
    iconPath: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6',
  },
  {
    label: '设备稼动率',
    value: '87.6',
    displayValue: 0,
    targetValue: 87.6,
    unit: '%',
    trend: 3.2,
    iconBg: 'linear-gradient(135deg, #06b6d4, #0891b2)',
    iconColor: '#fff',
    iconPath: 'M4 6h16M4 10h16M4 14h16M4 18h16',
  },
  {
    label: '良品率',
    value: '98.2',
    displayValue: 0,
    targetValue: 98.2,
    unit: '%',
    trend: 1.8,
    iconBg: 'linear-gradient(135deg, #10b981, #059669)',
    iconColor: '#fff',
    iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  {
    label: '在线设备',
    value: '18',
    displayValue: 0,
    targetValue: 18,
    unit: '台',
    trend: -1.2,
    iconBg: 'linear-gradient(135deg, #8b5cf6, #6d28d9)',
    iconColor: '#fff',
    iconPath: 'M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z',
  },
])

const kpiRefs = ref<any[]>([])

const formatKpiValue = (kpi: any) => {
  if (kpi.value.includes('.')) {
    return Number(kpi.displayValue).toFixed(1)
  }
  return Math.floor(kpi.displayValue).toLocaleString()
}

// ========== 产量数据 ==========
const productionData = [
  { label: '07/21', value: 1680, percent: 72 },
  { label: '07/22', value: 1520, percent: 65 },
  { label: '07/23', value: 1850, percent: 79 },
  { label: '07/24', value: 1720, percent: 74 },
  { label: '07/25', value: 1980, percent: 85 },
  { label: '07/26', value: 2100, percent: 90 },
  { label: '07/27', value: 2050, percent: 88 },
]

// ========== 设备数据（从接口获取，状态随机） ==========
const statusTextMap: Record<string, string> = { running: '运行中', stopped: '已停机', standby: '待机中' }
const statusOptions = ['running', 'stopped', 'standby'] as const

const deviceList = ref<{ name: string; code: string; status: string; statusText: string }[]>([])

const deviceStats = computed(() => {
  const running = deviceList.value.filter(d => d.status == 'running').length
  const stopped = deviceList.value.filter(d => d.status == 'stopped').length
  const standby = deviceList.value.filter(d => d.status == 'standby').length
  return { running, stopped, standby }
})

const loadDevices = async () => {
  try {
    const res = await api.queryDeviceList()
    const list: { name: string; code: string }[] = res.data || []
    deviceList.value = list.map(d => {
      const status = statusOptions[Math.floor(Math.random() * statusOptions.length)]
      return { ...d, status, statusText: statusTextMap[status] }
    })
  } catch (err: any) {
    console.error('加载设备列表失败:', err)
    // fallback 静态数据
    deviceList.value = [
      { name: 'SMT贴片机#1', code: 'SMT-001', status: 'running', statusText: '运行中' },
      { name: '回流焊炉#1', code: 'REF-001', status: 'running', statusText: '运行中' },
    ]
  }
}

// ========== 报警数据 ==========
const alarmList = [
  { level: 'warning', message: 'SMT-003 温度异常偏高，建议检查加热模块', time: '14:32', device: 'SMT-003' },
  { level: 'error', message: 'AOI-002 视觉检测偏差超限，需重新校准', time: '14:15', device: 'AOI-002' },
  { level: 'info', message: 'REF-001 已完成定期维护，状态正常', time: '13:50', device: 'REF-001' },
  { level: 'warning', message: '原料仓库存低于安全水位，请及时补充', time: '13:20', device: 'WMS' },
]
</script>

<style scoped>
/* ========== 容器 — 全屏固定，禁止滚动 ========== */
.dashboard-container {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0a1628 0%, #0f1f3d 30%, #152a50 60%, #0f1f3d 100%);
  padding: 0 24px;
  overflow: hidden;
}

/* ========== 背景装饰 ========== */
.bg-decorations {
  @apply absolute inset-0 overflow-hidden pointer-events-none;
  z-index: 0;
}

.bg-orb {
  @apply absolute rounded-full;
  filter: blur(30px);
  opacity: 0.12;
  will-change: transform;
}

.bg-orb-1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #3b82f6, transparent);
  top: -150px;
  right: -100px;
  animation: orbFloat 20s ease-in-out infinite;
}

.bg-orb-2 {
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, #06b6d4, transparent);
  bottom: -80px;
  left: -80px;
  animation: orbFloat 25s ease-in-out infinite reverse;
}

.bg-orb-3 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, #8b5cf6, transparent);
  top: 50%;
  left: 60%;
  animation: orbFloat 30s ease-in-out infinite 5s;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -40px) scale(1.05); }
  66% { transform: translate(-20px, 20px) scale(0.95); }
}

.grid-lines {
  @apply absolute inset-0;
  background-image:
    linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  opacity: 0.6;
}

/* ========== 顶栏 — 固定高度 ========== */
.dashboard-header {
  @apply relative z-10 flex items-center justify-between shrink-0;
  height: 60px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.header-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.header-left-inner {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title {
  @apply text-lg font-bold tracking-tight;
  color: #f0f4ff;
}

.datetime-display {
  @apply flex flex-col items-center;
}

.datetime-date {
  @apply text-xs;
  color: rgba(200, 218, 255, 0.7);
  font-family: monospace;
}

.datetime-time {
  @apply text-2xl font-bold tracking-wider;
  color: #93c5fd;
  font-family: monospace;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

.status-badge {
  @apply flex items-center gap-2 px-3 py-1.5 rounded-full text-xs;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.exit-btn {
  @apply flex items-center gap-1.5 ml-3 px-3 py-1.5 rounded-full text-xs transition-all duration-200;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.15);
  color: rgba(248, 113, 113, 0.8);
}

.exit-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.25);
  color: #f87171;
}

/* ========== 主体 — flex 撑满剩余空间 ========== */
.dashboard-main {
  @apply relative z-10 flex flex-col flex-1 min-h-0;
  gap: 12px;
  padding-top: 12px;
  padding-bottom: 12px;
}

/* ========== KPI 卡片行 — 固定比例 ========== */
.kpi-row {
  @apply grid grid-cols-4 gap-3 shrink-0;
}

.kpi-card {
  @apply rounded-xl p-4 flex items-start gap-3;
  background: linear-gradient(135deg, rgba(30, 58, 95, 0.5), rgba(15, 31, 61, 0.3));
  border: 1px solid rgba(59, 130, 246, 0.15);
  /* opt: removed backdrop-filter for perf */
  animation: kpiFadeIn 0.6s ease-out both;
}

@keyframes kpiFadeIn {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.kpi-card:hover {
  border-color: rgba(59, 130, 246, 0.35);
  box-shadow: 0 8px 30px rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
  transition: all 0.3s ease;
}

.kpi-icon {
  @apply w-10 h-10 rounded-xl flex items-center justify-center shrink-0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.kpi-info {
  @apply flex-1 min-w-0;
}

.kpi-label {
  @apply text-xs font-medium;
  color: rgba(148, 184, 255, 0.7);
  display: block;
  margin-bottom: 2px;
}

.kpi-value-row {
  @apply flex items-baseline gap-1;
}

.kpi-value {
  @apply text-2xl font-bold tracking-tight;
  color: #f0f4ff;
  font-variant-numeric: tabular-nums;
}

.kpi-unit {
  @apply text-xs;
  color: rgba(148, 184, 255, 0.5);
}

.kpi-trend {
  @apply flex items-center gap-0.5 mt-1 text-xs font-medium;
}

.trend-up { color: #34d399; }
.trend-down { color: #f87171; }

/* ========== 图表行 — flex-1，3列 ========== */
.charts-row {
  @apply grid grid-cols-4 gap-3 flex-1 min-h-0;
}

.chart-card {
  @apply rounded-xl p-4 flex flex-col;
  background: linear-gradient(135deg, rgba(30, 58, 95, 0.4), rgba(15, 31, 61, 0.2));
  border: 1px solid rgba(59, 130, 246, 0.12);
  /* opt: removed backdrop-filter for perf */
  min-height: 0;
}

.chart-card-wide {
  @apply col-span-2;
}

.chart-header {
  @apply flex items-center justify-between shrink-0;
  margin-bottom: 8px;
}

.chart-title {
  @apply flex items-center gap-2 text-sm font-semibold;
  color: rgba(200, 218, 255, 0.9);
}

.chart-badge {
  @apply text-xs px-2 py-0.5 rounded-full font-medium;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.chart-body {
  @apply w-full;
}

.chart-body.fill {
  @apply flex-1 min-h-0;
}

.flex-center {
  @apply flex items-center justify-center;
}

/* ========== 柱状图 ========== */
.bar-chart {
  @apply flex items-end justify-between h-full gap-1.5;
  padding-top: 4px;
}

.bar-group {
  @apply flex flex-col items-center flex-1 gap-0.5 h-full;
  animation: barRise 0.8s ease-out both;
}

@keyframes barRise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.bar-container {
  @apply w-full rounded-t-sm relative;
  flex: 1;
  background: rgba(59, 130, 246, 0.08);
  min-height: 4px;
  align-self: flex-end;
}

.bar-fill {
  @apply w-full rounded-t-sm absolute bottom-0 left-0 transition-all duration-1000;
  background: linear-gradient(180deg, #60a5fa, #3b82f6);
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.3);
  animation: barFill 1s ease-out both;
}

@keyframes barFill {
  from { height: 0 !important; }
}

.bar-glow {
  @apply absolute top-0 left-0 right-0 h-1 rounded-full;
  background: rgba(255, 255, 255, 0.3);
}

.bar-value {
  @apply text-xs font-semibold;
  color: rgba(200, 218, 255, 0.9);
}

.bar-label {
  @apply text-[10px];
  color: rgba(148, 184, 255, 0.5);
}

/* ========== 环形图 ========== */
.donut-container {
  @apply relative;
  width: 130px;
  height: 130px;
}

.donut-svg {
  @apply w-full h-full;
  transform: rotate(-90deg);
}

.donut-track {
  stroke: rgba(59, 130, 246, 0.08);
}

.donut-segment {
  transition: stroke-dashoffset 1.5s ease;
  animation: donutFill 1.5s ease-out both;
}

@keyframes donutFill {
  from { stroke-dashoffset: 314; }
}

.donut-segment-1 { stroke: #34d399; }
.donut-segment-2 { stroke: #fbbf24; }
.donut-segment-3 { stroke: #f87171; }

.donut-center {
  @apply absolute inset-0 flex flex-col items-center justify-center;
}

.donut-center-value {
  @apply text-xl font-bold;
  color: #f0f4ff;
}

.donut-center-label {
  @apply text-[10px];
  color: rgba(148, 184, 255, 0.6);
}

.donut-legend {
  @apply flex justify-center gap-3 mt-2 text-xs;
  color: rgba(200, 218, 255, 0.7);
}

.legend-item {
  @apply flex items-center gap-1;
}

.legend-dot {
  @apply w-2 h-2 rounded-full;
}

.dot-green { background: #34d399; }
.dot-yellow { background: #fbbf24; }
.dot-red { background: #f87171; }

.legend-num {
  @apply font-medium;
  color: rgba(200, 218, 255, 0.9);
}

/* ========== 仪表盘 ========== */
.gauge-wrapper {
  @apply relative;
  width: 180px;
}

.gauge-svg {
  @apply w-full;
  overflow: visible;
}

.gauge-track {
  stroke: rgba(59, 130, 246, 0.08);
}

.gauge-fill {
  stroke: #3b82f6;
  animation: gaugeFill 1.5s ease-out both;
  filter: drop-shadow(0 0 6px rgba(59, 130, 246, 0.4));
}

@keyframes gaugeFill {
  from { stroke-dashoffset: 276; }
}

.gauge-center {
  @apply absolute flex flex-col items-center;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -60%);
}

.gauge-value {
  @apply text-3xl font-bold;
  color: #60a5fa;
  text-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

.gauge-label {
  @apply text-xs;
  color: rgba(148, 184, 255, 0.6);
}

/* ========== 底部行 ========== */
.bottom-row {
  @apply grid grid-cols-2 shrink-0;
  gap: 8px;
}

.info-card {
  @apply rounded-xl flex flex-col;
  padding: 10px 12px;
  background: linear-gradient(135deg, rgba(30, 58, 95, 0.4), rgba(15, 31, 61, 0.2));
  border: 1px solid rgba(59, 130, 246, 0.12);
  /* opt: removed backdrop-filter for perf */
}

.info-card-header {
  @apply flex items-center justify-between shrink-0;
  margin-bottom: 6px;
}

/* ========== 设备列表 ========== */
.device-summary {
  font-size: 10px;
  color: rgba(148, 184, 255, 0.45);
}

.device-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 6px;
  flex: 1;
  align-content: start;
}

.device-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  border-radius: 6px;
  transition: background 0.2s;
  background: rgba(59, 130, 246, 0.04);
  border: 1px solid rgba(59, 130, 246, 0.08);
}

.device-item:hover {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.15);
}

.device-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-running { background: #10b981; box-shadow: 0 0 6px rgba(16, 185, 129, 0.5); animation: pulseDot 2s ease-in-out infinite; will-change: opacity; }
.status-stopped { background: #ef4444; box-shadow: 0 0 6px rgba(239, 68, 68, 0.4); }
.status-standby { background: #f59e0b; box-shadow: 0 0 6px rgba(245, 158, 11, 0.4); }

.device-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  line-height: 1.2;
}

.device-name {
  font-size: 11px;
  font-weight: 600;
  color: rgba(200, 218, 255, 0.85);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}


.device-status-tag {
  font-size: 9px;
  padding: 1px 5px;
  border-radius: 3px;
  flex-shrink: 0;
  line-height: 1.4;
}

.tag-running { background: rgba(16, 185, 129, 0.1); color: #34d399; }
.tag-stopped { background: rgba(239, 68, 68, 0.1); color: #f87171; }
.tag-standby { background: rgba(245, 158, 11, 0.1); color: #fbbf24; }

/* ========== 报警列表 ========== */
.alarm-badge {
  @apply text-xs px-2 py-0.5 rounded-full font-medium;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #f87171;
  animation: alarmPulse 2s ease-in-out infinite;
}

@keyframes alarmPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.alarm-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  overflow: hidden;
}

.alarm-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 5px 8px;
  border-radius: 5px;
  background: rgba(59, 130, 246, 0.04);
  border: 1px solid rgba(59, 130, 246, 0.08);
  animation: alarmSlide 0.4s ease-out both;
}

@keyframes alarmSlide {
  from { opacity: 0; transform: translateX(-12px); }
  to { opacity: 1; transform: translateX(0); }
}

.alarm-level {
  padding-top: 3px;
}

.alarm-dot {
  display: block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.level-warning .alarm-dot { background: #f59e0b; box-shadow: 0 0 6px rgba(245, 158, 11, 0.5); }
.level-error .alarm-dot { background: #ef4444; box-shadow: 0 0 6px rgba(239, 68, 68, 0.5); animation: alarmPulse 1.5s ease-in-out infinite; will-change: opacity; }
.level-info .alarm-dot { background: #3b82f6; box-shadow: 0 0 6px rgba(59, 130, 246, 0.5); }

.alarm-content {
  @apply flex flex-col flex-1 min-w-0;
}

.alarm-msg {
  font-size: 11px;
  color: rgba(200, 218, 255, 0.8);
  line-height: 1.3;
}

.alarm-time {
  font-size: 9px;
  font-family: monospace;
  margin-top: 1px;
  color: rgba(148, 184, 255, 0.35);
}

.alarm-device {
  font-size: 9px;
  font-family: monospace;
  flex-shrink: 0;
  margin-left: 6px;
  color: rgba(148, 184, 255, 0.3);
}

/* ========== 底部 ========== */
.footer-line {
  @apply relative z-10 shrink-0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.2), transparent);
}

/* ========== 全局禁止选中（电视专用） ========== */
.dashboard-container * {
  user-select: none;
  -webkit-user-select: none;
}
</style>
