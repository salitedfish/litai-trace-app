<template>
  <div class="relative w-full min-w-0" ref="containerRef">
    <div
      @click="toggleDropdown"
      :class="[
        'w-full flex items-center justify-between px-4 py-2.5 rounded-lg text-sm transition-all cursor-pointer border min-w-0 overflow-hidden',
        variant === 'solid'
          ? (disabled ? 'opacity-50 cursor-not-allowed bg-muted/80 border-transparent' : (isOpen ? 'bg-white border-accent ring-1 ring-accent' : 'bg-muted/80 hover:bg-white border-transparent hover:border-border'))
          : (disabled ? 'opacity-50 cursor-not-allowed bg-white border-border/50' : (isOpen ? 'bg-white border-accent ring-1 ring-accent' : 'bg-white border-border hover:border-accent/50'))
      ]"
    >
      <span :class="['block min-w-0 flex-1 truncate', !selectedOption ? 'text-muted-foreground' : 'text-foreground']">
        {{ selectedOption ? selectedOption.label : placeholder }}
      </span>
      <!-- 清空按钮（clearable 且有值时显示） -->
      <svg
        v-if="clearable && modelValue !== '' && !disabled"
        class="w-4 h-4 text-muted-foreground hover:text-foreground cursor-pointer shrink-0 ml-2"
        fill="none" viewBox="0 0 24 24" stroke="currentColor"
        @click.stop="handleClear"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
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
      <div
        v-if="isOpen && !disabled"
        class="absolute z-[100] w-full mt-1.5 bg-white border border-border/60 rounded-xl shadow-xl overflow-hidden"
      >
        <!-- 搜索输入框 -->
        <div v-if="searchable" class="p-2 border-b border-border/40">
          <input ref="searchInputRef" v-model="searchText" type="text" placeholder="输入关键词筛选..."
            class="w-full px-3 py-1.5 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all"
            @click.stop @keydown.esc="isOpen = false" />
        </div>
        <ul class="max-h-60 overflow-auto py-1 custom-scrollbar">
          <li
            v-if="filteredOptions.length == 0"
            class="px-3 py-3 text-sm text-muted-foreground text-center flex flex-col items-center gap-1"
          >
            <svg class="w-5 h-5 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
            {{ searchText ? '无匹配选项' : '无数据' }}
          </li>
          <li
            v-for="opt in filteredOptions"
            :key="opt.value"
            @click="selectOption(opt)"
            :class="[
              'px-3 py-2.5 text-sm cursor-pointer transition-colors flex items-center justify-between',
              modelValue === opt.value ? 'bg-accent/10 text-accent font-bold' : 'text-foreground hover:bg-muted/50'
            ]"
          >
            <span class="truncate block flex-1" :title="opt.label">{{ opt.label }}</span>
            <svg v-if="modelValue === opt.value" class="w-4 h-4 text-accent shrink-0 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
          </li>
        </ul>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: string | number
  options: { label: string, value: string | number }[]
  placeholder?: string
  disabled?: boolean
  variant?: 'solid' | 'outline'
  searchable?: boolean
  /** 是否显示清空按钮（点 ✕ 将值清空为 ''） */
  clearable?: boolean
}>(), {
  placeholder: '请选择...',
  disabled: false,
  variant: 'solid',
  searchable: false,
  clearable: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
  (e: 'change', value: string | number): void
}>()

const isOpen = ref(false)
const containerRef = ref<HTMLElement | null>(null)
const searchText = ref('')
const searchInputRef = ref<HTMLInputElement | null>(null)

const filteredOptions = computed(() => {
  if (!props.searchable || !searchText.value) return props.options
  const kw = searchText.value.toLowerCase()
  return props.options.filter(opt => opt.label.toLowerCase().includes(kw))
})

// 打开下拉时清空搜索关键词并自动聚焦
watch(isOpen, async (open) => {
  if (open) {
    searchText.value = ''
    await nextTick()
    searchInputRef.value?.focus()
  }
})

const selectedOption = computed(() => {
  return props.options.find(opt => opt.value === props.modelValue)
})

const toggleDropdown = () => {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

const selectOption = (opt: any) => {
  emit('update:modelValue', opt.value)
  emit('change', opt.value)
  isOpen.value = false
}

/** 点击清空按钮：值置空（占位展示），并通知父组件 */
const handleClear = () => {
  emit('update:modelValue', '')
  emit('change', '')
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
