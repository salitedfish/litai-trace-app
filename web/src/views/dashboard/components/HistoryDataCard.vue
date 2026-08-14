<template>
  <div class="tech-panel history-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        历史数据
      </h3>
      <div class="header-right-group">
        <!-- 产品型号过滤（放在徽标左侧，同一行） -->
        <span
          class="product-type-tag"
          :title="'产品型号：' + (productTypes.length ? productTypes.join('、') : '全部')"
        >
          产品型号：{{ productTypes.length ? productTypes.join('、') : '全部' }}
        </span>
        <span class="tech-badge" :class="loaded ? 'live' : ''">
          <span class="tech-dot"></span>
          {{ loading ? '加载中' : loaded ? '近两周' : '未加载' }}
        </span>
      </div>
    </div>

    <div v-if="!loaded" class="tech-placeholder">
      <span class="placeholder-blink">▮</span>&nbsp;加载中...
    </div>
    <div v-else class="history-body tech-scroll">
      <table class="history-table">
        <thead>
          <tr>
            <th class="history-project">项目</th>
            <th v-for="d in historyData.days" :key="d.date" class="history-date-head">{{ d.date }}</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="history-project">日均一次合格率</td>
            <td v-for="d in historyData.days" :key="'r' + d.date" class="history-cell">{{ d.first_pass_rate }}%</td>
          </tr>
          <tr>
            <td class="history-project">日均小时完成量</td>
            <td v-for="d in historyData.days" :key="'a' + d.date" class="history-cell">{{ d.avg_hourly }}</td>
          </tr>
          <tr>
            <td class="history-project">日完成量</td>
            <td v-for="d in historyData.days" :key="'b' + d.date" class="history-cell history-total">{{ d.total_count }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '../../../api/trace-app'

interface HistoryDay {
  date: string
  total_count: number
  avg_hourly: number
  first_pass_rate: number
}

// ========== 历史数据（进看板时查一次，非实时） ==========
const historyData = ref<{ days: HistoryDay[] }>({ days: [] })
const loading = ref(false)
const loaded = ref(false)
// 当前生效的产品型号过滤（用于头部展示；空数组表示全部产品）
const productTypes = ref<string[]>([])

/** 供父组件（DashboardView）进看板时调用，按配置的产品型号查一次前两周数据 */
async function load(types: string[]) {
  productTypes.value = Array.isArray(types) ? types.slice() : []
  loading.value = true
  try {
    const res = await api.queryHistoryOutput(Array.isArray(types) ? types : [])
    const data = res.data || {}
    const days = Array.isArray(data.days) ? data.days : []
    historyData.value = {
      days: days.map((d: any) => ({
        date: String(d.date || ''),
        total_count: Number(d.total_count) || 0,
        avg_hourly: Number(d.avg_hourly) || 0,
        first_pass_rate: Number(d.first_pass_rate) || 0,
      })),
    }
    loaded.value = true
  } catch (err: any) {
    console.error('加载历史数据失败:', err)
    loaded.value = false
  } finally {
    loading.value = false
  }
}

defineExpose({ load })
</script>

<style scoped>
.history-panel {
  @apply p-3 flex flex-col;
  min-height: 0;
}

/* 压缩面板头间距（覆盖全局默认 10px） */
.history-panel .tech-panel-header {
  margin-bottom: 5px;
  padding-bottom: 4px;
}

.history-panel .tech-panel-title {
  font-size: 12px;
}

/* 压缩状态徽标（覆盖全局 tech-badge 11px） */
.history-panel .tech-badge {
  font-size: 10px;
  padding: 1px 6px;
  letter-spacing: 0.04em;
}

/* 头部右侧：产品型号 + 状态徽标（同一行） */
.header-right-group {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

/* 产品型号标签（选中多个时省略号截断，悬停看全量） */
.product-type-tag {
  display: inline-flex;
  align-items: center;
  max-width: 96px;
  padding: 1px 6px;
  border-radius: 999px;
  font-size: 10px;
  letter-spacing: 0.04em;
  color: rgba(148, 184, 255, 0.85);
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.22);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ========== 横向表格：行=项目，列=日期，铺满整卡 ========== */
.history-body {
  @apply flex-1 min-h-0 overflow-hidden;
  padding: 0 2px;
}

.history-table {
  width: 100%;
  height: 100%;
  table-layout: fixed;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 10px;
}

/* 表头（日期列）：占满行高 */
.history-table thead th {
  padding: 4px 5px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: rgba(200, 218, 255, 0.75);
  background: rgba(10, 24, 51, 0.95);
  border-bottom: 1px solid rgba(56, 189, 248, 0.15);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: middle;
}

/* 第一列「项目」固定宽度，其余日期列均分剩余 */
.history-project {
  width: 74px;
  padding: 4px 5px;
  color: rgba(200, 218, 255, 0.75);
  background: rgba(10, 24, 51, 0.95);
  border-right: 1px solid rgba(56, 189, 248, 0.15);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: left;
  vertical-align: middle;
}

.history-table tbody .history-project {
  font-weight: 500;
  letter-spacing: 0.04em;
}

/* 数据格：行高占满，数值居中，颜色统一亮白 */
.history-cell {
  padding: 4px 5px;
  text-align: right;
  vertical-align: middle;
  color: #f0f4ff;
  font-family: 'Consolas', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
  border-bottom: 1px solid rgba(56, 189, 248, 0.06);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-cell:not(:last-child) {
  border-right: 1px solid rgba(56, 189, 248, 0.05);
}

.history-total {
  font-weight: 700;
}
</style>
