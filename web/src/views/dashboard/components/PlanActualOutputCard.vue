<template>
  <div class="tech-panel chart-card-placeholder plan-actual-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3v18h18M7 15l4-4 4 3 5-6" />
        </svg>
        计划/实际产量
      </h3>
    </div>

    <div class="placeholder-text">
      <span class="placeholder-blink">▮</span>
      预留区域
    </div>
  </div>
</template>

<script setup lang="ts">
// 计划/实际产量（当前为预留区域，后续接入产量数据）
</script>

<style scoped>
.plan-actual-panel {
  @apply p-4 flex flex-col;
  min-height: 0;
}
</style>
