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
      websocket_base_url: isDevMode
        ? JSON.stringify(`ws://${requestHost}/api/${scopeName}`)
        : `(location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/api/${scopeName}"`
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
