import { reactive } from 'vue'

// 追溯查询 → 数采查询的跨视图跳转预填状态。
// 应用无 router、视图在 App.vue 用 v-show 常驻挂载，故用模块级单例状态传递：
// 写方 TraceQueryView（navigateToDeviceData），读方 DeviceDataView（watch pending）。
export type DeviceDataNavState = {
  device_code: string
  start_time: string
  end_time: string
  pending: boolean
}

const state = reactive<DeviceDataNavState>({
  device_code: '',
  start_time: '',
  end_time: '',
  pending: false,
})

export function useDeviceDataNav() {
  return { state }
}

// 与 DeviceDataView 搜索栏 datetime-local 输入一致的格式化（YYYY-MM-DDTHH:mm）
export const formatDatetimeLocal = (d: Date) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${day}T${h}:${min}`
}

// 以报工时间为中点，前后各取 30 分钟，写入预填状态。
// 返回 false 表示缺少设备或报工时间无效，无法跳转。
export const navigateToDeviceData = (params: { device_code: string; report_time: string }) => {
  const report = (params.report_time || '').trim().replace(/\.\d+$/, '')
  if (!params.device_code || !report) return false
  // 兼容 '2026-07-14 09:14:57' 空格分隔写法（含毫秒已在上方剥掉）
  const t = new Date(report.includes('T') ? report : report.replace(' ', 'T'))
  if (isNaN(t.getTime())) return false
  state.device_code = params.device_code
  state.start_time = formatDatetimeLocal(new Date(t.getTime() - 30 * 60 * 1000))
  state.end_time = formatDatetimeLocal(new Date(t.getTime() + 30 * 60 * 1000))
  state.pending = true
  return true
}
