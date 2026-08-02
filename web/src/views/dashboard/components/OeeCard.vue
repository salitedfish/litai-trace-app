<template>
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
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useDashboardWebSocket } from '../../../composables/useDashboardWebSocket'

// ========== WebSocket OEE 数据（组件自管理） ==========
const { oeeData, connected, connect, disconnect, setQueryDate } = useDashboardWebSocket()

onMounted(() => {
  connect()
})

onUnmounted(() => {
  disconnect()
})

/** 供父组件（更多操作弹窗）设置查询日期 */
function setDate(dateStart: string, dateEnd: string) {
  setQueryDate(dateStart, dateEnd)
}

defineExpose({ setDate })

// OEE 子指标
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
</script>

<style scoped>
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
</style>
