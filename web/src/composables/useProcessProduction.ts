import { ref } from 'vue'
import { useWebSocket, type WsMessage } from './useWebSocket'

declare const websocket_base_url: string

/** 工序加工情况数据项 */
export interface ProcessProductionItem {
  procedure_code: string
  procedure_name: string
  total: number
  first_pass: number
  total_good: number
  first_pass_rate: number
  total_rate: number
}

/** 工序加工情况消息结构 */
export interface ProcessProductionMessage extends WsMessage {
  type: 'process_production'
  data: ProcessProductionItem[]
  timestamp: string
  query_date?: string
}

function getWebSocketUrl(): string {
  return `${websocket_base_url}/ws/process_production`
}

export function useProcessProduction() {
  const processProduction = ref<ProcessProductionItem[]>([])
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
        // 连接建立后补发日期，避免连接前设置时消息被丢弃
        if (pendingDate) {
          ws.send({ action: 'set_date', date_start: pendingDate.start, date_end: pendingDate.end })
        }
      },
      handlers: {
        process_production: (msg) => {
          processProduction.value = (msg as ProcessProductionMessage).data || []
          lastUpdate.value = msg.timestamp || ''
        },
      },
    })
  }

  return {
    processProduction,
    connected: ws.connected,
    lastUpdate,
    connect,
    disconnect: ws.disconnect,
    setQueryDate,
  }
}
