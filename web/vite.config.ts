import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import packageObj from './package.json'

export default defineConfig(({ mode }) => {
  const isDevMode = mode === 'development'
  const requestHost = 'localhost:18085'
  const scopeName = packageObj.name || 'trace_app'

  return {
    base: './',
    build: {
      target: 'chrome88',
      outDir: `dist/${scopeName}`
    },
    plugins: [vue()],
    define: {
      http_base_url: isDevMode ? JSON.stringify('/') : 'location.origin',
      // WebSocket 直连后端 host:port（不经过 nginx /api 代理，后端 WS 路由在根路径 /ws/...）
      websocket_base_url: isDevMode
        ? JSON.stringify(`ws://${requestHost}`)
        : `(location.protocol === "https:" ? "wss://" : "ws://") + location.hostname + ":18085"`
    },
    server: {
      host: '0.0.0.0',
      port: 8081,
      proxy: {
        '/api': {
          target: `http://${requestHost}`,
          changeOrigin: true
        }
      }
    }
  }
})
