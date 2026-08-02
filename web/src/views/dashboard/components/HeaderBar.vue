<template>
  <header class="dashboard-header">
    <div class="header-left">
      <div class="header-left-inner">
        <div class="status-badge">
          <span class="status-dot"></span>
          <span>系统运行中</span>
        </div>
        <button class="filter-btn" @click="emit('openFilter')" title="更多操作">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
        <button class="exit-btn" @click="emit('exit')" title="退出看板">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
    <div class="header-center">
      <h1 class="header-title">{{ title }}</h1>
    </div>
    <div class="header-right">
      <div class="datetime-display">
        <span class="datetime-date">{{ currentDate }}</span>
        <span class="datetime-time">{{ currentTime }}</span>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

defineProps<{ title: string }>()
const emit = defineEmits<{ (e: 'openFilter'): void; (e: 'exit'): void }>()

// ========== 时钟（每秒刷新） ==========
const currentDate = ref('')
const currentTime = ref('')

const updateClock = () => {
  const now = new Date()
  const days = ['日', '一', '二', '三', '四', '五', '六']
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  const day = days[now.getDay()]
  currentDate.value = `${y}年${m}月${d}日 星期${day}`
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false })
}

let clockTimer: number

onMounted(() => {
  updateClock()
  clockTimer = window.setInterval(updateClock, 1000)
})

onUnmounted(() => {
  clearInterval(clockTimer)
})
</script>

<style scoped>
.dashboard-header {
  @apply relative z-10 flex items-center justify-between shrink-0;
  height: 60px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.header-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.header-left-inner {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title {
  @apply text-lg font-bold tracking-tight;
  color: #f0f4ff;
}

.filter-btn {
  @apply flex items-center gap-1.5 ml-3 px-3 py-1.5 rounded-full text-xs transition-all duration-200;
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.15);
  color: rgba(148, 184, 255, 0.8);
}

.filter-btn:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.25);
  color: #93c5fd;
}

.status-badge {
  @apply flex items-center gap-2 px-3 py-1.5 rounded-full text-xs;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.exit-btn {
  @apply flex items-center gap-1.5 ml-3 px-3 py-1.5 rounded-full text-xs transition-all duration-200;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.15);
  color: rgba(248, 113, 113, 0.8);
}

.exit-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.25);
  color: #f87171;
}

.datetime-display {
  @apply flex flex-col items-center;
}

.datetime-date {
  @apply text-xs;
  color: rgba(200, 218, 255, 0.7);
  font-family: monospace;
}

.datetime-time {
  @apply text-2xl font-bold tracking-wider;
  color: #93c5fd;
  font-family: monospace;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}
</style>
