<template>
  <aside :class="['bg-card border-r border-border/50 flex flex-col transition-all duration-300 flex-shrink-0 shadow-sm overflow-hidden',
    isMobile ? 'fixed inset-y-0 left-0 z-50 h-screen shadow-2xl' : 'relative z-20 h-screen',
    isSidebarOpen ? 'w-64' : 'w-0 border-r-0']">
    <div class="h-20 flex items-center px-6 border-b border-border/40 bg-white/40 backdrop-blur-md">
      <div class="flex items-center gap-3 w-48">
        <img src="/logo.png" class="w-9 h-9 object-contain shrink-0" alt="Logo" />
        <span class="font-display tracking-tight text-lg text-foreground font-bold truncate" :title="appName">{{ appName }}</span>
      </div>
    </div>

    <nav class="flex-1 overflow-y-auto py-6 px-4 space-y-1 custom-scrollbar w-64">
      <p class="text-[10px] font-mono font-bold text-muted-foreground uppercase tracking-widest px-2 mb-3">导航</p>

      <a href="#" @click.prevent="currentView = 'home'"
        :class="currentView === 'home' ? 'bg-accent/10 text-accent border-accent/20' : 'text-muted-foreground hover:bg-muted/50 border-transparent hover:text-foreground'"
        class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium shadow-sm transition-colors border">
        <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
        <span class="text-sm shrink-0">首页</span>
      </a>
    </nav>

    <div class="p-4 border-t border-border/40 w-64">
      <div class="flex items-center gap-3 px-3 py-2 rounded-xl bg-muted/50 border border-border/50">
        <span class="relative flex h-2 w-2 shrink-0">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
        </span>
        <span class="text-xs font-mono text-muted-foreground shrink-0">系统状态: 正常</span>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, inject } from 'vue'
import type { Ref } from 'vue'

const appName = ref('追溯应用')
const isSidebarOpen = inject<Ref<boolean>>('isSidebarOpen', ref(true))
const isMobile = inject<Ref<boolean>>('isMobile', ref(false))
const currentView = inject<Ref<string>>('currentView', ref('home'))
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #E2E8F0; border-radius: 20px; }
</style>
