<template>
  <div class="datetime-display">
    <span class="datetime-date">{{ currentDate }}</span>
    <span class="datetime-time">{{ currentTime }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

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
