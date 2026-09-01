<template>
  <div
    ref="wrapRef"
    class="seamless-scroll"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
  >
    <!-- 双份内容无缝衔接：滚完第一份后跳回顶部，第二份已接上，跳回不可见 -->
    <div
      ref="trackRef"
      class="seamless-track"
    >
      <div
        v-for="copy in copyCount"
        :key="copy"
        class="seamless-item"
      >
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, onUpdated, ref } from 'vue'

/**
 * 通用"单步式"无缝循环滚动组件：每 moveMs 平滑滚一行、停 waitMs，合计约 2 秒一行。
 * 相比连续匀速滚动：每次位移正好一行（整数像素，无亚像素抖动），滚动有缓动过渡、其余时间静止，
 * 低端设备上更丝滑、更省电。
 * 内容经默认 slot 传入；容器高度由使用方通过 class 控制（如 flex-1 min-h-0）。
 * 注意：
 *  - 滚动内容项不要使用 margin（两份内容接缝会跳变），用 padding 代替
 *  - 行高需为整数（内容行 line-height 用整数 px），保证到位时像素对齐不抖动
 */
const props = withDefaults(defineProps<{
  /** 每滚一行的动画时长（ms），默认 600 */
  moveMs?: number
  /** 每行到位后的停留时长（ms），默认 1400（moveMs + waitMs = 2000 ≈ 2 秒一行） */
  waitMs?: number
  /** 鼠标悬停是否暂停滚动（默认开启，方便人工查看） */
  hover?: boolean
}>(), {
  moveMs: 600,
  waitMs: 1400,
  hover: true,
})

const wrapRef = ref<HTMLDivElement | null>(null)
const trackRef = ref<HTMLDivElement | null>(null)
// 内容是否超出可视高度：超出才滚动（不足一屏静止显示，避免露白）
const needScroll = ref(false)
// 需要滚动时渲染双份内容（无缝衔接），否则单份静止
const copyCount = computed(() => (needScroll.value ? 2 : 1))

// 行高（px，由测量取整保证整数）与总行数
let rowH = 0
let totalRows = 0
// 当前滚到的行序
let currentRow = 0
// 定时器句柄
let timerId = 0
// 悬停暂停标志
let paused = false

// 滚动一行时的过渡动画（缓入缓出更柔和）
const TRACK_TRANSITION = `transform ${props.moveMs}ms ease-in-out`

/** 单步：平滑滚过一行（到位后停 waitMs，由定时器节奏控制） */
function nextStep() {
  currentRow++
  const track = trackRef.value
  if (!track || !needScroll.value || paused) return
  // 滚完第一份（totalRows 行），跳回顶部重新开始——双份内容使跳回不可见
  if (currentRow >= totalRows) {
    track.style.transition = 'none'
    track.style.transform = 'translateY(0px)'
    // 强制回流，确保瞬跳先完成，再恢复过渡滚动下一轮
    void track.offsetHeight
    currentRow = 0
  }
  track.style.transition = TRACK_TRANSITION
  track.style.transform = `translateY(${-(currentRow * rowH)}px)`
}

function startLoop() {
  stopLoop()
  if (!needScroll.value || paused) return
  timerId = window.setInterval(nextStep, props.moveMs + props.waitMs)
}

function stopLoop() {
  if (timerId) {
    clearInterval(timerId)
    timerId = 0
  }
}

/** 重置回顶部并从零开始（数据更新后调用） */
function reset() {
  const track = trackRef.value
  if (track) {
    track.style.transition = 'none'
    track.style.transform = 'translateY(0px)'
  }
  currentRow = 0
  startLoop()
}

let measureTimer = 0

/** 测量内容高度与行高：决定是否滚动，并重置循环。数据变化时由 onUpdated 自动触发 */
function measure() {
  // 节流：同一轮渲染多次更新只测一次
  if (measureTimer) return
  measureTimer = window.setTimeout(() => {
    measureTimer = 0
    nextTick(() => {
      const el = wrapRef.value
      if (!el) return
      const item = el.querySelector('.seamless-item') as HTMLElement | null
      const h = item ? item.offsetHeight : 0
      const rowEl = item ? (item.querySelector('tbody tr') as HTMLElement | null) : null
      const rows = item ? item.querySelectorAll('tbody tr').length : 0
      rowH = rowEl ? rowEl.offsetHeight : 0
      totalRows = rows
      // 内容高度超过可视高度才滚动（+1 容差）
      needScroll.value = h > el.clientHeight + 1
      reset()
    })
  }, 0)
}

function onMouseEnter() {
  if (!props.hover) return
  paused = true
  stopLoop()
}

function onMouseLeave() {
  if (!props.hover) return
  paused = false
  startLoop()
}

onMounted(measure)
onUpdated(measure)

onUnmounted(() => {
  stopLoop()
  if (measureTimer) {
    clearTimeout(measureTimer)
    measureTimer = 0
  }
})
</script>

<style scoped>
/* 容器：内容溢出隐藏，高度由使用方通过 class 控制（如 flex-1 min-h-0） */
.seamless-scroll {
  overflow: hidden;
}

/* 滚动轨道：双份内容纵向堆叠，transform 由 JS 逐步驱动 */
.seamless-track {
  will-change: transform;
}
</style>
