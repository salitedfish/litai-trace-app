<template>
  <div class="tech-panel plan-actual-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3v18h18M7 15l4-4 4 3 5-6" />
        </svg>
        计划/实际产量
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

    <div v-if="!connected && planData.plan_count == 0 && planData.actual_count == 0" class="tech-placeholder">
      <span class="placeholder-blink">▮</span>&nbsp;暂无产量数据
    </div>
    <div v-else class="plan-actual-body">
      <!-- 计划产量 -->
      <div class="pa-card" style="--pa-color: #00FFDF; --pa-rgb: 0, 255, 223">
        <div class="pa-icon">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div class="pa-main">
          <span class="pa-label" :title="labelPlan">{{ labelPlan }}</span>
          <span class="pa-value"><em class="pa-unit">计</em>{{ planData.plan_count }}<i class="pa-unit-suffix">件</i></span>
        </div>
      </div>

      <!-- 实际产量 -->
      <div class="pa-card" style="--pa-color: #2E90FD; --pa-rgb: 46, 144, 253">
        <div class="pa-icon">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.27 6.96L12 12.01l8.73-5.05M12 22.08V12" />
          </svg>
        </div>
        <div class="pa-main">
          <span class="pa-label" :title="labelActual">{{ labelActual }}</span>
          <span class="pa-value"><em class="pa-unit">实</em>{{ planData.actual_count }}<i class="pa-unit-suffix">件</i></span>
        </div>
      </div>

      <!-- 产量进度 -->
      <div class="pa-card" style="--pa-color: #22d3ee; --pa-rgb: 34, 211, 238">
        <div class="pa-icon">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M23 6l-9.5 9.5-5-5L1 18" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 6h6v6" />
          </svg>
        </div>
        <div class="pa-main">
          <span class="pa-label" :title="labelProgress">{{ labelProgress }}</span>
          <span class="pa-value">{{ planData.progress.toFixed(1) }}<em class="pa-pct">%</em></span>
          <div class="pa-progress-track">
            <div
              class="pa-progress-fill"
              :style="{ width: Math.min(planData.progress, 100) + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { usePlanActualOutput } from '../../../composables/usePlanActualOutput'

// ========== WebSocket 计划/实际产量（组件自管理） ==========
const {
  planActual,
  connected,
  connect,
  disconnect,
  setQueryDate,
  setProductType: setProductTypeFilter,
} = usePlanActualOutput()

// 当前生效的产品型号过滤（用于头部展示；空数组表示全部产品）
const productTypes = ref<string[]>([])

// 当前查询日期区间（setDate 传入；为空表示未配置，默认当天）
const queryStart = ref('')
const queryEnd = ref('')

onMounted(() => {
  connect()
})

onUnmounted(() => {
  disconnect()
})

/** 供父组件（DashboardView）从看板配置读取日期后设置查询区间 */
function setDate(dateStart: string, dateEnd: string) {
  setQueryDate(dateStart, dateEnd)
  queryStart.value = dateStart || ''
  queryEnd.value = dateEnd || ''
}

/** 供父组件（DashboardView）从看板配置读取产品型号后设置过滤条件 */
function setProductType(types: string[]) {
  setProductTypeFilter(types)
  productTypes.value = Array.isArray(types) ? types.slice() : []
}

defineExpose({ setDate, setProductType })

/** 三块统计展示数据 */
const planData = computed(() => ({
  plan_count: planActual.value.plan_count,
  actual_count: planActual.value.actual_count,
  progress: planActual.value.progress,
}))

/** 查询区间前缀：配置了时间范围显示"起 到 止"，否则"当日" */
const rangePrefix = computed(() => {
  if (queryStart.value && queryEnd.value) {
    return `${queryStart.value} 到 ${queryEnd.value} `
  }
  return '当日'
})

const labelPlan = computed(() => rangePrefix.value + '计划产量')
const labelActual = computed(() => rangePrefix.value + '实际产量')
const labelProgress = computed(() => rangePrefix.value + '产量进度')
</script>

<style scoped>
.plan-actual-panel {
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
  max-width: 120px;
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

/* ========== 三块 KPI 卡片 ========== */
.plan-actual-body {
  @apply flex flex-1 flex-col;
  min-height: 0;
  gap: 10px;
}

.pa-card {
  --pa-color: #38bdf8;
  @apply relative flex flex-1 items-center gap-3 rounded-lg px-3;
  min-height: 0;
  background: linear-gradient(160deg, rgba(13, 32, 71, 0.45), rgba(6, 17, 40, 0.2));
  border: 1px solid rgba(56, 189, 248, 0.12);
  box-shadow: inset 0 0 18px rgba(37, 99, 235, 0.05);
  overflow: hidden;
}

/* 卡片左侧彩色光边 */
.pa-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 20%;
  bottom: 20%;
  width: 2px;
  border-radius: 2px;
  background: var(--pa-color);
  box-shadow: 0 0 8px var(--pa-color);
}

/* 卡片顶部呼吸光条 */
.pa-card::after {
  content: '';
  position: absolute;
  left: 8px;
  right: 8px;
  top: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--pa-color), transparent);
  opacity: 0.35;
}

/* 图标发光块 */
.pa-icon {
  @apply flex items-center justify-center shrink-0 rounded-md;
  width: 34px;
  height: 34px;
  color: var(--pa-color);
  background: radial-gradient(circle at 50% 30%, rgba(255, 255, 255, 0.06), transparent 70%);
  border: 1px solid rgba(var(--pa-rgb), 0.4);
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.3), 0 0 10px rgba(var(--pa-rgb), 0.2);
}

.pa-icon svg {
  width: 18px;
  height: 18px;
  filter: drop-shadow(0 0 4px var(--pa-color));
}

/* 右侧主区 */
.pa-main {
  @apply flex flex-col justify-center;
  min-width: 0;
  flex: 1;
}

.pa-label {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.12em;
  color: rgba(200, 218, 255, 0.6);
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* 大数字 */
.pa-value {
  display: flex;
  align-items: baseline;
  font-size: 24px;
  font-weight: 700;
  line-height: 1.15;
  color: var(--pa-color);
  font-family: 'Consolas', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
  text-shadow: 0 0 14px rgba(var(--pa-rgb), 0.45);
  overflow: hidden;
  white-space: nowrap;
}

/* 计划/实际前面的小角标字 */
.pa-unit {
  font-style: normal;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: rgba(200, 218, 255, 0.5);
  margin-right: 6px;
  padding: 1px 5px;
  border: 1px solid rgba(148, 184, 255, 0.2);
  border-radius: 3px;
}

/* 数量单位 */
.pa-unit-suffix {
  font-style: normal;
  font-size: 11px;
  font-weight: 500;
  color: rgba(200, 218, 255, 0.45);
  margin-left: 4px;
}

/* 进度百分号 */
.pa-pct {
  font-style: normal;
  font-size: 13px;
  font-weight: 600;
  color: var(--pa-color);
  margin-left: 1px;
}

/* 进度条 */
.pa-progress-track {
  position: relative;
  width: 100%;
  height: 5px;
  margin-top: 6px;
  border-radius: 3px;
  overflow: hidden;
  background: rgba(59, 130, 246, 0.1);
}

.pa-progress-fill {
  position: relative;
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, var(--pa-color), rgba(var(--pa-rgb), 0.5));
  box-shadow: 0 0 8px var(--pa-color);
  transition: width 1s ease;
  overflow: hidden;
}

/* 进度条流光 */
.pa-progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: -50%;
  width: 45%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
  animation: paShimmer 2.6s ease-in-out infinite;
}

@keyframes paShimmer {
  0% { transform: translateX(0); }
  100% { transform: translateX(420%); }
}
</style>
