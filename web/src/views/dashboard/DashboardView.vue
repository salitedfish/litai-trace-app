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
    <HeaderBar :title="pageTitle" @open-filter="showFilter = true" @exit="emit('exit')" />

    <!-- 主体 -->
    <main class="dashboard-main">
      <!-- 图表行 1：OEE / 产线设备 / 产量趋势 -->
      <section class="charts-row">
        <OeeCard ref="oeeCardRef" />
        <DeviceStatusCard class="col-span-2" :line-code="selectedLine" />
        <ProductionTrendCard />
      </section>

      <!-- 图表行 2：全部预留 -->
      <section class="charts-row">
        <div class="chart-card chart-card-placeholder col-span-4">
          <span class="placeholder-text">预留区域</span>
        </div>
      </section>
    </main>

    <!-- 底部装饰线 -->
    <div class="footer-line"></div>

    <!-- 操作弹窗 -->
    <FilterModal
      :show="showFilter"
      :start-date="startDate"
      :end-date="endDate"
      :selected-line="selectedLine"
      @close="showFilter = false"
      @start-date-change="onStartDateChange"
      @end-date-change="onEndDateChange"
      @line-change="onLineChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/trace-app'
import HeaderBar from './components/HeaderBar.vue'
import OeeCard from './components/OeeCard.vue'
import DeviceStatusCard from './components/DeviceStatusCard.vue'
import ProductionTrendCard from './components/ProductionTrendCard.vue'
import FilterModal from './components/FilterModal.vue'

const emit = defineEmits<{ (e: 'exit'): void }>()

const pageTitle = ref('智能生产看板')

// ========== 更多操作弹窗（日期 / 产线选择） ==========
const showFilter = ref(false)
const today = new Date().toISOString().slice(0, 10)
const startDate = ref(today)
const endDate = ref(today)
const selectedLine = ref('')

const oeeCardRef = ref<InstanceType<typeof OeeCard>>()

function onStartDateChange(value: string) {
  startDate.value = value
  oeeCardRef.value?.setDate(startDate.value, endDate.value)
}

function onEndDateChange(value: string) {
  endDate.value = value
  oeeCardRef.value?.setDate(startDate.value, endDate.value)
}

function onLineChange(value: string) {
  selectedLine.value = value
}

onMounted(async () => {
  try {
    const res = await api.getDashboardConfig()
    if (res.data?.title) {
      pageTitle.value = res.data.title
    }
  } catch (_) {
    // 使用默认标题
  }
})
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
