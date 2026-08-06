<template>
  <div class="dashboard-container">
    <!-- 背景装饰 -->
    <div class="bg-decorations">
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
      <div class="bg-orb bg-orb-3"></div>
      <div class="grid-lines"></div>
      <div class="bg-vignette"></div>
      <div class="bg-scanline"></div>
    </div>

    <!-- 系统标识 -->
    <div class="sys-tag">
      <span class="sys-tag-line"></span>
      <span class="sys-tag-text">MES·TRACE / SYS ONLINE</span>
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
        <div class="tech-panel chart-card-placeholder col-span-4">
          <span class="placeholder-text">
            <span class="placeholder-blink">▮</span>
            预留区域
          </span>
        </div>
      </section>
    </main>

    <!-- 底部数据流装饰线 -->
    <div class="footer-flow"></div>

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
import './dashboard.theme.css'

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
  background: radial-gradient(120% 90% at 50% 0%, #10224a 0%, #0a1833 45%, #050e22 100%);
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
  width: 420px;
  height: 420px;
  background: radial-gradient(circle, #3b82f6, transparent 65%);
  top: -160px;
  right: -100px;
  animation: techFloat 20s ease-in-out infinite;
}

.bg-orb-2 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #06b6d4, transparent 65%);
  bottom: -90px;
  left: -90px;
  animation: techFloat 25s ease-in-out infinite reverse;
}

.bg-orb-3 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, #6366f1, transparent 65%);
  top: 50%;
  left: 58%;
  animation: techFloat 30s ease-in-out infinite 5s;
}

.grid-lines {
  @apply absolute inset-0;
  background-image:
    linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px);
  background-size: 56px 56px;
  opacity: 0.6;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 45%, black 30%, transparent 85%);
  -webkit-mask-image: radial-gradient(ellipse 80% 80% at 50% 45%, black 30%, transparent 85%);
}

/* 暗角，聚焦中央内容 */
.bg-vignette {
  @apply absolute inset-0;
  background: radial-gradient(ellipse 90% 80% at 50% 40%, transparent 45%, rgba(2, 8, 23, 0.55) 100%);
}

/* 自上而下往复的扫描光带 */
.bg-scanline {
  @apply absolute left-0 right-0;
  top: -160px;
  height: 160px;
  background: linear-gradient(180deg, transparent, rgba(56, 189, 248, 0.07) 60%, transparent);
  animation: scanSweep 8s linear infinite;
}

@keyframes scanSweep {
  0% { transform: translateY(0); }
  100% { transform: translateY(calc(100vh + 160px)); }
}

/* ========== 系统标识 ========== */
.sys-tag {
  position: absolute;
  left: 22px;
  bottom: 18px;
  z-index: 5;
  display: flex;
  align-items: center;
  gap: 8px;
  pointer-events: none;
}

.sys-tag-line {
  width: 22px;
  height: 1px;
  background: linear-gradient(90deg, rgba(56, 189, 248, 0.8), transparent);
}

.sys-tag-text {
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 9px;
  letter-spacing: 0.24em;
  color: rgba(148, 184, 255, 0.4);
}

/* ========== 主体 ========== */
.dashboard-main {
  @apply relative z-10 flex flex-col flex-1 min-h-0;
  gap: 12px;
  padding-top: 12px;
  padding-bottom: 14px;
}

/* ========== 图表行 ========== */
.charts-row {
  @apply grid grid-cols-4 gap-3 flex-1 min-h-0;
}

/* ========== 预留区域 ========== */
.chart-card-placeholder {
  border-style: dashed;
  border-color: rgba(56, 189, 248, 0.18);
}

.placeholder-text {
  @apply flex-1 flex items-center justify-center;
  font-size: 13px;
  letter-spacing: 0.3em;
  color: rgba(148, 184, 255, 0.3);
  gap: 6px;
}

.placeholder-blink {
  color: #38bdf8;
  animation: techPulse 1.2s ease-in-out infinite;
}

/* ========== 底部数据流装饰线 ========== */
.footer-flow {
  @apply relative z-10 shrink-0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.22) 15%, rgba(56, 189, 248, 0.22) 85%, transparent);
}

.footer-flow::after {
  content: '';
  position: absolute;
  top: -1px;
  left: -70px;
  width: 70px;
  height: 4px;
  background: linear-gradient(90deg, transparent, #38bdf8, transparent);
  filter: blur(0.5px);
  animation: flowMove 3.6s linear infinite;
}

@keyframes flowMove {
  0% { left: -70px; }
  100% { left: 100%; }
}

/* ========== 全局禁止选中 ========== */
.dashboard-container * {
  user-select: none;
  -webkit-user-select: none;
}
</style>
