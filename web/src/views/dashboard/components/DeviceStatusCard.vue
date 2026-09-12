<template>
  <div class="tech-panel dev-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        产线设备
        <span v-if="title" class="line-name">{{ title }}</span>
      </h3>
      <div class="header-right-group">
        <!-- 状态图例（放在"实时"左侧，同一行） -->
        <div v-if="hasDevices" class="status-legend">
          <span v-for="s in legendItems" :key="s.name" class="legend-item">
            <i class="legend-dot" :style="{ background: s.color, boxShadow: `0 0 5px ${s.color}` }"></i>
            {{ s.name }}
          </span>
        </div>
        <span class="tech-badge" :class="badgeLive ? 'live' : 'offline'">
          <span class="tech-dot"></span>
          {{ badgeLive ? '实时' : '断开' }}
        </span>
      </div>
    </div>

    <div v-if="loading" class="tech-placeholder">
      <span class="placeholder-blink">▮</span>&nbsp;加载中...
    </div>
    <div v-else-if="error" class="tech-placeholder">{{ error }}</div>
    <div v-else-if="units.length == 0" class="tech-placeholder">暂无设备数据</div>
    <div v-else class="processes-wrap">
      <div class="devices-grid tech-scroll">
        <div
          v-for="dev in allDevices"
          :key="dev.device_code"
          class="device-tile"
          :style="tileStyle(dev.status)"
          :title="dev.unit_name + ' · ' + dev.device_code"
        >
          <img :src="deviceIcon(dev.device_type, dev.status)" class="device-tile-icon" />
          <span class="device-tile-name">{{ dev.device_name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'
import api from '../../../api/trace-app'
import { useDeviceStatus, STATUS_NAMES } from '../../../composables/useDeviceStatus'
import deviceDetectOff from '../../../assets/device_status/检测(关机).png'
import deviceDetectStandby from '../../../assets/device_status/检测(待机).png'
import deviceDetectFault from '../../../assets/device_status/检测(故障).png'
import deviceDetectRunning from '../../../assets/device_status/检测(运行).png'
import deviceNonDetectOff from '../../../assets/device_status/非检测(关机).png'
import deviceNonDetectStandby from '../../../assets/device_status/非检测(待机).png'
import deviceNonDetectFault from '../../../assets/device_status/非检测(故障).png'
import deviceNonDetectRunning from '../../../assets/device_status/非检测(运行).png'

export interface LineUnit {
  produce_unit_code: string
  produce_unit_name: string
  devices: { device_code: string, device_name: string, device_type: string, status?: string }[]
}

/** 看板2 模拟数据结构（客户演示用）：产线名 + 生产单元及设备，每个设备带 status 中文状态名 */
export interface DeviceStatusMock {
  workshop_name?: string
  units?: LineUnit[]
}

const props = defineProps<{
  lineCode: string
  mockData?: DeviceStatusMock | null
}>()

// ========== WebSocket 设备实时状态（组件自管理） ==========
const {
  deviceStatus,
  connected,
  connect: connectDeviceStatus,
  disconnect: disconnectDeviceStatus,
} = useDeviceStatus()

// ========== 产线设备查询（组件自管理，切换产线重新加载；产线空 = 全部产线） ==========
const title = ref('')
const units = ref<LineUnit[]>([])
const loading = ref(false)
const error = ref('')

const isMock = computed(() => !!props.mockData)

// 模拟模式下不连 WebSocket，但徽标须与正式看板一致显示"实时"——不能露出一块"断开"
const badgeLive = computed(() => isMock.value || connected.value)

// 模拟模式下的设备状态（device_code → 中文状态名），与真实链路的状态 map 分开存放，互不干扰
const mockStatus = ref<Record<string, string>>({})

/** 把配置的模拟数据摊平成渲染用的 units + 状态表；缺省字段补默认值，保证渲染路径不落空 */
const applyMock = () => {
  const mock = props.mockData || {}
  const mockUnits: LineUnit[] = []
  const statusMap: Record<string, string> = {}
  const unitList = Array.isArray(mock.units) ? mock.units : []
  unitList.forEach((unit: any, ui: number) => {
    const deviceList = Array.isArray(unit?.devices) ? unit.devices : []
    const devices = deviceList.map((dev: any, di: number) => {
      // device_code 仅作渲染 key，配置里没填就补一个稳定的自动值
      const deviceCode = String(dev?.device_code || 'mock_' + ui + '_' + di)
      // 状态非四种之一时退回"关机"，避免渲染出没有配色的状态
      const status = String(dev?.status || '')
      statusMap[deviceCode] = STATUS_NAMES.indexOf(status) >= 0 ? status : '关机'
      return {
        device_code: deviceCode,
        device_name: String(dev?.device_name || ''),
        device_type: String(dev?.device_type || '非检测'),
      }
    })
    mockUnits.push({
      produce_unit_code: String(unit?.produce_unit_code || 'mock_unit_' + ui),
      produce_unit_name: String(unit?.produce_unit_name || ''),
      devices: devices,
    })
  })
  title.value = String(mock.workshop_name || '全部产线')
  units.value = mockUnits
  mockStatus.value = statusMap
}

const loadLineDevices = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await api.queryLineDevices(props.lineCode)
    title.value = res.data?.workshop_name || '全部产线'
    units.value = res.data?.units || []
  } catch (err: any) {
    console.error('加载产线设备失败:', err)
    error.value = '设备数据加载失败'
  } finally {
    loading.value = false
  }
}

watch(() => props.lineCode, () => {
  // 模拟模式下不查真实产线设备
  if (isMock.value) return
  loadLineDevices()
})

/** 供父组件在配置就绪后启动：模拟模式直接落配置值，否则连 WS + 查产线设备（产线空则全部产线） */
function start() {
  if (isMock.value) {
    applyMock()
    return
  }
  connectDeviceStatus()
  loadLineDevices()
}

defineExpose({ start })

onUnmounted(() => {
  disconnectDeviceStatus()
})

// 设备类型（检测/非检测）× 状态（关机/待机/故障/运行）→ 图标
const deviceIcon = (deviceType: string, status: string) => {
  const detect = deviceType == '检测'
  if (status == '运行') return detect ? deviceDetectRunning : deviceNonDetectRunning
  if (status == '待机') return detect ? deviceDetectStandby : deviceNonDetectStandby
  if (status == '故障') return detect ? deviceDetectFault : deviceNonDetectFault
  return detect ? deviceDetectOff : deviceNonDetectOff
}

// 状态 → 主题色（光晕 / 顶线 / 角点）
const STATUS_COLORS: Record<string, string> = {
  运行: '#34d399',
  待机: '#fbbf24',
  故障: '#f87171',
  关机: '#5b6b8c',
}

const legendItems = ['运行', '待机', '故障', '关机'].map(name => ({ name, color: STATUS_COLORS[name] }))

const hasDevices = computed(() => units.value.some(u => u.devices.length > 0))

// 产线所有设备拍平到单个网格横向排列自动换行；状态取自 WebSocket 实时推送，取不到默认关机
const allDevices = computed(() => {
  const result: { device_code: string, device_name: string, device_type: string, status: string, unit_name: string }[] = []
  for (const u of units.value) {
    for (const dev of u.devices) {
      // 模拟模式取配置的状态；真实链路取 WebSocket 推送的状态码（无记录默认关机）
      const status = isMock.value
        ? (mockStatus.value[dev.device_code] || '关机')
        : (STATUS_NAMES[deviceStatus.value[dev.device_code] || 0] || '关机')
      result.push({ ...dev, status: status, unit_name: u.produce_unit_name })
    }
  }
  return result
})

// 设备磁贴行内样式（状态主题色 + 光晕透明度）
const tileStyle = (status: string) => {
  const color = STATUS_COLORS[status] || STATUS_COLORS['关机']
  const rgb = hexToRgb(color)
  return {
    '--st-color': color,
    '--st-alpha': `rgba(${rgb}, 0.22)`,
    '--st-alpha2': `rgba(${rgb}, 0.5)`,
  }
}

function hexToRgb(hex: string): string {
  const v = parseInt(hex.slice(1), 16)
  return `${(v >> 16) & 255}, ${(v >> 8) & 255}, ${v & 255}`
}
</script>

<style scoped>
.dev-panel {
  @apply p-4 flex flex-col;
  min-height: 0;
}

/* ========== 状态图例 ========== */
.header-right-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-legend {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  letter-spacing: 0.1em;
  color: rgba(148, 184, 255, 0.6);
}

.legend-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
}

/* ========== 设备网格 ========== */
.processes-wrap {
  @apply flex-1 flex flex-col min-h-0;
}

.devices-grid {
  @apply flex-1 overflow-y-auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-content: flex-start;
  gap: 8px;
  padding-bottom: 2px;
}

/* ========== 设备磁贴 ========== */
.device-tile {
  position: relative;
  @apply flex flex-col items-center gap-1 rounded-md px-2 py-2;
  width: 84px;
  background: linear-gradient(180deg, rgba(56, 189, 248, 0.07), rgba(56, 189, 248, 0.02));
  border: 1px solid rgba(56, 189, 248, 0.14);
  transition: all 0.25s ease;
  cursor: default;
}

/* 状态顶线 */
.device-tile::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--st-color);
  box-shadow: 0 0 8px var(--st-color);
  opacity: 0.85;
}

/* 状态角点 */
.device-tile::after {
  content: '';
  position: absolute;
  top: 4px;
  right: 4px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--st-color);
  box-shadow: 0 0 5px var(--st-color);
}

.device-tile:hover {
  transform: translateY(-2px);
  border-color: var(--st-color);
  box-shadow: 0 0 14px var(--st-alpha), inset 0 0 12px var(--st-alpha);
}

.device-tile-icon {
  width: 44px;
  height: 44px;
  object-fit: contain;
  filter: drop-shadow(0 0 6px var(--st-alpha2));
  transition: filter 0.25s ease;
}

.device-tile:hover .device-tile-icon {
  filter: drop-shadow(0 0 10px var(--st-alpha2));
}

.device-tile-name {
  @apply text-center truncate;
  width: 100%;
  font-size: 10px;
  color: rgba(200, 218, 255, 0.85);
}

.placeholder-blink {
  color: #38bdf8;
  animation: techPulse 1.2s ease-in-out infinite;
}
</style>
