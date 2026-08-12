<template>
  <header class="dashboard-header">
    <div class="header-left">
      <div class="header-left-inner">
        <div class="status-badge">
          <span class="tech-dot" style="color: #34d399"></span>
          <span>系统运行中</span>
        </div>
        <button class="exit-btn" @click="emit('exit')" title="退出看板">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <div class="header-center">
      <div class="title-wrap">
        <span class="title-line title-line-l"></span>
        <svg class="title-diamond" viewBox="0 0 12 12">
          <path d="M6 0 L12 6 L6 12 L0 6 Z" fill="none" stroke="#38bdf8" stroke-width="1" />
        </svg>
        <h1 class="header-title">{{ title }}</h1>
        <svg class="title-diamond" viewBox="0 0 12 12">
          <path d="M6 0 L12 6 L6 12 L0 6 Z" fill="none" stroke="#38bdf8" stroke-width="1" />
        </svg>
        <span class="title-line title-line-r"></span>
      </div>
      <div class="title-underline"></div>
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
const emit = defineEmits<{ (e: 'exit'): void }>()

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
  height: 62px;
}

/* 底部渐变分隔线 */
.dashboard-header::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.5) 20%, rgba(56, 189, 248, 0.5) 80%, transparent);
  opacity: 0.7;
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
  flex-direction: column;
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

/* ========== 标题区 ========== */
.title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-line {
  width: 42px;
  height: 1px;
  margin-top: 4px;
}

.title-line-l {
  background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.7));
}

.title-line-r {
  background: linear-gradient(90deg, rgba(56, 189, 248, 0.7), transparent);
}

.title-diamond {
  width: 10px;
  height: 10px;
  filter: drop-shadow(0 0 4px rgba(56, 189, 248, 0.8));
}

.header-title {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.3em;
  margin-right: -0.3em; /* 抵消末位字距，保证视觉居中 */
  background: linear-gradient(180deg, #ffffff 0%, #bfdbff 55%, #7fb2ff 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  filter: drop-shadow(0 0 12px rgba(59, 130, 246, 0.5));
}

.title-underline {
  width: 132px;
  height: 3px;
  margin-top: 6px;
  background:
    linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.6) 20%, rgba(56, 189, 248, 0.6) 80%, transparent);
  clip-path: polygon(0 50%, 6% 0, 12% 100%, 18% 0, 24% 100%, 30% 0, 36% 100%, 42% 0, 48% 100%, 54% 0, 60% 100%, 66% 0, 72% 100%, 78% 0, 84% 100%, 90% 0, 94% 50%, 100% 50%);
  opacity: 0.75;
}

/* ========== 状态徽标 ========== */
.status-badge {
  @apply flex items-center gap-2 px-3 py-1.5 rounded-full text-xs;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.25);
  color: #34d399;
  letter-spacing: 0.06em;
  box-shadow: inset 0 0 8px rgba(16, 185, 129, 0.06);
}

.exit-btn {
  @apply flex items-center gap-1.5 ml-3 px-3 py-1.5 rounded-full text-xs transition-all duration-200;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.18);
  color: rgba(248, 113, 113, 0.8);
}

.exit-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(248, 113, 113, 0.35);
  color: #f87171;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
}

/* ========== 时间显示 ========== */
.datetime-display {
  @apply flex flex-col items-center;
}

.datetime-date {
  @apply text-xs;
  color: rgba(200, 218, 255, 0.7);
  font-family: 'Consolas', 'Courier New', monospace;
  letter-spacing: 0.12em;
}

.datetime-time {
  @apply text-2xl font-bold tracking-wider;
  color: #93c5fd;
  font-family: 'Consolas', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
}

.datetime-time::after {
  content: '';
  display: inline-block;
  width: 2px;
  height: 20px;
  margin-left: 6px;
  vertical-align: middle;
  background: #38bdf8;
  animation: blinkCursor 1s step-end infinite;
  opacity: 0.7;
}

@keyframes blinkCursor {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 0; }
}
</style>
