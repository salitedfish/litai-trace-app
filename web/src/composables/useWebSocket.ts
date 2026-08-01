import { ref, onUnmounted } from 'vue'

const RECONNECT_INTERVAL = 5000

export interface WsMessage {
  type: string
  [key: string]: any
}

export interface WsOptions {
  /** 消息处理器，按 type 分发 */
  handlers?: Record<string, (msg: WsMessage) => void>
  /** 连接成功后回调 */
  onConnected?: () => void
  /** 连接断开回调 */
  onDisconnected?: () => void
}

/** 通用 WebSocket composable
 *
 * 用法：
 *   const ws = useWebSocket('ws://...')
 *   ws.connect({ handlers: { oee: msg => handleOee(msg) } })
 *   ws.send({ action: 'set_date', ... })
 *   ws.disconnect()
 */
export function useWebSocket(url: string) {
  const connected = ref(false)

  let ws: WebSocket | null = null
  let reconnectTimer: number | null = null
  let destroyed = false
  let options: WsOptions = {}

  function connect(opts?: WsOptions) {
    if (destroyed) return
    if (ws) close()

    options = opts || {}

    try {
      ws = new WebSocket(url)

      ws.onopen = () => {
        connected.value = true
        if (reconnectTimer !== null) {
          clearTimeout(reconnectTimer)
          reconnectTimer = null
        }
        options.onConnected?.()
      }

      ws.onmessage = (event: MessageEvent) => {
        try {
          const msg: WsMessage = JSON.parse(event.data)
          const handler = options.handlers?.[msg.type]
          if (handler) {
            handler(msg)
          }
        } catch {
          // ignore parse errors
        }
      }

      ws.onclose = () => {
        connected.value = false
        ws = null
        options.onDisconnected?.()
        if (!destroyed) {
          reconnectTimer = window.setTimeout(() => connect(options), RECONNECT_INTERVAL)
        }
      }

      ws.onerror = () => {
        // onclose 会紧随其后
      }
    } catch {
      if (!destroyed) {
        reconnectTimer = window.setTimeout(() => connect(options), RECONNECT_INTERVAL)
      }
    }
  }

  function send(data: Record<string, any>) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
    }
  }

  function close() {
    if (ws) {
      ws.close()
      ws = null
    }
  }

  function disconnect() {
    destroyed = true
    if (reconnectTimer !== null) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    close()
    connected.value = false
  }

  onUnmounted(disconnect)

  return { connected, connect, send, close, disconnect }
}
