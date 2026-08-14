import { ref } from 'vue'
import { useWebSocket, type WsMessage } from './useWebSocket'

declare const websocket_base_url: string

/** 工序合格率数据项 */
export interface ProcessQualityItem {
  procedure_code: string
  procedure_name: string
  total: number
  good: number
  quality_rate: number
}

/** 工序合格率消息结构 */
export interface ProcessQualityMessage extends WsMessage {
  type: 'process_quality'
  data: ProcessQualityItem[]
  timestamp: string
  query_date?: string
}

function getWebSocketUrl(): string {
  return `${websocket_base_url}/ws/process_quality`
}

export function useProcessQuality() {
  const processQuality = ref<ProcessQualityItem[]>([])
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
        process_quality: (msg) => {
          processQuality.value = (msg as ProcessQualityMessage).data || []
          lastUpdate.value = msg.timestamp || ''
        },
      },
    })
  }

  return {
    processQuality,
    connected: ws.connected,
    lastUpdate,
    connect,
    disconnect: ws.disconnect,
    setQueryDate,
  }
}
