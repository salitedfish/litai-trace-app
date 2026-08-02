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
        <DashboardClock />
      </div>
    </header>

    <!-- 主体 -->
    <main class="dashboard-main">
      <!-- 图表行 -->
      <section class="charts-row">
        <!-- 设备 OEE -->
        <div class="chart-card">
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

        <!-- 预留空间：工艺路线工序设备展示 -->
        <div class="chart-card chart-card-placeholder col-span-2">
          <div v-if="!selectedRouting" class="placeholder-text">预留区域</div>
          <div v-else-if="routingProcessesLoading" class="placeholder-text">加载中...</div>
          <div v-else-if="routingProcessesError" class="placeholder-text">{{ routingProcessesError }}</div>
          <div v-else-if="routingProcesses.length == 0" class="placeholder-text">该工艺路线暂无工序数据</div>
          <div v-else class="processes-wrap">
            <div class="processes-title">{{ routingProcessesTitle }}</div>
            <div class="devices-grid">
              <div v-for="dev in allDevices" :key="dev.device_code" class="device-tile" :title="dev.process_name + ' · ' + dev.device_code">
                <img :src="deviceIcon(dev.device_type, dev.status)" class="device-tile-icon" />
                <span class="device-tile-name">{{ dev.device_name }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 近7日产量趋势 -->
        <div class="chart-card">
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
      </section>

      <!-- 下部分：全部预留 -->
      <section class="charts-row">
        <div class="chart-card chart-card-placeholder col-span-4">
          <span class="placeholder-text">预留区域</span>
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
          <div class="filter-field">
            <label class="filter-label">工艺路线</label>
            <DarkSelect
              v-model="selectedRouting"
              :options="routingOptions"
              :disabled="routingLoading"
              placeholder="请选择工艺路线"
              searchable
            />
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import api from '../../api/trace-app'
import { useDashboardWebSocket } from '../../composables/useDashboardWebSocket'
import { useDeviceStatus, STATUS_NAMES } from '../../composables/useDeviceStatus'
import DarkSelect from '../../components/DarkSelect.vue'
import DashboardClock from './DashboardClock.vue'
import deviceDetectOff from '../../assets/device_status/检测(关机).png'
import deviceDetectStandby from '../../assets/device_status/检测(待机).png'
import deviceDetectFault from '../../assets/device_status/检测(故障).png'
import deviceDetectRunning from '../../assets/device_status/检测(运行).png'
import deviceNonDetectOff from '../../assets/device_status/非检测(关机).png'
import deviceNonDetectStandby from '../../assets/device_status/非检测(待机).png'
import deviceNonDetectFault from '../../assets/device_status/非检测(故障).png'
import deviceNonDetectRunning from '../../assets/device_status/非检测(运行).png'

const emit = defineEmits<{ (e: 'exit'): void }>()

const pageTitle = ref('智能生产看板')

// ========== WebSocket OEE 数据 ==========
const { oeeData, connected, connect, disconnect, setQueryDate } = useDashboardWebSocket()

// ========== WebSocket 设备状态 ==========
const { connect: connectDeviceStatus, disconnect: disconnectDeviceStatus, statusOf } = useDeviceStatus()

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

// ========== 工艺路线下拉 ==========
const routingList = ref<{ routing_code: string, routing_name: string, routing_type: string, workshop_code: string, workshop_name: string }[]>([])
const selectedRouting = ref('')
const routingLoading = ref(false)

const routingOptions = computed(() => {
  return routingList.value.map(item => ({ label: item.routing_name, value: item.routing_code }))
})

const loadRoutingList = async () => {
  routingLoading.value = true
  try {
    const res = await api.queryRoutingList()
    routingList.value = res.data || []
  } catch (err: any) {
    console.error('加载工艺路线列表失败:', err)
  } finally {
    routingLoading.value = false
  }
}

// ========== 工艺路线工序设备展示 ==========
interface RoutingProcess {
  process_code: string
  process_name: string
  process_order: number
  produce_unit_code: string
  produce_unit_name: string
  devices: { device_code: string, device_name: string, device_type: string, status?: string }[]
}

// 设备类型（检测/非检测）× 状态（关机/待机/故障/运行）→ 图标
const deviceIcon = (deviceType: string, status: string) => {
  const detect = deviceType == '检测'
  if (status == '运行') return detect ? deviceDetectRunning : deviceNonDetectRunning
  if (status == '待机') return detect ? deviceDetectStandby : deviceNonDetectStandby
  if (status == '故障') return detect ? deviceDetectFault : deviceNonDetectFault
  return detect ? deviceDetectOff : deviceNonDetectOff
}

const routingProcessesTitle = ref('')
const routingProcesses = ref<RoutingProcess[]>([])
const routingProcessesLoading = ref(false)
const routingProcessesError = ref('')

const loadRoutingProcesses = async () => {
  if (!selectedRouting.value) {
    routingProcessesTitle.value = ''
    routingProcesses.value = []
    routingProcessesError.value = ''
    return
  }
  routingProcessesLoading.value = true
  routingProcessesError.value = ''
  try {
    const res = await api.queryRoutingProcesses(selectedRouting.value)
    routingProcessesTitle.value = res.data?.routing_name || ''
    routingProcesses.value = res.data?.processes || []
  } catch (err: any) {
    console.error('加载工艺路线工序失败:', err)
    routingProcessesError.value = '工序数据加载失败'
  } finally {
    routingProcessesLoading.value = false
  }
}

// 切换工艺路线后重新加载工序设备
watch(selectedRouting, () => {
  loadRoutingProcesses()
})

// 按工序顺序拍平所有设备，横向排列自动换行；状态取自 WebSocket 推送的实时状态，取不到默认关机
const allDevices = computed(() => {
  const result: { device_code: string, device_name: string, device_type: string, status: string, process_name: string }[] = []
  for (const p of routingProcesses.value) {
    for (const dev of p.devices) {
      result.push({ ...dev, status: STATUS_NAMES[statusOf(dev.device_code)] || '关机', process_name: p.process_name })
    }
  }
  return result
})

onMounted(async () => {
  connect()
  connectDeviceStatus()
  loadRoutingList()
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
  disconnect()
  disconnectDeviceStatus()
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
  background: rgba(0, 0, 0, 0.6);
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

/* ========== 预留区域 ========== */
.chart-card-placeholder {
  border-style: dashed;
  border-color: rgba(59, 130, 246, 0.15);
}

.placeholder-text {
  @apply flex-1 flex items-center justify-center;
  font-size: 13px;
  letter-spacing: 0.2em;
  color: rgba(148, 184, 255, 0.3);
}

/* ========== 工序设备展示 ========== */
.processes-wrap {
  @apply flex-1 flex flex-col min-h-0;
}

.processes-title {
  @apply shrink-0 mb-2;
  font-size: 13px;
  font-weight: 600;
  color: rgba(200, 218, 255, 0.9);
}

.devices-grid {
  @apply flex-1 overflow-y-auto;
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  gap: 8px;
}

.devices-grid::-webkit-scrollbar {
  width: 4px;
}

.devices-grid::-webkit-scrollbar-track {
  background: transparent;
}

.devices-grid::-webkit-scrollbar-thumb {
  background-color: rgba(59, 130, 246, 0.3);
  border-radius: 20px;
}

.device-tile {
  @apply flex flex-col items-center gap-1 rounded-lg px-2 py-2;
  width: 84px;
  background: rgba(59, 130, 246, 0.06);
  border: 1px solid rgba(59, 130, 246, 0.12);
}

.device-tile-icon {
  width: 44px;
  height: 44px;
  object-fit: contain;
}

.device-tile-name {
  @apply text-center truncate;
  width: 100%;
  font-size: 10px;
  color: rgba(200, 218, 255, 0.85);
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
