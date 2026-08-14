import { ref } from 'vue'
import { useWebSocket, type WsMessage } from './useWebSocket'

declare const websocket_base_url: string

/** 计划/实际产量数据项 */
export interface PlanActualOutputData {
  plan_count: number
  actual_count: number
  progress: number
}

/** 计划/实际产量消息结构 */
export interface PlanActualOutputMessage extends WsMessage {
  type: 'plan_actual_output'
  data: PlanActualOutputData
  timestamp: string
}

function getWebSocketUrl(): string {
  return `${websocket_base_url}/ws/plan_actual_output`
}

export function usePlanActualOutput() {
  const planActual = ref<PlanActualOutputData>({ plan_count: 0, actual_count: 0, progress: 0 })
  const lastUpdate = ref('')

  const ws = useWebSocket(getWebSocketUrl())

  // 待发送的查询日期（连接建立前设置的日期会在 onConnected 时补发）
  let pendingDate: { start: string, end: string } | null = null
  // 待发送的产品型号过滤（空数组表示查全部，连接建立前设置会在 onConnected 时补发）
  let pendingProductTypes: string[] | null = null

  function setQueryDate(dateStart: string, dateEnd: string) {
    pendingDate = { start: dateStart, end: dateEnd }
    ws.send({ action: 'set_date', date_start: dateStart, date_end: dateEnd })
  }

  function setProductType(productTypes: string[]) {
    pendingProductTypes = Array.isArray(productTypes) ? productTypes.slice() : []
    ws.send({ action: 'set_product_type', product_types: pendingProductTypes })
  }

  function connect() {
    ws.connect({
      onConnected: () => {
        // 连接建立后补发日期/产品类型，避免连接前设置时消息被丢弃
        if (pendingDate) {
          ws.send({ action: 'set_date', date_start: pendingDate.start, date_end: pendingDate.end })
        }
        if (pendingProductTypes) {
          ws.send({ action: 'set_product_type', product_types: pendingProductTypes })
        }
      },
      handlers: {
        plan_actual_output: (msg) => {
          const data = (msg as PlanActualOutputMessage).data
          if (data && typeof data == 'object') {
            planActual.value = {
              plan_count: Number(data.plan_count) || 0,
              actual_count: Number(data.actual_count) || 0,
              progress: Number(data.progress) || 0,
            }
          }
          lastUpdate.value = msg.timestamp || ''
        },
      },
    })
  }

  return {
    planActual,
    connected: ws.connected,
    lastUpdate,
    connect,
    disconnect: ws.disconnect,
    setQueryDate,
    setProductType,
  }
}
