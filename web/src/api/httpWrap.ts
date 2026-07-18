import axios from 'axios'
import { showToast } from '../utils/dialog'

declare const http_base_url: string

const getBasePrefix = () => {
  const path = window.location.pathname
  const appName = 'trace_app'
  const appIndex = path.indexOf(`/${appName}`)
  if (appIndex > 0) {
    return path.substring(0, appIndex)
  }
  return ''
}

const getBaseUrl = () => {
  if (import.meta.env.DEV) {
    return http_base_url
  }
  return window.location.origin + getBasePrefix()
}

const instance = axios.create({
  baseURL: getBaseUrl(),
  timeout: 15000,
})

instance.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

instance.interceptors.response.use(
  response => {
    const res = response.data
    if (res && res.code === 'login') {
      if (!(window as any)._isRedirecting) {
        (window as any)._isRedirecting = true
        const appId = res.data?.app_id
        if (appId) {
          const authUrl = `${window.location.origin}${getBasePrefix()}/auth/#/login`
          window.location.href = `${authUrl}?path=${encodeURIComponent(window.location.href)}&appId=${appId}`
        } else if (res.data?.login_url) {
          window.location.href = res.data.login_url
        }
      }
      return Promise.reject(new Error(res.info || '未登录'))
    }
    return res
  },
  error => {
    console.error('API Request Error:', error)
    const msg = error?.response?.status
      ? `请求失败 (${error.response.status}${error.response.statusText ? ': ' + error.response.statusText : ''})`
      : (error?.message || '网络请求失败')
    showToast(msg, 'error')
    return Promise.reject(error)
  }
)

export interface ApiResponse<T = any> {
  code: string
  data: T
  info: string
}

export const _get = async <T = any>(url: string, params?: any): Promise<ApiResponse<T>> => {
  const res = await instance.get(url, { params })
  return res as unknown as ApiResponse<T>
}
export const _post = async <T = any>(url: string, data?: any): Promise<ApiResponse<T>> => {
  const res = await instance.post(url, data)
  return res as unknown as ApiResponse<T>
}
export const _postBlob = (url: string, data?: any) => instance.post(url, data, { responseType: 'blob' })
