<template>
  <div class="tech-panel qualified-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.6-2.6A9 9 0 1111 3a9 9 0 016.6 3.4z" />
        </svg>
        工序合格率
      </h3>
      <span class="tech-badge" :class="connected ? 'live' : 'offline'">
        <span class="tech-dot"></span>
        {{ connected ? '实时' : '断开' }}
      </span>
    </div>

    <div v-if="items.length == 0" class="tech-placeholder">
      <span class="placeholder-blink">▮</span>&nbsp;暂无报工数据
    </div>
    <div v-else class="quality-list tech-scroll">
      <div v-for="item in items" :key="item.procedure_code" class="quality-row">
        <div class="quality-top">
          <span class="quality-name" :title="item.procedure_code">{{ item.procedure_name }}</span>
          <span class="quality-rate" :class="rateClass(item.quality_rate)">
            {{ item.quality_rate.toFixed(1) }}%
          </span>
        </div>
        <div class="quality-bar-track">
          <div class="quality-bar-fill" :class="barClass(item.quality_rate)" :style="{ width: barWidth(item.quality_rate) }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onUnmounted } from 'vue'
import { useProcessQuality } from '../../../composables/useProcessQuality'

// ========== WebSocket 工序合格率（组件自管理，父组件配置就绪后 start 启动） ==========
const { processQuality, connected, connect, disconnect, setQueryDate } = useProcessQuality()

onUnmounted(() => {
  disconnect()
})

/** 供父组件（DashboardView）从看板配置读取日期后设置查询区间 */
function setDate(dateStart: string, dateEnd: string) {
  setQueryDate(dateStart, dateEnd)
}

/** 供父组件在配置就绪后启动 WebSocket（避免先按默认条件查一波再按配置改查） */
function start() {
  connect()
}

defineExpose({ setDate, start })

// 工序合格率列表
const items = computed(() => processQuality.value)

/** 合格率数字颜色：低于 90% 红色，大于等于 90% 绿色 */
function rateClass(rate: number): string {
  return rate < 90 ? 'rate-low' : 'rate-good'
}

/** 进度条颜色：>=90% 绿 / 80~90% 黄 / <80% 红 */
function barClass(rate: number): string {
  if (rate >= 90) return 'bar-good'
  if (rate >= 80) return 'bar-warn'
  return 'bar-low'
}

/** 进度条宽度（封顶 100%） */
function barWidth(rate: number): string {
  return Math.min(rate, 100) + '%'
}
</script>

<style scoped>
.qualified-panel {
  @apply p-4 flex flex-col;
  min-height: 0;
}

/* ========== 工序合格率列表 ========== */
.quality-list {
  @apply flex-1 min-h-0 overflow-y-auto flex flex-col gap-1.5;
}

.quality-row {
  @apply flex flex-col gap-1 rounded px-2 py-1.5;
  background: rgba(59, 130, 246, 0.06);
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.quality-top {
  @apply flex items-center justify-between gap-2;
}

.quality-name {
  font-size: 11px;
  color: rgba(200, 218, 255, 0.85);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.quality-rate {
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 14px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

.rate-good {
  color: #34d399;
  text-shadow: 0 0 8px rgba(52, 211, 153, 0.4);
}

.rate-low {
  color: #f87171;
  text-shadow: 0 0 8px rgba(248, 113, 113, 0.4);
}

/* ========== 合格率进度条 ========== */
.quality-bar-track {
  position: relative;
  width: 100%;
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
  background: rgba(59, 130, 246, 0.12);
}

.quality-bar-fill {
  position: relative;
  height: 100%;
  border-radius: 2px;
  transition: width 0.8s ease;
  overflow: hidden;
}

/* 进度条流光（同 OEE 进度条） */
.quality-bar-fill::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: -50%;
  width: 45%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.45), transparent);
  animation: barShimmer 2.6s ease-in-out infinite;
}

@keyframes barShimmer {
  0% { transform: translateX(0); }
  100% { transform: translateX(420%); }
}

.bar-good {
  background: #34d399;
  box-shadow: 0 0 6px rgba(52, 211, 153, 0.5);
}

.bar-warn {
  background: #fbbf24;
  box-shadow: 0 0 6px rgba(251, 191, 36, 0.5);
}

.bar-low {
  background: #f87171;
  box-shadow: 0 0 6px rgba(248, 113, 113, 0.5);
}
</style>
