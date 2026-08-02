<template>
  <div class="chart-card chart-card-placeholder">
    <div class="chart-header">
      <h3 class="chart-title">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        产线设备
      </h3>
      <span class="chart-badge" :class="{ 'text-green-400': connected }">
        {{ connected ? '实时' : '断开' }}
      </span>
    </div>
    <div v-if="!selected" class="placeholder-text">请选择产线</div>
    <div v-else-if="loading" class="placeholder-text">加载中...</div>
    <div v-else-if="error" class="placeholder-text">{{ error }}</div>
    <div v-else-if="units.length == 0" class="placeholder-text">该产线暂无设备数据</div>
    <div v-else class="processes-wrap">
      <div class="processes-title">{{ title }}</div>
      <div class="devices-grid">
        <div v-for="dev in allDevices" :key="dev.device_code" class="device-tile" :title="dev.unit_name + ' · ' + dev.device_code">
          <img :src="deviceIcon(dev.device_type, dev.status)" class="device-tile-icon" />
          <span class="device-tile-name">{{ dev.device_name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
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

const props = defineProps<{
  lineCode: string
}>()

// ========== WebSocket 设备实时状态（组件自管理） ==========
const {
  deviceStatus,
  connected,
  connect: connectDeviceStatus,
  disconnect: disconnectDeviceStatus,
} = useDeviceStatus()

// ========== 产线设备查询（组件自管理，切换产线重新加载） ==========
const title = ref('')
const units = ref<LineUnit[]>([])
const loading = ref(false)
const error = ref('')

const selected = computed(() => !!props.lineCode)

const loadLineDevices = async () => {
  if (!props.lineCode) {
    title.value = ''
    units.value = []
    error.value = ''
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await api.queryLineDevices(props.lineCode)
    title.value = res.data?.workshop_name || ''
    units.value = res.data?.units || []
  } catch (err: any) {
    console.error('加载产线设备失败:', err)
    error.value = '设备数据加载失败'
  } finally {
    loading.value = false
  }
}

watch(() => props.lineCode, () => {
  loadLineDevices()
})

onMounted(() => {
  connectDeviceStatus()
  loadLineDevices()
})

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

// 按生产单元拍平所有设备，横向排列自动换行；状态取自 WebSocket 推送的实时状态，取不到默认关机
const allDevices = computed(() => {
  const result: { device_code: string, device_name: string, device_type: string, status: string, unit_name: string }[] = []
  for (const u of units.value) {
    for (const dev of u.devices) {
      const statusCode = deviceStatus.value[dev.device_code] || 0
      result.push({ ...dev, status: STATUS_NAMES[statusCode] || '关机', unit_name: u.produce_unit_name })
    }
  }
  return result
})
</script>

<style scoped>
.chart-card {
  @apply rounded-xl p-4 flex flex-col;
  background: linear-gradient(135deg, rgba(30, 58, 95, 0.4), rgba(15, 31, 61, 0.2));
  border: 1px solid rgba(59, 130, 246, 0.12);
  min-height: 0;
}

.chart-card-placeholder {
  border-style: dashed;
  border-color: rgba(59, 130, 246, 0.15);
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

.placeholder-text {
  @apply flex-1 flex items-center justify-center;
  font-size: 13px;
  letter-spacing: 0.2em;
  color: rgba(148, 184, 255, 0.3);
}

/* ========== 产线设备展示 ========== */
.processes-wrap {
  @apply flex-1 flex flex-col min-h-0;
}

.processes-title {
  @apply shrink-0 mb-2;
  font-size: 13px;
  font-weight: 600;
  color: rgba(200, 218, 255, 0.9);
}

.devices-grid {
  @apply flex-1 overflow-y-auto;
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  gap: 8px;
}

.devices-grid::-webkit-scrollbar {
  width: 4px;
}

.devices-grid::-webkit-scrollbar-track {
  background: transparent;
}

.devices-grid::-webkit-scrollbar-thumb {
  background-color: rgba(59, 130, 246, 0.3);
  border-radius: 20px;
}

.device-tile {
  @apply flex flex-col items-center gap-1 rounded-lg px-2 py-2;
  width: 84px;
  background: rgba(59, 130, 246, 0.06);
  border: 1px solid rgba(59, 130, 246, 0.12);
}

.device-tile-icon {
  width: 44px;
  height: 44px;
  object-fit: contain;
}

.device-tile-name {
  @apply text-center truncate;
  width: 100%;
  font-size: 10px;
  color: rgba(200, 218, 255, 0.85);
}
</style>
