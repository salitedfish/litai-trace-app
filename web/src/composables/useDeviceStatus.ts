import { ref } from 'vue'
import { useWebSocket, type WsMessage } from './useWebSocket'

declare const websocket_base_url: string

/** 设备状态消息结构 */
export interface DeviceStatusMessage extends WsMessage {
  type: 'device_status'
  data: { device_map: Record<string, number> }
  timestamp: string
}

/** 状态码 → 中文文案（与后端对齐：0 关机 / 1 运行 / 2 待机 / 3 故障） */
export const STATUS_NAMES = ['关机', '运行', '待机', '故障']

function getWebSocketUrl(): string {
  return `${websocket_base_url}/ws/device_status`
}

export function useDeviceStatus() {
  const deviceStatus = ref<Record<string, number>>({})

  const ws = useWebSocket(getWebSocketUrl())

  function connect() {
    ws.connect({
      handlers: {
        device_status: (msg) => {
          const deviceMap = (msg as DeviceStatusMessage).data?.device_map
          if (deviceMap) {
            deviceStatus.value = { ...deviceMap }
          }
        },
      },
    })
  }

  function disconnect() {
    ws.disconnect()
  }

  /** 取设备状态码，无记录默认 0（关机） */
  function statusOf(deviceCode: string): number {
    return deviceStatus.value[deviceCode] || 0
  }

  return {
    deviceStatus,
    connected: ws.connected,
    connect,
    disconnect,
    statusOf,
  }
}
