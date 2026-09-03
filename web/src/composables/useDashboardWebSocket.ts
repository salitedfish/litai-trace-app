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

  function setQueryDate(dateStart: string, dateEnd: string) {
    pendingDate = { start: dateStart, end: dateEnd }
    ws.send({ action: 'set_date', date_start: dateStart, date_end: dateEnd })
  }

  function connect() {
    ws.connect({
      onConnected: () => {
        // 连接建立后补发日期，避免连接前设置时消息被丢弃（后端 provider 按连接重建，重连后也需重发）
        if (pendingDate) {
          ws.send({ action: 'set_date', date_start: pendingDate.start, date_end: pendingDate.end })
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
  }
}
