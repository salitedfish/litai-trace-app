import { ref } from 'vue'
import { useWebSocket, type WsMessage } from './useWebSocket'

declare const websocket_base_url: string

/** OEE 单条数据项 */
export interface OeeItem {
  name: string
  value: number | string
  max?: number
}

/** OEE 消息结构 */
export interface OeeMessage extends WsMessage {
  type: 'oee'
  data: OeeItem[]
  timestamp: string
  query_date?: string
}

/** 结构化 OEE 数据 */
export interface OeeData {
  target: number
  oee: number | string
  availability: number | string
  performance: number | string
  quality: number | string
}

const DEFAULT_OEE: OeeData = {
  target: 99,
  oee: '-',
  availability: '-',
  performance: '-',
  quality: '-',
}

function parseOeeMessage(msg: OeeMessage): OeeData {
  const items = msg.data
  const result = { ...DEFAULT_OEE }
  for (const item of items) {
    switch (item.name) {
      case '目标值':
        result.target = Number(item.value) || 99
        break
      case 'oee':
        result.oee = item.value
        break
      case '时间开动率':
        result.availability = item.value
        break
      case '性能开动率':
        result.performance = item.value
        break
      case '合格率':
        result.quality = item.value
        break
    }
  }
  return result
}

function getWebSocketUrl(): string {
  return `${websocket_base_url}/ws/oee`
}

export function useDashboardWebSocket() {
  const oeeData = ref<OeeData>({ ...DEFAULT_OEE })
  const lastUpdate = ref('')

  const ws = useWebSocket(getWebSocketUrl())

  // 待发送的查询日期（连接建立前设置的日期会在 onConnected 时补发）
  let pendingDate: { start: string, end: string } | null = null
  // 待发送的未使用设备名单，同上——两个看板共用 /ws/oee 端点，
  // 服务端分不清调用方，名单只能由前端推上去，所以必须在连接前就备好
  let pendingUnusedDevices: string[] | null = null

  function setQueryDate(dateStart: string, dateEnd: string) {
    pendingDate = { start: dateStart, end: dateEnd }
    ws.send({ action: 'set_date', date_start: dateStart, date_end: dateEnd })
  }

  /** 设置未使用的设备（这些设备不计入 OEE）。传空数组即不排除 */
  function setUnusedDevices(devices: string[]) {
    pendingUnusedDevices = Array.isArray(devices) ? devices.slice() : []
    ws.send({ action: 'set_unused_devices', unused_devices: pendingUnusedDevices })
  }

  function connect() {
    ws.connect({
      onConnected: () => {
        // 连接建立后补发日期与设备名单，避免连接前设置时消息被丢弃（后端 provider 按连接重建，重连后也需重发）
        if (pendingDate) {
          ws.send({ action: 'set_date', date_start: pendingDate.start, date_end: pendingDate.end })
        }
        if (pendingUnusedDevices) {
          ws.send({ action: 'set_unused_devices', unused_devices: pendingUnusedDevices })
        }
      },
      handlers: {
        oee: (msg) => {
          oeeData.value = parseOeeMessage(msg as OeeMessage)
          lastUpdate.value = msg.timestamp || ''
        },
      },
    })
  }

  return {
    oeeData,
    connected: ws.connected,
    lastUpdate,
    connect,
    disconnect: ws.disconnect,
    setQueryDate,
    setUnusedDevices,
  }
}
