<template>
  <div class="min-h-full flex flex-col relative z-10 w-full max-w-[1400px] mx-auto pt-8">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-foreground">追溯应用</h1>
      <p class="text-sm text-muted-foreground mt-1">欢迎使用追溯应用 — 在此处开发您的业务功能</p>
    </div>

    <!-- 状态卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-card rounded-2xl border border-border/40 p-6 shadow-sm">
        <div class="flex items-center gap-4">
          <div :class="['w-12 h-12 rounded-xl flex items-center justify-center', iconBgClass]">
            <!-- 运行中 -->
            <svg v-if="status == 'running'" class="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <!-- 检测中 -->
            <svg v-else-if="status == 'checking'" class="w-6 h-6 text-yellow-600 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <!-- 未运行 -->
            <svg v-else class="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-muted-foreground">服务状态</p>
            <div class="flex items-center gap-2">
              <p :class="['text-lg font-bold', textColorClass]">{{ statusText }}</p>
              <button
                @click="testConnection"
                :disabled="status == 'checking'"
                class="p-1.5 rounded-lg hover:bg-muted/50 text-muted-foreground hover:text-accent transition-colors border border-transparent hover:border-border/50 disabled:opacity-50 disabled:cursor-not-allowed"
                title="测试连接"
              >
                <svg class="w-4 h-4" :class="{ 'animate-spin': status == 'checking' }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-card rounded-2xl border border-border/40 p-6 shadow-sm">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
          </div>
          <div>
            <p class="text-sm text-muted-foreground">API 地址</p>
            <p class="text-lg font-bold text-foreground">:18085</p>
          </div>
        </div>
      </div>

      <div class="bg-card rounded-2xl border border-border/40 p-6 shadow-sm">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
            <svg class="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>
          </div>
          <div>
            <p class="text-sm text-muted-foreground">框架</p>
            <p class="text-lg font-bold text-foreground">mg_app_framework</p>
          </div>
        </div>
      </div>
    </div>

    <!-- API 端点列表 -->
    <div class="bg-card rounded-2xl border border-border/40 p-6 shadow-sm">
      <h2 class="text-lg font-bold text-foreground mb-4">API 端点</h2>
      <div class="space-y-3">
        <div class="flex items-center gap-4 p-3 rounded-xl bg-muted/20 border border-border/40">
          <span class="px-2 py-1 rounded-lg text-xs font-bold bg-green-100 text-green-700">GET</span>
          <code class="text-sm font-mono text-foreground">/api/trace_app/health</code>
          <span class="text-sm text-muted-foreground">健康检查</span>
        </div>
        <div class="flex items-center gap-4 p-3 rounded-xl bg-muted/20 border border-border/40">
          <span class="px-2 py-1 rounded-lg text-xs font-bold bg-blue-100 text-blue-700">POST</span>
          <code class="text-sm font-mono text-foreground">/api/trace_app/echo</code>
          <span class="text-sm text-muted-foreground">回显请求参数</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../api/trace-app'

type ServiceStatus = 'checking' | 'running' | 'stopped'

const status = ref<ServiceStatus>('checking')

const statusText = computed(() => {
  if (status.value == 'running') return '运行中'
  if (status.value == 'checking') return '检测中...'
  return '未运行'
})

const iconBgClass = computed(() => {
  if (status.value == 'running') return 'bg-green-100'
  if (status.value == 'checking') return 'bg-yellow-100'
  return 'bg-red-100'
})

const textColorClass = computed(() => {
  if (status.value == 'running') return 'text-foreground'
  if (status.value == 'checking') return 'text-yellow-600'
  return 'text-red-600'
})

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

onMounted(() => {
  testConnection()
})
</script>
