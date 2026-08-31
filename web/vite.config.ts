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
      // 最低支持到 Chrome 64：产物体内用到 import.meta（Chrome 64+），且需 esbuild 把 ES2020/21 语法
    // （??=、||=、?? 等）降级 —— 电视自带浏览器内核普遍偏老，目标线过高会导致白屏（SyntaxError）
    target: 'chrome64',
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
