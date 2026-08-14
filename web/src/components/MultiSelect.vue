<template>
  <div class="relative w-full min-w-0" ref="containerRef">
    <div
      @click="toggleDropdown"
      :class="[
        'w-full flex items-center justify-between px-4 py-2.5 rounded-lg text-sm transition-all cursor-pointer border min-w-0 overflow-hidden',
        disabled
          ? 'opacity-50 cursor-not-allowed bg-white border-border/50'
          : (isOpen ? 'bg-white border-accent ring-1 ring-accent' : 'bg-white border-border hover:border-accent/50')
      ]"
    >
      <span :class="['block min-w-0 flex-1 truncate', modelValue.length == 0 ? 'text-muted-foreground' : 'text-foreground']">
        {{ displayText }}
      </span>
      <svg
        class="w-4 h-4 text-muted-foreground transition-transform duration-200 shrink-0 ml-2"
        :class="{ 'rotate-180': isOpen }"
        fill="none" viewBox="0 0 24 24" stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </div>

    <transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <div v-if="isOpen && !disabled" class="absolute z-[100] w-full mt-1.5 bg-white border border-border/60 rounded-xl shadow-xl overflow-hidden">
        <ul class="max-h-60 overflow-auto py-1 custom-scrollbar">
          <li v-if="options.length == 0" class="px-3 py-3 text-sm text-muted-foreground text-center">无数据</li>
          <li
            v-for="opt in options"
            :key="opt.value"
            @click="toggleSelect(opt)"
            :class="[
              'px-3 py-2.5 text-sm cursor-pointer transition-colors flex items-center justify-between',
              isSelected(opt.value) ? 'bg-accent/10 text-accent font-bold' : 'text-foreground hover:bg-muted/50'
            ]"
          >
            <span class="truncate block flex-1" :title="opt.label">{{ opt.label }}</span>
            <svg v-if="isSelected(opt.value)" class="w-4 h-4 text-accent shrink-0 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
            </svg>
          </li>
        </ul>
        <div v-if="modelValue.length > 0" class="p-2 border-t border-border/40 flex justify-end">
          <button class="text-xs text-muted-foreground hover:text-accent transition-colors" @click="clear">清空</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: (string | number)[]
  options: { label: string, value: string | number }[]
  placeholder?: string
  disabled?: boolean
}>(), {
  placeholder: '请选择...',
  disabled: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: (string | number)[]): void
  (e: 'change', value: (string | number)[]): void
}>()

const isOpen = ref(false)
const containerRef = ref<HTMLElement | null>(null)

const displayText = computed(() => {
  if (props.modelValue.length == 0) return props.placeholder
  if (props.modelValue.length == 1) {
    const opt = props.options.find(o => o.value == props.modelValue[0])
    return opt ? opt.label : props.placeholder
  }
  return `已选 ${props.modelValue.length} 项`
})

const isSelected = (value: string | number) => {
  return props.modelValue.includes(value)
}

const toggleDropdown = () => {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

const toggleSelect = (opt: { label: string, value: string | number }) => {
  const list = isSelected(opt.value)
    ? props.modelValue.filter(v => v != opt.value)
    : [...props.modelValue, opt.value]
  emit('update:modelValue', list)
  emit('change', list)
}

const clear = () => {
  emit('update:modelValue', [])
  emit('change', [])
}

const handleClickOutside = (e: MouseEvent) => {
  if (containerRef.value && !containerRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})
</script>
