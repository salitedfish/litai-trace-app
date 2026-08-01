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
          <button class="filter-btn" @click="showFilter = true" title="更多操作">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          <button class="exit-btn" @click="emit('exit')" title="退出看板">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <!-- <span>退出</span> -->
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

    <!-- 主体 -->
    <main class="dashboard-main">
      <!-- 图表行 -->
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

        <!-- OEE 综合展示 -->
        <div class="chart-card chart-card-wide">
          <div class="chart-header">
            <h3 class="chart-title">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
              设备 OEE
            </h3>
            <span class="chart-badge" :class="{ 'text-green-400': connected }">
              {{ connected ? '实时' : '断开' }}
            </span>
          </div>
          <div class="chart-body fill oee-body">
            <!-- 左侧：仪表盘 -->
            <div class="oee-gauge-area">
              <svg class="oee-gauge-svg" viewBox="0 0 200 110">
                <!-- 背景弧 -->
                <path d="M20,95 A80,80 0 0,1 180,95" fill="none" stroke-width="14" stroke-linecap="round" stroke="rgba(59,130,246,0.08)"/>
                <!-- 色区：红 0-30% -->
                <path d="M20,95 A80,80 0 0,1 72,33.6" fill="none" stroke-width="14" stroke-linecap="round" stroke="rgba(239,68,68,0.15)"/>
                <!-- 色区：黄 30-60% -->
                <path d="M72,33.6 A80,80 0 0,1 128,33.6" fill="none" stroke-width="14" stroke-linecap="round" stroke="rgba(245,158,11,0.15)"/>
                <!-- 色区：绿 60-100% -->
                <path d="M128,33.6 A80,80 0 0,1 180,95" fill="none" stroke-width="14" stroke-linecap="round" stroke="rgba(16,185,129,0.15)"/>
                <!-- 填充弧渐变 -->
                <defs>
                  <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#ef4444"/>
                    <stop offset="40%" stop-color="#f59e0b"/>
                    <stop offset="70%" stop-color="#10b981"/>
                    <stop offset="100%" stop-color="#06b6d4"/>
                  </linearGradient>
                </defs>
                <path d="M20,95 A80,80 0 0,1 180,95" fill="none" stroke="url(#gaugeGrad)" stroke-width="14" stroke-linecap="round"
                  stroke-dasharray="264" :stroke-dashoffset="gaugeOffset"/>
                <!-- 刻度 -->
                <circle cx="20" cy="95" r="3" fill="rgba(148,184,255,0.3)"/>
                <circle cx="51.2" cy="43.6" r="2.5" fill="rgba(148,184,255,0.2)"/>
                <circle cx="100" cy="15" r="3" fill="rgba(148,184,255,0.3)"/>
                <circle cx="148.8" cy="43.6" r="2.5" fill="rgba(148,184,255,0.2)"/>
                <circle cx="180" cy="95" r="3" fill="rgba(148,184,255,0.3)"/>
              </svg>
              <div class="oee-gauge-value">
                <span class="oee-gauge-num">{{ oeePercent.toFixed(1) }}%</span>
              </div>
              <div class="oee-gauge-label">OEE</div>
              <div class="oee-target">目标 {{ oeeData.target }}%</div>
            </div>

            <!-- 右侧：三个子指标 + 进度条 -->
            <div class="oee-sub-list">
              <div v-for="(item, idx) in subMetrics" :key="idx" class="oee-sub-item">
                <div class="oee-sub-header">
                  <span class="oee-sub-label">{{ item.label }}</span>
                  <span class="oee-sub-value">{{ item.displayValue }}</span>
                </div>
                <div class="oee-progress-track">
                  <div class="oee-progress-fill" :style="{ width: item.percent + '%', background: item.color }"></div>
                </div>
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

    <!-- 操作弹窗 -->
    <div v-if="showFilter" class="filter-overlay" @click.self="showFilter = false">
      <div class="filter-modal">
        <div class="filter-modal-header">
          <span class="filter-modal-title">更多操作</span>
          <button class="filter-modal-close" @click="showFilter = false">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="filter-modal-body">
          <div class="filter-field">
            <label class="filter-label">开始日期</label>
            <input type="date" class="filter-input" :value="startDate" @change="onStartDateChange" />
          </div>
          <div class="filter-field">
            <label class="filter-label">结束日期</label>
            <input type="date" class="filter-input" :value="endDate" @change="onEndDateChange" />
          </div>
        </div>
        <div class="filter-modal-footer">
          <button class="filter-btn-primary" @click="showFilter = false">确认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '../../api/trace-app'
import { useDashboardWebSocket } from '../../composables/useDashboardWebSocket'

const emit = defineEmits<{ (e: 'exit'): void }>()

const pageTitle = ref('智能生产看板')

// ========== WebSocket OEE 数据 ==========
const { oeeData, connected, connect, disconnect, setQueryDate } = useDashboardWebSocket()

// ========== 日期选择 ==========
const showFilter = ref(false)
const today = new Date().toISOString().slice(0, 10)
const startDate = ref(today)
const endDate = ref(today)

function onStartDateChange(e: Event) {
  const target = e.target as HTMLInputElement
  startDate.value = target.value
  setQueryDate(startDate.value, endDate.value)
}

function onEndDateChange(e: Event) {
  const target = e.target as HTMLInputElement
  endDate.value = target.value
  setQueryDate(startDate.value, endDate.value)
}

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
  connect()
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
  disconnect()
})

// ========== OEE 子指标 ==========
const subMetrics = computed(() => {
  const o = oeeData.value
  return [
    {
      label: '时间开动率',
      displayValue: typeof o.availability == 'number' ? o.availability.toFixed(1) + '%' : o.availability,
      percent: typeof o.availability == 'number' ? Math.min(o.availability, 100) : 0,
      color: '#25EFBD',
    },
    {
      label: '性能开动率',
      displayValue: typeof o.performance == 'number' ? o.performance.toFixed(1) + '%' : o.performance,
      percent: typeof o.performance == 'number' ? Math.min(o.performance, 100) : 0,
      color: '#FE8C45',
    },
    {
      label: '合格率',
      displayValue: typeof o.quality == 'number' ? o.quality.toFixed(1) + '%' : o.quality,
      percent: typeof o.quality == 'number' ? Math.min(o.quality, 100) : 0,
      color: '#EF5454',
    },
  ]
})

/** OEE 百分比 */
const oeePercent = computed(() => {
  const v = oeeData.value.oee
  if (typeof v == 'number') return Math.min(v, 100)
  return 0
})

/** 仪表盘弧线偏移（半圆弧长 π × 80 ≈ 251 + 线帽修正） */
const gaugeOffset = computed(() => {
  const c = 264
  return c - (c * oeePercent.value) / 100
})

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

// ========== 设备数据 ==========
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

/* ========== 顶栏 ========== */
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

.filter-btn {
  @apply flex items-center gap-1.5 ml-3 px-3 py-1.5 rounded-full text-xs transition-all duration-200;
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.15);
  color: rgba(148, 184, 255, 0.8);
}

.filter-btn:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.25);
  color: #93c5fd;
}

/* ========== 时间筛选弹窗 ========== */
.filter-overlay {
  @apply fixed inset-0 z-[10000] flex items-center justify-center;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.filter-modal {
  @apply rounded-xl;
  width: 320px;
  background: linear-gradient(135deg, #1a2d4a, #0f1f3d);
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.filter-modal-header {
  @apply flex items-center justify-between;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

.filter-modal-title {
  font-size: 14px;
  font-weight: 600;
  color: #f0f4ff;
}

.filter-modal-close {
  @apply flex items-center justify-center rounded-full transition-colors;
  width: 28px;
  height: 28px;
  color: rgba(148, 184, 255, 0.5);
}

.filter-modal-close:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

.filter-modal-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-field {
  @apply flex flex-col gap-1.5;
}

.filter-label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(148, 184, 255, 0.6);
}

.filter-input {
  width: 100%;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid rgba(59, 130, 246, 0.15);
  background: rgba(59, 130, 246, 0.06);
  color: #93c5fd;
  font-size: 13px;
  font-family: monospace;
  outline: none;
}

.filter-input:focus {
  border-color: rgba(59, 130, 246, 0.4);
}

.filter-input::-webkit-calendar-picker-indicator {
  filter: invert(0.7) sepia(1) hue-rotate(190deg);
  cursor: pointer;
}

.filter-modal-footer {
  padding: 10px 16px 14px;
  display: flex;
  justify-content: flex-end;
}

.filter-btn-primary {
  padding: 6px 20px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #fff;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s;
}

.filter-btn-primary:hover {
  opacity: 0.9;
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

/* ========== 主体 ========== */
.dashboard-main {
  @apply relative z-10 flex flex-col flex-1 min-h-0;
  gap: 12px;
  padding-top: 12px;
  padding-bottom: 12px;
}

/* ========== 图表行 ========== */
.charts-row {
  @apply grid grid-cols-4 gap-3 flex-1 min-h-0;
}

.chart-card {
  @apply rounded-xl p-4 flex flex-col;
  background: linear-gradient(135deg, rgba(30, 58, 95, 0.4), rgba(15, 31, 61, 0.2));
  border: 1px solid rgba(59, 130, 246, 0.12);
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

/* ========== OEE 面板 ========== */
.oee-body {
  @apply flex flex-1 items-center gap-4;
  padding: 0 4px;
  min-height: 0;
}

.oee-gauge-area {
  @apply relative flex flex-col items-center shrink-0;
  width: 160px;
}

.oee-gauge-svg {
  width: 140px;
  height: 77px;
  overflow: visible;
}

.oee-gauge-track {
  stroke: rgba(59, 130, 246, 0.08);
}

.oee-gauge-fill {
  stroke: #60a5fa;
  transition: stroke-dashoffset 1s ease;
}

.oee-gauge-value {
  margin-top: 0;
  line-height: 1;
}

.oee-gauge-num {
  font-size: 20px;
  font-weight: 700;
  color: #f0f4ff;
  font-variant-numeric: tabular-nums;
}

.oee-gauge-label {
  font-size: 10px;
  font-weight: 600;
  color: rgba(148, 184, 255, 0.45);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 1px;
}

.oee-target {
  font-size: 10px;
  color: rgba(148, 184, 255, 0.3);
  margin-top: 1px;
}

.oee-sub-list {
  @apply flex-1 grid gap-2;
  grid-template-rows: 1fr 1fr 1fr;
}

.oee-sub-item {
  @apply flex flex-col justify-center;
}

.oee-sub-header {
  @apply flex items-center justify-between mb-0.5;
}

.oee-sub-label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(200, 218, 255, 0.75);
}

.oee-sub-value {
  font-size: 15px;
  font-weight: 700;
  color: #f0f4ff;
  font-variant-numeric: tabular-nums;
}

.oee-progress-track {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
  background: rgba(59, 130, 246, 0.08);
}

.oee-progress-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 1s ease;
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

/* ========== 全局禁止选中 ========== */
.dashboard-container * {
  user-select: none;
  -webkit-user-select: none;
}
</style>
