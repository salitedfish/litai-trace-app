<template>
  <header class="h-16 w-full px-4 md:px-8 flex items-center justify-between relative z-20 border-b border-border/40 bg-white/40 backdrop-blur-md">
    <div class="flex items-center gap-4 text-sm font-medium text-muted-foreground">
      <button @click="toggleSidebar" class="p-2 -ml-3 rounded-lg hover:bg-muted/50 text-muted-foreground hover:text-foreground transition-colors border border-transparent hover:border-border/50">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" v-if="!isSidebarOpen" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" v-else />
        </svg>
      </button>
      <div class="h-5 w-px bg-border/60"></div>
      <span class="text-foreground text-lg font-bold truncate">{{ pageTitle }}</span>
    </div>

    <div class="flex items-center gap-5">
      <button @click="gotoPortal" class="flex items-center gap-2 text-muted-foreground hover:text-accent transition-colors p-2 rounded-lg hover:bg-accent/10 border border-transparent hover:border-accent/20" title="返回门户">
        <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        <span class="text-xs font-bold uppercase tracking-widest font-mono hidden md:block">返回门户</span>
      </button>

      <div class="w-px h-5 bg-border/60 hidden md:block"></div>

      <div class="flex items-center gap-4">
        <div class="flex items-center gap-3 cursor-pointer group">
          <span class="text-sm font-bold text-foreground group-hover:text-accent transition-colors hidden md:block">{{ userName }}</span>
          <div class="w-8 h-8 shrink-0 rounded-full bg-muted border border-border group-hover:border-accent transition-colors overflow-hidden flex items-center justify-center shadow-sm">
            <svg class="w-4 h-4 text-muted-foreground group-hover:text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
          </div>
        </div>

        <button @click="logout" class="p-2 -mr-2 rounded-lg text-muted-foreground hover:text-red-500 hover:bg-red-50 transition-colors border border-transparent hover:border-red-100" title="退出登录">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { inject, ref, computed, onMounted } from 'vue'
import type { Ref } from 'vue'
import { showConfirm } from '../../utils/dialog'

const isSidebarOpen = inject<Ref<boolean>>('isSidebarOpen', ref(true))
const currentView = inject<Ref<string>>('currentView', ref('home'))

const pageTitle = computed(() => {
  const titleMap: Record<string, string> = {
    home: '追溯应用',
    history: '追溯查询',
    device_data: '数采查询',
  }
  return titleMap[currentView.value] || '追溯应用'
})

const userName = ref('登录用户')

onMounted(() => {
  try {
    const loginName = document.cookie
      .split(';')
      .map(cookie => cookie.trim().split('='))
      .find(([key]) => key == 'login_name')
    if (loginName?.[1]) {
      userName.value = decodeURIComponent(loginName.slice(1).join('='))
    }
  } catch (e) {
    console.warn('获取登录用户名失败', e)
  }
})

const getBasePrefix = () => {
  const path = window.location.pathname
  const appName = 'trace_app'
  const appIndex = path.indexOf(`/${appName}`)
  if (appIndex > 0) {
    return path.substring(0, appIndex)
  }
  return ''
}

const toggleSidebar = () => {
  if (isSidebarOpen) {
    isSidebarOpen.value = !isSidebarOpen.value
  }
}

const gotoPortal = () => {
  const origin = window.location.origin
  location.href = `${origin}${getBasePrefix()}/portal/#/main`
}

const logout = async () => {
  if (await showConfirm('确定要退出当前账号吗？', '退出确认')) {
    const keysToRemove = []
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i)
      if (k && (k.toLowerCase().includes('token') || k.toLowerCase().includes('user'))) {
        keysToRemove.push(k)
      }
    }
    keysToRemove.forEach(k => localStorage.removeItem(k))

    const logoutValidFields = ['login_nickname', 'login_name', 'login_uuid', 'token']
    const path = window.location.pathname
    const appName = 'trace_app'
    const appIndex = path.indexOf(`/${appName}`)
    let prefix = ''
    if (appIndex > 0) {
      prefix = path.substring(0, appIndex)
    }

    logoutValidFields.forEach(field => {
      document.cookie = `${field}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`
      if (prefix) {
        document.cookie = `${field}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=${prefix}`
      }
    })

    window.location.reload()
  }
}
</script>
