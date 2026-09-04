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
    <HeaderBar :title="pageTitle" @exit="emit('exit')" />

    <!-- 主体：两行两列均分 -->
    <main class="dashboard-main">
      <!-- 配置加载中：等配置获取完再加载看板 -->
      <div v-if="!configReady" class="board-loading">
        <div class="board-loading-spinner"></div>
        <span class="board-loading-text">正在加载看板配置...</span>
      </div>

      <!-- 第一行：OEE / 产线设备 -->
      <section v-show="configReady" class="charts-row2">
        <OeeCard ref="oeeCardRef" />
        <DeviceStatusCard ref="deviceStatusCardRef" :line-code="selectedLine" />
      </section>

      <!-- 第二行：工序加工情况 / 不合格原因占比（旧检验项不合格占比卡 UnqualifiedPieCard.vue 保留备用） -->
      <section v-show="configReady" class="charts-row2">
        <ProcessProductionCard ref="processProductionCardRef" />
        <UnqualifiedReasonPieCard ref="reasonPieCardRef" :workshop-name="workshopName" />
      </section>
    </main>

    <!-- 底部数据流装饰线 -->
    <div class="footer-flow"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/trace-app'
import HeaderBar from '../dashboard/components/HeaderBar.vue'
import OeeCard from '../dashboard/components/OeeCard.vue'
import DeviceStatusCard from '../dashboard/components/DeviceStatusCard.vue'
import ProcessProductionCard from './components/ProcessProductionCard.vue'
import UnqualifiedReasonPieCard from './components/UnqualifiedReasonPieCard.vue'
import '../dashboard/dashboard.theme.css'

const emit = defineEmits<{ (e: 'exit'): void }>()

const pageTitle = ref('智能看板2')

// ========== 看板参数（日期 / 产线 / 产品型号，来自看板2配置，加载时一并获取） ==========
const today = new Date().toISOString().slice(0, 10)
const startDate = ref(today)
const endDate = ref(today)
const selectedLine = ref('')
const productTypes = ref<string[]>([])
// 选中产线的展示名（供饼图卡头部标签，配置产线为空时保持空=全部产线）
const workshopName = ref('')
// 配置是否已获取完（在此之前显示加载中，卡片不启动）
const configReady = ref(false)

const oeeCardRef = ref<InstanceType<typeof OeeCard>>()
const deviceStatusCardRef = ref<InstanceType<typeof DeviceStatusCard>>()
const processProductionCardRef = ref<InstanceType<typeof ProcessProductionCard>>()
const reasonPieCardRef = ref<InstanceType<typeof UnqualifiedReasonPieCard>>()

onMounted(async () => {
  // 加载看板2配置（标题 / 查询日期 / 产线 / 产品型号），与看板1完全独立
  let configTitle = ''
  let configStartDate = ''
  let configEndDate = ''
  let configWorkshopCode = ''
  let configProductType: string[] = []
  try {
    const res = await api.getDashboardConfig2()
    const cfg = res.data || {}
    configTitle = cfg.title || ''
    configStartDate = cfg.start_date || ''
    configEndDate = cfg.end_date || ''
    configWorkshopCode = cfg.workshop_code || ''
    configProductType = Array.isArray(cfg.product_type) ? cfg.product_type.slice() : []
  } catch (_) {
    // 使用默认配置
  }

  if (configTitle) pageTitle.value = configTitle
  if (configStartDate) startDate.value = configStartDate
  if (configEndDate) endDate.value = configEndDate
  if (configWorkshopCode) selectedLine.value = configWorkshopCode
  productTypes.value = configProductType

  // 配置了查询日期时，同步给 OEE / 工序加工情况查询
  if (configStartDate || configEndDate) {
    oeeCardRef.value?.setDate(startDate.value, endDate.value)
    processProductionCardRef.value?.setDate(startDate.value, endDate.value)
  }

  // 配置就绪后统一启动各卡片（WS connect + 设备查询），日期/产线已先下发
  oeeCardRef.value?.start()
  processProductionCardRef.value?.start()
  deviceStatusCardRef.value?.start()

  // 饼图卡：按配置的日期 / 产线 / 产品型号统计不合格原因占比（产线空 = 全部产线）
  reasonPieCardRef.value?.load({
    start_date: startDate.value,
    end_date: endDate.value,
    workshop_code: selectedLine.value,
    product_types: productTypes.value,
  })

  // 产线名解析仅用于饼图卡头部标签展示（产线空无需查），不阻塞看板启动，失败回退显示编码
  if (configWorkshopCode) {
    resolveWorkshopName(configWorkshopCode)
  }

  configReady.value = true
})

/** 按产线编码查名称（异步补充显示，不进主流程），查不到回退显示编码 */
async function resolveWorkshopName(code: string) {
  try {
    const lineRes = await api.queryLineList()
    const line = (lineRes.data || []).find((l: any) => l.workshop_code == code)
    workshopName.value = line?.workshop_name || code
  } catch (err: any) {
    console.error('解析产线名称失败:', err)
    workshopName.value = code
  }
}
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

/* ========== 图表行：两行两列均分 ========== */
.charts-row2 {
  @apply grid grid-cols-2 gap-3 flex-1 min-h-0;
  /* 行高锁定为容器高度：minmax(0, 1fr) 的最小值必须是 0，否则 1fr 隐含 min:auto 会被卡片内容撑高、内部滚动失效 */
  grid-auto-rows: minmax(0, 1fr);
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
