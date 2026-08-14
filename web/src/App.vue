<template>
  <!-- 全屏看板模式 -->
  <DashboardView v-if="currentView === 'dashboard'" @exit="currentView = 'home'" />

  <!-- 正常布局 -->
  <div v-else class="flex h-screen overflow-hidden bg-background dot-pattern relative">
    <Sidebar />

    <div v-if="isMobile && isSidebarOpen" @click="isSidebarOpen = false" class="fixed inset-0 z-40 bg-foreground/40 backdrop-blur-sm transition-opacity md:hidden"></div>

    <div class="flex flex-col flex-1 relative z-10 w-full overflow-hidden">
      <Header />
      <main class="flex-1 w-full px-6 overflow-y-auto custom-scrollbar relative z-10 flex flex-col">
        <HomeView v-show="currentView === 'home'" />
        <TraceQueryView v-show="currentView === 'history'" />
        <DeviceDataView v-show="currentView === 'device_data'" />
        <DashboardSettingsView v-show="currentView === 'dashboard_settings'" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, provide, onMounted, onUnmounted, watch } from 'vue'
import Sidebar from './components/layout/Sidebar.vue'
import Header from './components/layout/Header.vue'
import HomeView from './views/HomeView.vue'
import TraceQueryView from './views/TraceQueryView.vue'
import DeviceDataView from './views/DeviceDataView.vue'
import DashboardView from './views/dashboard/DashboardView.vue'
import DashboardSettingsView from './views/dashboard/DashboardSettingsView.vue'
import { registerServiceWorker } from './registerServiceWorker'

const isSidebarOpen = ref(true)
const isMobile = ref(false)

// 当前视图持久化：刷新页面时保持当前页（sessionStorage 刷新保留、关闭会话清空）
const VIEW_STORAGE_KEY = 'trace_app_current_view'
const currentView = ref(sessionStorage.getItem(VIEW_STORAGE_KEY) || 'home')

watch(currentView, (view) => {
  sessionStorage.setItem(VIEW_STORAGE_KEY, view)
})

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    isSidebarOpen.value = false
  } else {
    isSidebarOpen.value = true
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  registerServiceWorker()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

provide('isSidebarOpen', isSidebarOpen)
provide('isMobile', isMobile)
provide('currentView', currentView)
</script>
