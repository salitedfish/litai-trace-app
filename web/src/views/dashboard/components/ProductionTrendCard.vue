<template>
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
</template>

<script setup lang="ts">
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
</style>
