<template>
  <!--
    图片查看视口：支持「以光标/双指中点为锚点」的缩放 + 按住自由拖动。

    为什么需要它：直接用 `transform: scale()` 放大图片是**不会撑开容器**的
    （transform 不参与布局），外层再写 overflow-hidden 就变成「放大后从中心往外溢、
    被裁掉，只能看中间」。这里把图片绝对定位到视口中心，自己维护平移量并按边界钳制，
    所以放大后能拖到任意角落、拖到边就停。

    用法（外层必须有确定尺寸，组件会填满它）：
      <div class="w-full h-[45vh] overflow-hidden">
        <PanZoomImage :src="url" />
      </div>
  -->
  <div
    ref="rootRef"
    class="relative w-full h-full overflow-hidden select-none"
    :style="{ touchAction: 'none', cursor: cursorStyle }"
    @wheel.prevent="onWheel"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointercancel="onPointerUp"
    @dblclick="onDblClick"
  >
    <img
      v-if="src && !loadFailed"
      ref="imgRef"
      :src="src"
      :alt="alt"
      draggable="false"
      class="absolute left-1/2 top-1/2 max-w-none origin-center"
      :class="smooth ? 'transition-transform duration-150 ease-out' : ''"
      :style="imgStyle"
      @load="onImgLoad"
      @error="loadFailed = true"
      @dragstart.prevent
    />

    <!-- 加载中 -->
    <div v-if="src && !ready && !loadFailed" class="absolute inset-0 flex items-center justify-center gap-2 text-sm text-muted-foreground">
      <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
      图片加载中...
    </div>

    <!-- 加载失败（图片跨服务取，失败时不能留一片空白） -->
    <div v-else-if="src && loadFailed" class="absolute inset-0 flex items-center justify-center text-sm text-muted-foreground">
      图片加载失败
    </div>

    <!-- 无图占位 -->
    <div v-else-if="!src" class="absolute inset-0 flex items-center justify-center text-sm text-muted-foreground">
      <slot name="empty">暂无图片</slot>
    </div>

    <!-- 悬浮工具条：overlay 浮在图片上；compact 用于小图（如两张图并排对比） -->
    <div
      v-if="toolbar && src && ready"
      class="absolute left-1/2 -translate-x-1/2 flex items-center bg-white/95 border border-border/60 shadow-lg rounded-full z-10"
      :class="compact ? 'bottom-3 gap-1 px-2.5 py-1' : 'bottom-6 gap-2 px-4 py-2'"
      @pointerdown.stop
      @dblclick.stop
    >
      <button
        type="button"
        :class="btnClass"
        title="缩小"
        @click="withSmooth(() => zoomBy(1 / 1.25))"
      >
        <svg :class="iconClass" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" /></svg>
      </button>
      <span class="text-xs font-bold text-center text-muted-foreground" :class="compact ? 'w-10' : 'w-12'">{{ Math.round(scale * 100) }}%</span>
      <button
        type="button"
        :class="btnClass"
        title="放大"
        @click="withSmooth(() => zoomBy(1.25))"
      >
        <svg :class="iconClass" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" /></svg>
      </button>

      <template v-if="rotateEnabled">
        <div class="w-px bg-border mx-1" :class="compact ? 'h-4' : 'h-5'"></div>
        <button
          type="button"
          :class="btnClass"
          title="逆时针旋转"
          @click="withSmooth(() => rotateBy(-90))"
        >
          <svg :class="iconClass" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" /></svg>
        </button>
        <button
          type="button"
          :class="btnClass"
          title="顺时针旋转"
          @click="withSmooth(() => rotateBy(90))"
        >
          <svg :class="iconClass" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 10h-10a8 8 0 00-8 8v2M21 10l-6 6m6-6l-6-6" /></svg>
        </button>
      </template>

      <div class="w-px bg-border mx-1" :class="compact ? 'h-4' : 'h-5'"></div>
      <button
        type="button"
        :class="btnClass"
        title="还原（适应窗口）"
        @click="withSmooth(reset)"
      >
        <svg :class="iconClass" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { CSSProperties } from 'vue'

const props = withDefaults(defineProps<{
  src?: string          // 图片地址（objectURL / data-url / http 均可）
  alt?: string
  minScale?: number     // 最小缩放（相对「适应窗口」的倍数）
  maxScale?: number     // 最大缩放
  toolbar?: boolean     // 是否显示悬浮工具条
  compact?: boolean     // 紧凑工具条（小图场景）
  rotateEnabled?: boolean
}>(), {
  src: '',
  alt: '',
  minScale: 0.1,
  maxScale: 8,
  toolbar: true,
  compact: false,
  rotateEnabled: true
})

const rootRef = ref<HTMLElement | null>(null)
const imgRef = ref<HTMLImageElement | null>(null)

// scale 是**相对「适应窗口」的倍数**：1 = 整张图刚好塞进视口
const scale = ref(1)
const rotate = ref(0)
const panX = ref(0)   // 平移量，屏幕像素；相对视口中心
const panY = ref(0)

const naturalW = ref(0)
const naturalH = ref(0)
const viewW = ref(0)
const viewH = ref(0)
const ready = ref(false)       // 图片已加载且视口尺寸已知
const loadFailed = ref(false)
const dragging = ref(false)
const smooth = ref(false)      // 按钮操作时开过渡；滚轮/拖动/捏合时关掉，否则发飘

const btnClass = computed(() => [
  'hover:bg-accent hover:text-white rounded-full text-muted-foreground transition-all',
  props.compact ? 'p-1.5' : 'p-2'
].join(' '))
const iconClass = computed(() => (props.compact ? 'w-4 h-4' : 'w-5 h-5'))

const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v))

// 转 90/270 度时，宽高在视觉上互换
const quarterTurn = computed(() => {
  const r = ((rotate.value % 360) + 360) % 360
  return r === 90 || r === 270
})

// 基础显示尺寸：按「旋转后的外接框」塞进视口
// —— 带上旋转一起算，是为了让图片转 90 度后仍然整张看得见，而不是溢出
const baseSize = computed(() => {
  if (!naturalW.value || !naturalH.value || !viewW.value || !viewH.value) {
    return { w: 0, h: 0 }
  }
  const effW = quarterTurn.value ? naturalH.value : naturalW.value
  const effH = quarterTurn.value ? naturalW.value : naturalH.value
  const fit = Math.min(viewW.value / effW, viewH.value / effH)
  return { w: naturalW.value * fit, h: naturalH.value * fit }
})

// 平移边界：只有放大到超出视口才允许拖，且拖到边就停（不会把图拖飞）
const panLimit = computed(() => {
  const { w, h } = baseSize.value
  const dispW = w * scale.value
  const dispH = h * scale.value
  const outerW = quarterTurn.value ? dispH : dispW
  const outerH = quarterTurn.value ? dispW : dispH
  return {
    x: Math.max(0, (outerW - viewW.value) / 2),
    y: Math.max(0, (outerH - viewH.value) / 2)
  }
})

const clampPan = () => {
  const lim = panLimit.value
  panX.value = clamp(panX.value, -lim.x, lim.x)
  panY.value = clamp(panY.value, -lim.y, lim.y)
}

// 显式标注 CSSProperties：visibility 的联合类型不接受裸 string
const imgStyle = computed<CSSProperties>(() => ({
  width: baseSize.value.w ? `${baseSize.value.w}px` : 'auto',
  height: baseSize.value.h ? `${baseSize.value.h}px` : 'auto',
  visibility: ready.value ? 'visible' : 'hidden',
  willChange: 'transform',
  transform:
    `translate(-50%, -50%) translate(${panX.value}px, ${panY.value}px) ` +
    `rotate(${rotate.value}deg) scale(${scale.value})`
}))

const cursorStyle = computed(() => {
  if (!ready.value) return 'default'
  if (dragging.value) return 'grabbing'
  const lim = panLimit.value
  return lim.x > 0.5 || lim.y > 0.5 ? 'grab' : 'default'
})

const measure = () => {
  const root = rootRef.value
  if (!root) return
  viewW.value = root.clientWidth
  viewH.value = root.clientHeight
  if (naturalW.value && naturalW.value > 0) ready.value = true
  clampPan()
}

const reset = () => {
  scale.value = 1
  rotate.value = 0
  panX.value = 0
  panY.value = 0
}

/**
 * 以视口内的某个点为锚点缩放到 next。
 * cx/cy 是「相对视口中心」的屏幕偏移。
 *
 * 推导：图片上一点 p 映射到屏幕为  screen = center + pan + R(rot)·(s·p)
 * 要让光标下的那个像素点不动，解得  pan' = w − k·(w − pan)（w 为光标偏移，k = s'/s）。
 * 注意这个式子**与旋转角无关** —— 因为平移在旋转之前施加、且两者同绕视口中心，
 * 所以带旋转时依然成立，不需要额外补偿。
 */
const zoomAt = (cx: number, cy: number, next: number) => {
  const s = clamp(next, props.minScale, props.maxScale)
  if (!ready.value || s === scale.value) return
  const k = s / scale.value
  panX.value = cx - k * (cx - panX.value)
  panY.value = cy - k * (cy - panY.value)
  scale.value = s
  clampPan()
}

// 按钮缩放以视口中心为锚点
const zoomBy = (factor: number) => zoomAt(0, 0, scale.value * factor)

const rotateBy = (deg: number) => {
  rotate.value += deg
  // 转过 90 度后基础尺寸会重算，旧的平移量已无意义，回到居中
  panX.value = 0
  panY.value = 0
  clampPan()
}

let smoothTimer: number | undefined
const withSmooth = (fn: () => void) => {
  smooth.value = true
  fn()
  window.clearTimeout(smoothTimer)
  smoothTimer = window.setTimeout(() => { smooth.value = false }, 180)
}

const onImgLoad = () => {
  const img = imgRef.value
  if (!img) return
  loadFailed.value = false
  naturalW.value = img.naturalWidth
  naturalH.value = img.naturalHeight
  reset()
  measure()
}

const onWheel = (e: WheelEvent) => {
  const root = rootRef.value
  if (!root || !ready.value) return
  const rect = root.getBoundingClientRect()
  const cx = e.clientX - rect.left - rect.width / 2
  const cy = e.clientY - rect.top - rect.height / 2
  zoomAt(cx, cy, scale.value * (e.deltaY < 0 ? 1.15 : 1 / 1.15))
}

const onDblClick = (e: MouseEvent) => {
  const root = rootRef.value
  if (!root || !ready.value) return
  if (scale.value > 1.01) {
    withSmooth(reset)
    return
  }
  const rect = root.getBoundingClientRect()
  withSmooth(() => zoomAt(
    e.clientX - rect.left - rect.width / 2,
    e.clientY - rect.top - rect.height / 2,
    2.5
  ))
}

// ========== 指针（鼠标 / 触屏 / 笔 统一走 Pointer Events）==========
const pointers = new Map<number, { x: number, y: number }>()
let dragFrom: { x: number, y: number } | null = null
let pinchFrom: { dist: number, scale: number, panX: number, panY: number, midX: number, midY: number } | null = null

const localCenter = () => {
  const rect = rootRef.value!.getBoundingClientRect()
  return { left: rect.left, top: rect.top, cx: rect.left + rect.width / 2, cy: rect.top + rect.height / 2 }
}

const beginPinch = () => {
  const root = rootRef.value
  if (!root) return
  const [a, b] = [...pointers.values()]
  const { cx, cy } = localCenter()
  pinchFrom = {
    dist: Math.hypot(a.x - b.x, a.y - b.y) || 1,
    scale: scale.value,
    panX: panX.value,
    panY: panY.value,
    midX: (a.x + b.x) / 2 - cx,
    midY: (a.y + b.y) / 2 - cy
  }
  dragging.value = false
  dragFrom = null
}

const onPointerDown = (e: PointerEvent) => {
  const root = rootRef.value
  if (!root || !ready.value) return
  if (e.pointerType === 'mouse' && e.button !== 0) return   // 只认左键
  try { root.setPointerCapture(e.pointerId) } catch { /* 某些环境不支持，忽略 */ }

  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY })
  if (pointers.size === 1) {
    dragging.value = true
    dragFrom = { x: e.clientX, y: e.clientY }
    pinchFrom = null
  } else if (pointers.size === 2) {
    beginPinch()
  }
}

const onPointerMove = (e: PointerEvent) => {
  if (!pointers.has(e.pointerId)) return
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY })

  // 单指/鼠标：平移。平移量在屏幕坐标系，与旋转无关，所以直接加增量即可
  if (pointers.size === 1 && dragging.value && dragFrom) {
    panX.value += e.clientX - dragFrom.x
    panY.value += e.clientY - dragFrom.y
    dragFrom = { x: e.clientX, y: e.clientY }
    clampPan()
    return
  }

  // 双指：捏合缩放 + 跟随中点移动
  if (pointers.size === 2 && pinchFrom) {
    const [a, b] = [...pointers.values()]
    const { cx, cy } = localCenter()
    const dist = Math.hypot(a.x - b.x, a.y - b.y) || 1
    const midX = (a.x + b.x) / 2 - cx
    const midY = (a.y + b.y) / 2 - cy

    const s = clamp(pinchFrom.scale * (dist / pinchFrom.dist), props.minScale, props.maxScale)
    const k = s / pinchFrom.scale
    // 与 zoomAt 同一套锚点公式，只是锚点换成双指中点、并以捏合起始态为基准
    panX.value = midX - k * (pinchFrom.midX - pinchFrom.panX)
    panY.value = midY - k * (pinchFrom.midY - pinchFrom.panY)
    scale.value = s
    clampPan()
  }
}

const onPointerUp = (e: PointerEvent) => {
  if (!pointers.has(e.pointerId)) return
  pointers.delete(e.pointerId)
  const root = rootRef.value
  if (root) {
    try { root.releasePointerCapture(e.pointerId) } catch { /* 已自动释放，忽略 */ }
  }

  if (pointers.size === 0) {
    dragging.value = false
    dragFrom = null
    pinchFrom = null
  } else if (pointers.size === 1) {
    // 从双指松到单指：把拖拽基准接到剩下那根手指上，避免画面跳一下
    const p = [...pointers.values()][0]
    dragging.value = true
    dragFrom = { x: p.x, y: p.y }
    pinchFrom = null
  }
}

// ========== 生命周期 ==========
let ro: ResizeObserver | null = null

onMounted(() => {
  measure()
  if (typeof ResizeObserver !== 'undefined') {
    ro = new ResizeObserver(measure)
    if (rootRef.value) ro.observe(rootRef.value)
  }
  // 图片可能在上面的监听挂上之前就已加载完（缓存命中），补一次
  nextTick(() => {
    const img = imgRef.value
    if (img && img.complete && img.naturalWidth) onImgLoad()
  })
})

onBeforeUnmount(() => {
  ro?.disconnect()
  ro = null
  window.clearTimeout(smoothTimer)
})

watch(() => props.src, () => {
  naturalW.value = 0
  naturalH.value = 0
  ready.value = false
  loadFailed.value = false
  reset()
  nextTick(() => {
    const img = imgRef.value
    if (img && img.complete && img.naturalWidth) onImgLoad()
  })
})
</script>
