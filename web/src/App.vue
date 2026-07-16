<template>
  <div class="flex h-screen overflow-hidden bg-background">
    <!-- 侧边栏 -->
    <aside class="w-64 bg-card border-r border-border/50 flex flex-col flex-shrink-0 shadow-sm">
      <div class="h-20 flex items-center px-6 border-b border-border/40">
        <div class="flex items-center gap-3">
          <img src="/logo.png" class="w-9 h-9 object-contain shrink-0" alt="Logo" />
          <span class="font-bold text-lg text-foreground truncate">追溯应用</span>
        </div>
      </div>

      <nav class="flex-1 overflow-y-auto py-6 px-4 space-y-1">
        <p class="text-[10px] font-bold text-muted-foreground uppercase tracking-widest px-2 mb-3">导航</p>

        <a href="#" @click.prevent="currentView = 'home'"
          :class="currentView === 'home' ? 'bg-accent/10 text-accent' : 'text-muted-foreground hover:bg-muted/50'"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium transition-colors">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
          <span>首页</span>
        </a>
      </nav>
    </aside>

    <!-- 主内容区 -->
    <div class="flex flex-col flex-1 w-full overflow-hidden">
      <main class="flex-1 w-full px-6 overflow-y-auto custom-scrollbar">
        <HomeView v-if="currentView === 'home'" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import HomeView from './views/HomeView.vue'

const currentView = ref('home')
</script>
