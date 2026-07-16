<template>
  <div class="flex h-screen overflow-hidden bg-background dot-pattern relative">
    <Sidebar />

    <div v-if="isMobile && isSidebarOpen" @click="isSidebarOpen = false" class="fixed inset-0 z-40 bg-foreground/40 backdrop-blur-sm transition-opacity md:hidden"></div>

    <div class="flex flex-col flex-1 relative z-10 w-full overflow-hidden">
      <Header />
      <main class="flex-1 w-full px-6 overflow-y-auto custom-scrollbar relative z-10 flex flex-col">
        <HomeView v-if="currentView === 'home'" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, provide, onMounted, onUnmounted } from 'vue'
import Sidebar from './components/layout/Sidebar.vue'
import Header from './components/layout/Header.vue'
import HomeView from './views/HomeView.vue'
import { registerServiceWorker } from './registerServiceWorker'

const isSidebarOpen = ref(true)
const isMobile = ref(false)
const currentView = ref('home')

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
