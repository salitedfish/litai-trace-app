<template>
  <transition name="modal-fade">
    <div v-if="visible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm overflow-hidden transform transition-all p-6 border border-border">
        <h3 class="text-lg font-bold text-foreground mb-2">{{ title || '提示' }}</h3>
        <p class="text-sm text-muted-foreground mb-6 leading-relaxed">{{ message }}</p>

        <div class="flex justify-end gap-3">
          <button @click="handleCancel" class="px-4 py-2.5 text-sm font-medium text-foreground bg-muted hover:bg-border rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-accent/50">
            取消
          </button>
          <button @click="handleConfirm" class="px-4 py-2.5 text-sm font-medium text-white bg-accent hover:bg-accent/90 rounded-lg transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-accent/50">
            确定
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{
  title?: string
  message: string
  onResolve: (value: boolean) => void
  onClose: () => void
}>()

const visible = ref(false)

onMounted(() => {
  visible.value = true
})

const handleConfirm = () => {
  visible.value = false
  setTimeout(() => {
    props.onResolve(true)
    props.onClose()
  }, 200)
}

const handleCancel = () => {
  visible.value = false
  setTimeout(() => {
    props.onResolve(false)
    props.onClose()
  }, 200)
}
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-active > div,
.modal-fade-leave-active > div {
  transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.modal-fade-enter-from > div {
  transform: scale(0.95);
}
.modal-fade-leave-to > div {
  transform: scale(0.95);
}
</style>
