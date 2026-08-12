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

  function connect() {
    ws.connect({
      handlers: {
        oee: (msg) => {
          oeeData.value = parseOeeMessage(msg as OeeMessage)
          lastUpdate.value = msg.timestamp || ''
        },
      },
    })
  }

  function setQueryDate(dateStart: string, dateEnd: string) {
    ws.send({ action: 'set_date', date_start: dateStart, date_end: dateEnd })
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
