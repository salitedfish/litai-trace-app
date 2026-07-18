import { ref } from 'vue'
import api from '../api/trace-app'

export type ServiceStatus = 'checking' | 'running' | 'stopped'

const status = ref<ServiceStatus>('checking')
let initialized = false

export function useServiceStatus() {
  const testConnection = async () => {
    status.value = 'checking'
    try {
      const res = await api.health()
      if (res?.code == 'success' && res?.data?.status == 'ok') {
        status.value = 'running'
      } else {
        status.value = 'stopped'
      }
    } catch (err) {
      console.error('服务连接失败', err)
      status.value = 'stopped'
    }
  }

  if (!initialized) {
    initialized = true
    testConnection()
  }

  return {
    status,
    testConnection,
  }
}
