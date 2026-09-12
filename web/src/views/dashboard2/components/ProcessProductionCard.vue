<template>
  <div class="tech-panel production-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
        工序加工情况
      </h3>
      <span class="tech-badge" :class="badgeLive ? 'live' : 'offline'">
        <span class="tech-dot"></span>
        {{ badgeLive ? '实时' : '断开' }}
      </span>
    </div>

    <div v-if="items.length == 0" class="tech-placeholder">
      <span class="placeholder-blink">▮</span>&nbsp;暂无报工数据
    </div>
    <template v-else>
      <!-- 表头：固定在滚动区外，不随内容滚动 -->
      <table class="production-table">
        <thead>
          <tr>
            <th class="col-code">工序编码</th>
            <th class="col-name">工序名称</th>
            <th class="col-num">产出数量</th>
            <th class="col-rate">一次合格率</th>
            <th class="col-rate">总体合格率</th>
          </tr>
        </thead>
      </table>

      <!-- 数据行：复用通用无缝滚动组件（内容超出一屏单步循环滚动，不足一屏静止） -->
      <SeamlessScroll class="production-body">
        <table class="production-table">
          <tbody>
            <tr v-for="item in items" :key="item.procedure_code">
              <td class="prod-code col-code" :title="item.procedure_code">{{ item.procedure_code }}</td>
              <td class="prod-name col-name" :title="item.procedure_name">{{ item.procedure_name }}</td>
              <td class="prod-num col-num">{{ item.total }}</td>
              <td class="prod-rate col-rate" :class="rateClass(item.first_pass_rate)">
                <span class="rate-dot"></span>{{ item.first_pass_rate.toFixed(1) }}%
              </td>
              <td class="prod-rate col-rate" :class="rateClass(item.total_rate)">
                <span class="rate-dot"></span>{{ item.total_rate.toFixed(1) }}%
              </td>
            </tr>
          </tbody>
        </table>
      </SeamlessScroll>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onUnmounted } from 'vue'
import SeamlessScroll from '../../../components/ui/SeamlessScroll.vue'
import { useProcessProduction, type ProcessProductionItem } from '../../../composables/useProcessProduction'

// mockData：看板2 配置的模拟数据（客户演示用），传入即启用——直接展示传入值、不连 WebSocket
const props = defineProps<{ mockData?: ProcessProductionItem[] | null }>()

// ========== WebSocket 工序加工情况（组件自管理，父组件配置就绪后 start 启动） ==========
const { processProduction, connected, connect, disconnect, setQueryDate } = useProcessProduction()

const isMock = computed(() => !!props.mockData)

// 模拟模式下不连 WebSocket，但徽标须与正式看板一致显示"实时"——不能露出一块"断开"
const badgeLive = computed(() => isMock.value || connected.value)

/** 供父组件（BoardView）从看板配置读取日期后设置查询区间 */
function setDate(dateStart: string, dateEnd: string) {
  setQueryDate(dateStart, dateEnd)
}

/** 供父组件在配置就绪后启动：模拟模式不连 WebSocket（数据由父组件传入） */
function start() {
  if (isMock.value) return
  connect()
}

defineExpose({ setDate, start })

// 工序加工情况列表：模拟模式取配置数据，否则取 WebSocket 实时数据
const items = computed(() => (props.mockData ? props.mockData : processProduction.value))

/** 合格率数字颜色：低于 90% 红色，大于等于 90% 绿色 */
function rateClass(rate: number): string {
  return rate < 90 ? 'rate-low' : 'rate-good'
}

onUnmounted(() => {
  disconnect()
})
</script>

<style scoped>
.production-panel {
  @apply p-3 flex flex-col;
  min-height: 0;
}

/* 压缩面板头间距（覆盖全局默认 10px） */
.production-panel .tech-panel-header {
  margin-bottom: 5px;
  padding-bottom: 4px;
}

.production-panel .tech-panel-title {
  font-size: 12px;
}

.production-panel .tech-badge {
  font-size: 10px;
  padding: 1px 6px;
  letter-spacing: 0.04em;
}

/* ========== 滚动区：由通用 SeamlessScroll 组件接管滚动，这里只约束布局 ========== */
.production-body {
  @apply flex-1 min-h-0;
}

/* ========== 表格 ========== */
.production-table {
  width: 100%;
  table-layout: fixed;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 10px;
}

/* 表头：固定展示在滚动区外，不随内容滚动 */
.production-table thead th {
  /* 行高须为整数（line-height 固定整数 px），配合 SeamlessScroll 单步滚动保证像素对齐不抖动 */
  line-height: 16px;
  padding: 5px 6px;
  font-weight: 600;
  letter-spacing: 0.03em;
  color: rgba(176, 205, 255, 0.9);
  background: linear-gradient(180deg, #0d2148 0%, #0a1a3d 100%);
  border-bottom: 1px solid rgba(56, 189, 248, 0.25);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: middle;
}

/* 列宽：工序编码/名称偏宽，其余三列较窄。th 与 td 共用，保证拆开的表头/表体两表列对齐 */
.col-code { width: 26%; }
.col-name { width: 26%; text-align: left; padding-left: 8px; }
.col-num { width: 15%; }
.col-rate { width: 16.5%; }

/* 数据格 */
.production-table tbody td {
  /* 行高须为整数（line-height 固定整数 px），配合 SeamlessScroll 单步滚动保证像素对齐不抖动 */
  line-height: 16px;
  padding: 5px 6px;
  border-bottom: 1px solid rgba(56, 189, 248, 0.06);
  text-align: center;
  vertical-align: middle;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: background 0.15s ease;
}

/* 行 hover 高亮 */
.production-table tbody tr:hover td {
  background: rgba(59, 130, 246, 0.08);
}

.prod-code {
  color: rgba(148, 184, 255, 0.85);
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 10px;
}

/* 工序名称：表头与内容统一左对齐 */
.prod-name {
  color: rgba(200, 218, 255, 0.88);
  text-align: left;
  padding-left: 8px;
}

.prod-num {
  color: #f0f4ff;
  font-family: 'Consolas', 'Courier New', monospace;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.prod-rate {
  font-family: 'Consolas', 'Courier New', monospace;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

/* 合格率色点指示 */
.rate-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 4px;
  vertical-align: middle;
  box-shadow: 0 0 6px currentColor;
}

.rate-good {
  color: #34d399;
  text-shadow: 0 0 8px rgba(52, 211, 153, 0.4);
}

.rate-good .rate-dot {
  background: #34d399;
}

.rate-low {
  color: #f87171;
  text-shadow: 0 0 8px rgba(248, 113, 113, 0.4);
}

.rate-low .rate-dot {
  background: #f87171;
}
</style>
