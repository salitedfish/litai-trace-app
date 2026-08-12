<template>
  <div class="tech-panel chart-card-placeholder hourly-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
        </svg>
        小时产量统计
      </h3>
    </div>

    <div class="placeholder-text">
      <span class="placeholder-blink">▮</span>
      预留区域
    </div>
  </div>
</template>

<script setup lang="ts">
// 小时产量统计（当前为预留区域，后续接入小时产量数据）
</script>

<style scoped>
.hourly-panel {
  @apply p-4 flex flex-col;
  min-height: 0;
}
</style>
