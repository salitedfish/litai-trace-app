<template>
  <div class="tech-panel trend-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
        </svg>
        近7日产量趋势
      </h3>
      <span class="tech-badge">周同比 +8.3%</span>
    </div>

    <div class="chart-body fill">
      <div class="bar-chart">
        <div
          class="bar-group"
          v-for="(bar, idx) in productionData"
          :key="idx"
          :style="{ animationDelay: `${idx * 0.08}s` }"
        >
          <span class="bar-value" :class="{ 'bar-value-peak': bar.value == maxValue }">{{ bar.value }}</span>
          <div class="bar-container">
            <div class="bar-fill" :class="{ 'bar-fill-peak': bar.value == maxValue }" :style="{ height: bar.percent + '%', '--bar-delay': `${idx * 0.3}s` }">
              <div class="bar-glow"></div>
            </div>
          </div>
          <span class="bar-label">{{ bar.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// 近7日产量（当前为演示数据，后续接真实接口）
const productionData = [
  { label: '07/21', value: 1680, percent: 72 },
  { label: '07/22', value: 1520, percent: 65 },
  { label: '07/23', value: 1850, percent: 79 },
  { label: '07/24', value: 1720, percent: 74 },
  { label: '07/25', value: 1980, percent: 85 },
  { label: '07/26', value: 2100, percent: 90 },
  { label: '07/27', value: 2050, percent: 88 },
]

// 峰值（最高产量日）高亮
const maxValue = computed(() => Math.max(...productionData.map(d => d.value)))
</script>

<style scoped>
.trend-panel {
  @apply p-4 flex flex-col;
  min-height: 0;
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
  position: relative;
  padding-top: 4px;
  border-bottom: 1px solid rgba(56, 189, 248, 0.2);
  /* 水平网格线（三等分，repeat 纵向铺开） */
  background-image:
    linear-gradient(rgba(56, 189, 248, 0.06) 1px, transparent 1px);
  background-size: 100% 33.333%;
}

.bar-group {
  @apply flex flex-col items-center flex-1 gap-0.5 h-full;
  min-width: 0;
  animation: barRise 0.8s ease-out both;
}

@keyframes barRise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.bar-container {
  @apply w-full rounded-t-sm relative;
  flex: 1;
  background: rgba(59, 130, 246, 0.07);
  min-height: 4px;
  align-self: flex-end;
}

.bar-fill {
  @apply w-full rounded-t-sm absolute bottom-0 left-0 transition-all duration-1000;
  background: linear-gradient(180deg, #7dd3fc 0%, #38bdf8 45%, #2563eb 100%);
  box-shadow: 0 0 14px rgba(59, 130, 246, 0.35);
  animation: barFill 1s ease-out both;
  overflow: hidden;
}

@keyframes barFill {
  from { height: 0 !important; }
}

/* 柱体流光 */
.bar-fill::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: -60%;
  width: 50%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.35), transparent);
  animation: techShimmer 3s ease-in-out infinite;
  animation-delay: var(--bar-delay);
}

/* 柱顶发光帽 */
.bar-glow {
  @apply absolute top-0 left-0 right-0 rounded-full;
  height: 2px;
  background: rgba(255, 255, 255, 0.75);
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.6);
}

/* 峰值日高亮 */
.bar-fill-peak {
  background: linear-gradient(180deg, #a5f3fc 0%, #22d3ee 45%, #0891b2 100%);
  box-shadow: 0 0 22px rgba(34, 211, 238, 0.55);
}

.bar-value {
  @apply text-xs font-semibold;
  color: rgba(200, 218, 255, 0.9);
  font-family: 'Consolas', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

.bar-value-peak {
  color: #67e8f9;
  text-shadow: 0 0 10px rgba(34, 211, 238, 0.6);
}

.bar-label {
  @apply text-[10px];
  color: rgba(148, 184, 255, 0.5);
  font-family: 'Consolas', 'Courier New', monospace;
}
</style>
