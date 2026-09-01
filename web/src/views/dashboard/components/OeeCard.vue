<template>
  <div class="tech-panel oee-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
        </svg>
        设备 OEE
      </h3>
      <span class="tech-badge" :class="connected ? 'live' : 'offline'">
        <span class="tech-dot"></span>
        {{ connected ? '实时' : '断开' }}
      </span>
    </div>

    <div class="chart-body fill oee-body">
      <!-- 左侧：仪表盘 -->
      <div class="oee-gauge-area">
        <svg class="oee-gauge-svg" viewBox="0 0 200 110">
          <!-- 外侧刻度环（虚线刻度） -->
          <path d="M10,95 A90,90 0 0,1 190,95" fill="none" stroke="rgba(148,184,255,0.28)" stroke-width="2" stroke-dasharray="2 11.5"/>
          <!-- 背景弧 -->
          <path d="M20,95 A80,80 0 0,1 180,95" fill="none" stroke-width="12" stroke-linecap="round" stroke="rgba(59,130,246,0.10)"/>
          <!-- 色区：红 0-30% -->
          <path d="M20,95 A80,80 0 0,1 72,33.6" fill="none" stroke-width="12" stroke-linecap="round" stroke="rgba(239,68,68,0.18)"/>
          <!-- 色区：黄 30-60% -->
          <path d="M72,33.6 A80,80 0 0,1 128,33.6" fill="none" stroke-width="12" stroke-linecap="round" stroke="rgba(245,158,11,0.18)"/>
          <!-- 色区：绿 60-100% -->
          <path d="M128,33.6 A80,80 0 0,1 180,95" fill="none" stroke-width="12" stroke-linecap="round" stroke="rgba(16,185,129,0.18)"/>
          <!-- 填充弧渐变 + 辉光 -->
          <defs>
            <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#ef4444"/>
              <stop offset="40%" stop-color="#f59e0b"/>
              <stop offset="70%" stop-color="#10b981"/>
              <stop offset="100%" stop-color="#22d3ee"/>
            </linearGradient>
            <filter id="gaugeGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="3.5" result="blur"/>
              <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          <path d="M20,95 A80,80 0 0,1 180,95" fill="none" stroke="url(#gaugeGrad)" stroke-width="12" stroke-linecap="round"
            stroke-dasharray="264" :stroke-dashoffset="gaugeOffset" filter="url(#gaugeGlow)"/>
          <!-- 弧端点刻度 -->
          <circle cx="20" cy="95" r="3" fill="rgba(148,184,255,0.35)"/>
          <circle cx="100" cy="15" r="3" fill="rgba(148,184,255,0.35)"/>
          <circle cx="180" cy="95" r="3" fill="rgba(148,184,255,0.35)"/>
          <!-- 指针光点 -->
          <circle :cx="tipPos.x" :cy="tipPos.y" r="8" fill="rgba(56,189,248,0.15)" filter="url(#gaugeGlow)"/>
          <circle :cx="tipPos.x" :cy="tipPos.y" r="3.5" fill="#38bdf8"/>
        </svg>
        <div class="oee-gauge-value">
          <span class="oee-gauge-num">{{ oeePercent.toFixed(1) }}<em>%</em></span>
        </div>
        <div class="oee-gauge-label">OEE</div>
        <div class="oee-target">目标 {{ oeeData.target }}%</div>
      </div>

      <!-- 右侧：三个子指标 + 进度条 -->
      <div class="oee-sub-list">
        <div v-for="(item, idx) in subMetrics" :key="idx" class="oee-sub-item">
          <div class="oee-sub-header">
            <span class="oee-sub-label">
              <i class="oee-sub-dot" :style="{ background: item.color, boxShadow: `0 0 6px ${item.color}` }"></i>
              {{ item.label }}
            </span>
            <span class="oee-sub-value">{{ item.displayValue }}</span>
          </div>
          <div class="oee-progress-track">
            <div class="oee-progress-fill" :style="{ width: item.percent + '%', background: item.color, boxShadow: `0 0 8px ${item.color}` }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onUnmounted } from 'vue'
import { useDashboardWebSocket } from '../../../composables/useDashboardWebSocket'

// ========== WebSocket OEE 数据（组件自管理，父组件配置就绪后 start 启动） ==========
const { oeeData, connected, connect, disconnect, setQueryDate } = useDashboardWebSocket()

onUnmounted(() => {
  disconnect()
})

/** 供父组件（更多操作弹窗）设置查询日期 */
function setDate(dateStart: string, dateEnd: string) {
  setQueryDate(dateStart, dateEnd)
}

/** 供父组件在配置就绪后启动 WebSocket（避免先按默认条件查一波再按配置改查） */
function start() {
  connect()
}

defineExpose({ setDate, start })

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

/** 指针光点位置（半圆弧上，随 OEE 转动） */
const tipPos = computed(() => {
  const a = (Math.PI * oeePercent.value) / 100
  return {
    x: 100 - 80 * Math.cos(a),
    y: 95 - 80 * Math.sin(a),
  }
})
</script>

<style scoped>
.oee-panel {
  @apply p-4 flex flex-col;
  min-height: 0;
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
  width: 168px;
}

.oee-gauge-svg {
  width: 146px;
  height: 80px;
  overflow: visible;
}

.oee-gauge-value {
  margin-top: 0;
  line-height: 1;
}

.oee-gauge-num {
  font-size: 24px;
  font-weight: 700;
  color: #f0f4ff;
  font-family: 'Consolas', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
  text-shadow: 0 0 14px rgba(56, 189, 248, 0.45);
}

.oee-gauge-num em {
  font-style: normal;
  font-size: 13px;
  font-weight: 600;
  color: #67e8f9;
  margin-left: 1px;
}

.oee-gauge-label {
  font-size: 9px;
  font-weight: 700;
  color: rgba(148, 184, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.34em;
  margin-top: 3px;
}

.oee-target {
  font-size: 10px;
  color: rgba(148, 184, 255, 0.35);
  margin-top: 2px;
  font-family: 'Consolas', 'Courier New', monospace;
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
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: rgba(200, 218, 255, 0.75);
  letter-spacing: 0.05em;
}

.oee-sub-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
}

.oee-sub-value {
  font-size: 15px;
  font-weight: 700;
  color: #f0f4ff;
  font-family: 'Consolas', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

.oee-progress-track {
  position: relative;
  width: 100%;
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
  background: rgba(59, 130, 246, 0.1);
}

.oee-progress-fill {
  position: relative;
  height: 100%;
  border-radius: 2px;
  transition: width 1s ease;
  overflow: hidden;
}

/* 进度条流光 */
.oee-progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: -50%;
  width: 45%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
  animation: oeeShimmer 2.6s ease-in-out infinite;
}

@keyframes oeeShimmer {
  0% { transform: translateX(0); }
  100% { transform: translateX(420%); }
}
</style>
