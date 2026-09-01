<template>
  <div class="tech-panel hourly-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
        </svg>
        小时产量统计
      </h3>
      <div class="header-right-group">
        <!-- 产品型号过滤（放在"实时"左侧，同一行） -->
        <span
          class="product-type-tag"
          :title="'产品型号：' + (productTypes.length ? productTypes.join('、') : '全部')"
        >
          产品型号：{{ productTypes.length ? productTypes.join('、') : '全部' }}
        </span>
        <span class="tech-badge" :class="connected ? 'live' : 'offline'">
          <span class="tech-dot"></span>
          {{ connected ? '实时' : '断开' }}
        </span>
      </div>
    </div>

    <div v-if="bars.length == 0" class="tech-placeholder">
      <span class="placeholder-blink">▮</span>&nbsp;暂无报工数据
    </div>
    <div v-else class="chart-body fill">
      <div class="bar-chart tech-scroll">
        <div
          v-for="(bar, idx) in bars"
          :key="idx"
          class="bar-group"
          :style="{ animationDelay: `${idx * 0.05}s`, '--bar-delay': `${idx * 0.3}s` }"
          :title="`${bar.hour}时 · ${bar.count}件`"
        >
          <span class="bar-value">{{ bar.count }}</span>
          <div class="bar-container">
            <div class="bar-fill" :style="{ height: bar.percent + '%' }">
              <div class="bar-glow"></div>
            </div>
          </div>
          <span class="bar-label">{{ bar.hour.slice(5) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue'
import { useHourlyOutput } from '../../../composables/useHourlyOutput'

// ========== WebSocket 小时产量（组件自管理，父组件配置就绪后 start 启动） ==========
const {
  hourlyOutput,
  connected,
  connect,
  disconnect,
  setQueryDate,
  setProductType: setProductTypeFilter,
} = useHourlyOutput()

// 当前生效的产品型号过滤（用于头部展示；空数组表示全部产品）
const productTypes = ref<string[]>([])

onUnmounted(() => {
  disconnect()
})

/** 供父组件（DashboardView）从看板配置读取日期后设置查询区间 */
function setDate(dateStart: string, dateEnd: string) {
  setQueryDate(dateStart, dateEnd)
}

/** 供父组件（DashboardView）从看板配置读取产品型号后设置过滤条件 */
function setProductType(types: string[]) {
  setProductTypeFilter(types)
  productTypes.value = Array.isArray(types) ? types.slice() : []
}

/** 供父组件在配置就绪后启动 WebSocket（避免先按默认条件查一波再按配置改查） */
function start() {
  connect()
}

defineExpose({ setDate, setProductType, start })

// 柱状图数据：按数量归一化为高度百分比（峰值最高）
const bars = computed(() => {
  const list = hourlyOutput.value
  const max = Math.max(...list.map(d => d.count), 1)
  return list.map(d => ({
    hour: d.hour,
    count: d.count,
    percent: Math.round((d.count / max) * 100),
  }))
})
</script>

<style scoped>
.hourly-panel {
  @apply p-4 flex flex-col;
  min-height: 0;
}

/* 头部右侧：产品型号 + 实时徽标（同一行） */
.header-right-group {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

/* 产品型号标签（选中多个时省略号截断，悬停看全量） */
.product-type-tag {
  display: inline-flex;
  align-items: center;
  max-width: 220px;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 11px;
  letter-spacing: 0.06em;
  color: rgba(148, 184, 255, 0.85);
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.22);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chart-body {
  @apply w-full;
}

.chart-body.fill {
  @apply flex-1 min-h-0;
}

/* ========== 小时柱状图 ========== */
.bar-chart {
  @apply flex items-end gap-1 h-full;
  position: relative;
  padding-top: 4px;
  overflow-x: auto;
  overflow-y: hidden;
  border-bottom: 1px solid rgba(56, 189, 248, 0.2);
  /* 水平网格线（四等分，repeat 纵向铺开） */
  background-image:
    linear-gradient(rgba(56, 189, 248, 0.06) 1px, transparent 1px);
  background-size: 100% 25%;
}

.bar-group {
  @apply flex flex-col items-center gap-0.5 h-full;
  flex: 1 1 0%;
  min-width: 44px;
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
  @apply w-full rounded-t-sm absolute bottom-0 left-0;
  background: linear-gradient(180deg, #7dd3fc 0%, #38bdf8 45%, #2563eb 100%);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
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
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
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

.bar-value {
  @apply text-[9px] font-semibold;
  color: rgba(200, 218, 255, 0.9);
  font-family: 'Consolas', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-label {
  @apply text-[9px];
  color: rgba(148, 184, 255, 0.5);
  font-family: 'Consolas', 'Courier New', monospace;
  white-space: nowrap;
}
</style>
