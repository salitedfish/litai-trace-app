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

      <template v-for="item in navItems" :key="item.label">
        <!-- 普通导航项 -->
        <a v-if="!item.children" href="#" @click.prevent="currentView = item.view!"
          :class="currentView === item.view ? 'bg-accent/10 text-accent border-accent/20' : 'text-muted-foreground hover:bg-muted/50 border-transparent hover:text-foreground'"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium shadow-sm transition-colors border">
          <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" /></svg>
          <span class="text-sm shrink-0">{{ item.label }}</span>
        </a>

        <!-- 可展开的分组 -->
        <div v-else>
          <a href="#" @click.prevent="toggleGroup(item.label)"
            class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium shadow-sm transition-colors border"
            :class="groupActiveClass(item)">
            <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" /></svg>
            <span class="text-sm shrink-0 flex-1">{{ item.label }}</span>
            <svg class="w-4 h-4 transition-transform duration-200" :class="{ 'rotate-90': expandedGroups[item.label] }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </a>

          <!-- 子菜单 -->
          <div v-show="expandedGroups[item.label]" class="mt-0.5 space-y-0.5 relative pl-7">
            <div class="absolute left-[18px] top-1 bottom-1 w-px bg-gradient-to-b from-blue-300/50 to-blue-100/20"></div>
            <a v-for="child in item.children!" :key="child.label"
              href="#" @click.prevent="currentView = child.view!"
              :class="currentView === child.view ? 'bg-accent/10 text-accent border-accent/20' : 'text-muted-foreground hover:bg-muted/50 border-transparent hover:text-foreground'"
              class="flex items-center gap-3 px-3 py-2 rounded-lg font-medium transition-colors border text-sm relative">
              <div class="absolute left-[-17px] top-1/2 w-[14px] h-px bg-gradient-to-r from-blue-300/50 to-transparent"></div>
              <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="child.icon" /></svg>
              <span class="text-xs shrink-0">{{ child.label }}</span>
            </a>
          </div>
        </div>
      </template>
    </nav>

    <div class="p-4 border-t border-border/40 w-64">
      <div class="flex items-center gap-3 px-3 py-2 rounded-xl bg-muted/50 border border-border/50">
        <span class="relative flex h-2 w-2 shrink-0">
          <span v-if="status == 'running'" class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
          <span v-else-if="status == 'checking'" class="relative inline-flex rounded-full h-2 w-2 bg-yellow-500 animate-pulse"></span>
          <span v-else class="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
        </span>
        <span class="text-xs font-mono text-muted-foreground shrink-0">系统状态: {{ sidebarStatusText }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, reactive, computed, inject } from 'vue'
import type { Ref } from 'vue'
import { useServiceStatus } from '../../composables/useServiceStatus'

const { status } = useServiceStatus()

const sidebarStatusText = computed(() => {
  if (status.value == 'running') return '运行中'
  if (status.value == 'checking') return '检测中...'
  return '未运行'
})

const appName = ref('追溯应用')
const isSidebarOpen = inject<Ref<boolean>>('isSidebarOpen', ref(true))
const isMobile = inject<Ref<boolean>>('isMobile', ref(false))
const currentView = inject<Ref<string>>('currentView', ref('home'))

const expandedGroups = reactive<Record<string, boolean>>({})

const toggleGroup = (label: string) => {
  expandedGroups[label] = !expandedGroups[label]
}

const groupActiveClass = (group: any) => {
  const active = group.children?.some((c: any) => currentView.value == c.view)
  return active ? 'bg-accent/10 text-accent border-accent/20' : 'text-muted-foreground hover:bg-muted/50 border-transparent hover:text-foreground'
}

interface NavItem {
  view?: string
  label: string
  icon: string
  children?: NavItem[]
}

const navItems: NavItem[] = [
  { view: 'home', label: '首页', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { view: 'history', label: '追溯查询', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
  { view: 'report_query', label: '报工查询', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' },
  { view: 'unqualified_reason', label: '报工不合格原因', icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' },
  { view: 'material_scan_query', label: '扫码登料查询', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2m-6 0a2 2 0 104 0m-4 0a2 2 0 114 0m-7 8h2m2 0h6m-8 4h8' },
  { view: 'device_data', label: '数采查询', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  {
    label: '智能看板',
    icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    children: [
      { view: 'dashboard', label: '看板', icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
      { view: 'dashboard_settings', label: '设置', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
    ],
  },
  {
    label: '智能看板2',
    icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    children: [
      { view: 'dashboard2', label: '看板', icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
      { view: 'dashboard2_settings', label: '设置', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
    ],
  },
]
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #E2E8F0; border-radius: 20px; }
</style>
