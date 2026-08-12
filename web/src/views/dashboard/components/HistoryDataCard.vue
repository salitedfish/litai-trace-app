<template>
  <div class="tech-panel chart-card-placeholder history-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        历史数据
      </h3>
    </div>

    <div class="placeholder-text">
      <span class="placeholder-blink">▮</span>
      预留区域
    </div>
  </div>
</template>

<script setup lang="ts">
// 历史数据（当前为预留区域，后续接入历史数据）
</script>

<style scoped>
.history-panel {
  @apply p-4 flex flex-col;
  min-height: 0;
}
</style>
