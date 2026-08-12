<template>
  <div class="tech-panel chart-card-placeholder qualified-panel">
    <div class="tech-panel-header">
      <h3 class="tech-panel-title">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.6-2.6A9 9 0 1111 3a9 9 0 016.6 3.4z" />
        </svg>
        工序合格率
      </h3>
    </div>

    <div class="placeholder-text">
      <span class="placeholder-blink">▮</span>
      预留区域
    </div>
  </div>
</template>

<script setup lang="ts">
// 工序合格率（当前为预留区域，后续接入合格率数据）
</script>

<style scoped>
.qualified-panel {
  @apply p-4 flex flex-col;
  min-height: 0;
}
</style>
