<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="visible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="close">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-6xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">检验单</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                {{ step?.procedure_name || '工序' }}
                <span v-if="step?.procedure_code" class="ml-1 font-mono">({{ step?.procedure_code }})</span>
                <span class="ml-2">产出: <code class="bg-muted px-1 py-0.5 rounded font-mono text-xs">{{ step?.qr_code }}</code></span>
              </p>
            </div>
            <div class="flex items-center gap-2">
              <span v-if="data && data.is_qualified != null"
                class="text-xs font-bold px-3 py-1 rounded-full"
                :class="data.is_qualified ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-600'">
                {{ data.is_qualified ? '整体合格' : '存在不合格项' }}
              </span>
              <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="close">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
          </div>
          <div class="overflow-auto flex-1 p-6">
            <div v-if="loading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-8">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              加载中...
            </div>
            <div v-else-if="error" class="text-sm text-red-500 py-4 text-center">{{ error }}</div>
            <div v-else-if="!data" class="text-sm text-muted-foreground py-8 text-center">该报工无检验单记录</div>
            <div v-else>
              <table class="w-full text-left border-collapse text-sm">
                <thead>
                  <tr class="border-b border-border/50 text-xs text-muted-foreground">
                    <th class="px-3 py-2.5 font-medium w-14 text-center">#</th>
                    <th class="px-3 py-2.5 font-medium">检验项名称</th>
                    <th class="px-3 py-2.5 font-medium w-28">类型</th>
                    <th class="px-3 py-2.5 font-medium w-36">数据范围</th>
                    <th class="px-3 py-2.5 font-medium">检验要求</th>
                    <th class="px-3 py-2.5 font-medium w-36">检验工具</th>
                    <th class="px-3 py-2.5 font-medium">填写值</th>
                    <th class="px-3 py-2.5 font-medium w-24 text-center">结果</th>
                    <th class="px-3 py-2.5 font-medium w-28">不合格原因</th>
                    <th class="px-3 py-2.5 font-medium w-28 text-center">图片</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border/30">
                  <tr v-for="(item, i) in items" :key="i" class="hover:bg-muted/30">
                    <td class="px-3 py-2.5 text-center text-muted-foreground">{{ i + 1 }}</td>
                    <td class="px-3 py-2.5">
                      <span class="font-medium">{{ item.item_name }}</span>
                      <span class="ml-1 font-mono text-[10px] text-muted-foreground">{{ item.item_code }}</span>
                    </td>
                    <td class="px-3 py-2.5">
                      <span class="text-xs" :class="item.inspect_type === 'range' ? 'text-amber-600' : 'text-blue-600'">{{ item.inspect_type === 'range' ? '数据范围' : '是否合格' }}</span>
                    </td>
                    <td class="px-3 py-2.5 font-mono text-xs">{{ item.range_value || '-' }}</td>
                    <td class="px-3 py-2.5 text-xs text-muted-foreground whitespace-normal break-words">{{ item.requirement || '-' }}</td>
                    <td class="px-3 py-2.5 text-xs text-muted-foreground whitespace-normal break-words">{{ item.tool || '-' }}</td>
                    <td class="px-3 py-2.5 font-mono text-xs">{{ item.input_value ?? '-' }}</td>
                    <td class="px-3 py-2.5 text-center">
                      <span class="text-xs font-medium" :class="item.is_qualified ? 'text-teal-600' : 'text-red-600'">{{ item.is_qualified ? '合格' : '不合格' }}</span>
                    </td>
                    <td class="px-3 py-2.5">
                      <button v-if="unqualifiedReasonCount(item) > 0"
                        class="px-2.5 py-1 rounded-md text-xs font-medium bg-red-50 text-red-600 hover:bg-red-100 border border-red-200 transition-colors"
                        @click="showUnqualifiedReasons(item)">查看原因 ({{ unqualifiedReasonCount(item) }})</button>
                      <span v-else class="text-xs text-muted-foreground">-</span>
                    </td>
                    <td class="px-3 py-2.5 text-center">
                      <button v-if="imageCount(item) > 0"
                        class="px-2.5 py-1 rounded-md text-xs font-medium bg-indigo-50 text-indigo-600 hover:bg-indigo-100 border border-indigo-200 transition-colors"
                        @click="showImages(item)">查看图片 ({{ imageCount(item) }})</button>
                      <span v-else class="text-xs text-muted-foreground">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div class="flex items-center justify-between mt-4 text-xs text-muted-foreground px-1">
                <span>操作人: {{ data.operator || '-' }}</span>
                <span>检验时间: {{ fmtTime(data.op_time) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>

  <!-- 不合格原因明细（本弹窗内逐项点击查看，z 高于检验单弹窗） -->
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="reasonVisible" class="fixed inset-0 z-[1100] flex items-center justify-center bg-black/30" @click.self="closeUnqualifiedReasons">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md max-h-[70vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-5 py-3.5 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">不合格原因</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                检验项: {{ reasonItem?.item_name || '-' }}
                <span v-if="reasonItem?.item_code" class="ml-1 font-mono">({{ reasonItem.item_code }})</span>
              </p>
            </div>
            <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeUnqualifiedReasons">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="overflow-auto p-5">
            <div v-if="reasonItem && unqualifiedReasonCount(reasonItem) > 0" class="space-y-2">
              <div v-for="(r, ri) in reasonItem.unqualified_reasons" :key="ri" class="flex items-center justify-between gap-3 rounded-lg border border-border/50 bg-muted/20 px-3 py-2">
                <span class="text-sm text-foreground">{{ r?.reason_name || r?.reason_code || '-' }}</span>
                <span v-if="r?.reason_code" class="font-mono text-[10px] text-muted-foreground">{{ r.reason_code }}</span>
              </div>
            </div>
            <p v-else class="text-sm text-muted-foreground text-center py-4">该检验项无不合格原因</p>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>

  <!-- 检验项图片：图片存 manual_line 服务器磁盘、DB 只存路径，经 manual_line 的
       download_image 接口（跨服务、与 mgDMS 下载同约定不加登录鉴权）按路径回显 -->
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="imageVisible" class="fixed inset-0 z-[1100] flex items-center justify-center bg-black/30" @click.self="closeImages">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-5 py-3.5 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">检验项图片</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                检验项: {{ imageItem?.item_name || '-' }}
                <span v-if="imageItem?.item_code" class="ml-1 font-mono">({{ imageItem.item_code }})</span>
              </p>
            </div>
            <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeImages">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="overflow-auto p-5">
            <div v-if="imageLoading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-10">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              图片加载中...
            </div>
            <div v-else>
              <div v-if="imageError" class="text-xs text-red-500 mb-3">{{ imageError }}</div>
              <div v-if="imageItem?.baseline_image" class="mb-5">
                <p class="text-xs font-bold text-muted-foreground mb-2">基准图片（档案配置）</p>
                <!-- 滚轮/双指以光标为锚点缩放，放大后按住可自由拖动 -->
                <div v-if="baselineUrl" class="w-full h-[45vh] rounded-lg border border-border/60 bg-muted/10 overflow-hidden">
                  <PanZoomImage :src="baselineUrl" alt="基准图片" compact />
                </div>
                <p v-else class="text-xs text-muted-foreground">基准图片加载失败或已不存在</p>
              </div>
              <div v-if="imageItem?.actual_image">
                <p class="text-xs font-bold text-muted-foreground mb-2">实际图片（报工上传）</p>
                <!-- 滚轮/双指以光标为锚点缩放，放大后按住可自由拖动 -->
                <div v-if="actualUrl" class="w-full h-[45vh] rounded-lg border border-border/60 bg-muted/10 overflow-hidden">
                  <PanZoomImage :src="actualUrl" alt="实际图片" compact />
                </div>
                <p v-else class="text-xs text-muted-foreground">实际图片加载失败或已不存在</p>
              </div>
              <p v-if="!imageItem?.baseline_image && !imageItem?.actual_image" class="text-sm text-muted-foreground text-center py-4">该检验项未上传图片</p>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import api from '../../api/trace-app'
import { _postBlob } from '../../api/httpWrap'
import { fmtTime } from '../../utils/trace-format'
import PanZoomImage from '../ui/PanZoomImage.vue'

const props = defineProps<{
  visible: boolean
  /** 报工记录（需含 workorder_code / procedure_name / procedure_code / qr_code） */
  step: any
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

const data = ref<any>(null)
const loading = ref(false)
const error = ref('')
const items = computed<any[]>(() => data.value?.items || [])

const load = async () => {
  loading.value = true
  error.value = ''
  data.value = null
  try {
    const res = await api.queryInspectionRecord(props.step?.workorder_code || '')
    data.value = res.data || null
  } catch (err: any) {
    error.value = '加载失败: ' + (err?.message || '未知错误')
  } finally {
    loading.value = false
  }
}

watch(() => [props.visible, props.step], () => {
  if (!props.visible) return
  load()
})

const close = () => {
  emit('update:visible', false)
  data.value = null
  error.value = ''
}

// ========== 不合格原因明细 ==========
// 某检验项选中的不合格原因条数（非数组/缺键按 0 计，0 = 无原因可看）
const unqualifiedReasonCount = (item: any) =>
  Array.isArray(item?.unqualified_reasons) ? item.unqualified_reasons.length : 0

const reasonVisible = ref(false)
const reasonItem = ref<any>(null)
const showUnqualifiedReasons = (item: any) => {
  reasonItem.value = item
  reasonVisible.value = true
}
const closeUnqualifiedReasons = () => {
  reasonVisible.value = false
  reasonItem.value = null
}

// ========== 检验项图片 ==========
const MANUAL_IMAGE_DOWNLOAD_URL = '/api/manual_line_general_traceability/inspection_item/download_image'

const readBlobText = (blob: Blob) => new Promise<string>((resolve, reject) => {
  const reader = new FileReader()
  reader.onerror = () => reject(new Error('读取响应失败'))
  reader.onload = () => resolve(String(reader.result || ''))
  reader.readAsText(blob)
})

// 按 manual_line 落库的图片路径读回图片，返回 objectURL（调用方负责 revoke）。
// httpWrap 响应拦截器已把 axios 响应解包为 response.data——responseType='blob' 时返回值即 Blob 本身。
const loadManualImageUrl = async (path: string): Promise<string> => {
  const blob: any = await _postBlob(MANUAL_IMAGE_DOWNLOAD_URL, { path })
  if (!blob || !(blob instanceof Blob)) {
    throw new Error('图片回显失败')
  }
  // 后端文件缺失/参数不合法时返回 JSON（blob.type 为 application/json），转成可读错误
  if (blob.type && blob.type.indexOf('json') >= 0) {
    let info = '图片不存在'
    try {
      info = JSON.parse(await readBlobText(blob)).info || info
    } catch (e) {
      // 解析失败保持默认提示
    }
    throw new Error(info)
  }
  return URL.createObjectURL(blob)
}

const imageVisible = ref(false)
const imageItem = ref<any>(null)
const imageLoading = ref(false)
const imageError = ref('')
const baselineUrl = ref('')
const actualUrl = ref('')

// 某检验项可看的图片张数（基准 + 实际，存了路径才算）
const imageCount = (item: any) => {
  let count = 0
  if (item?.baseline_image) count += 1
  if (item?.actual_image) count += 1
  return count
}

const revokeImageUrls = () => {
  if (baselineUrl.value) {
    URL.revokeObjectURL(baselineUrl.value)
    baselineUrl.value = ''
  }
  if (actualUrl.value) {
    URL.revokeObjectURL(actualUrl.value)
    actualUrl.value = ''
  }
}

const showImages = async (item: any) => {
  revokeImageUrls()
  imageItem.value = item
  imageError.value = ''
  imageVisible.value = true
  const baseline = item?.baseline_image || ''
  const actual = item?.actual_image || ''
  imageLoading.value = true
  // 基准/实际图独立加载：任一张失败不影响另一张展示，错误统一提示
  const errors: string[] = []
  try {
    if (baseline) {
      try {
        baselineUrl.value = await loadManualImageUrl(baseline)
      } catch (err: any) {
        errors.push('基准图片: ' + (err?.message || '加载失败'))
      }
    }
    if (actual) {
      try {
        actualUrl.value = await loadManualImageUrl(actual)
      } catch (err: any) {
        errors.push('实际图片: ' + (err?.message || '加载失败'))
      }
    }
  } catch (err: any) {
    errors.push(err?.message || '图片加载失败')
  } finally {
    imageLoading.value = false
    imageError.value = errors.length > 0 ? errors.join('；') : ''
  }
}

const closeImages = () => {
  imageVisible.value = false
  revokeImageUrls()
  imageItem.value = null
}

// 弹窗关闭后仍残留的 objectURL（极端场景下组件卸载）释放，防泄漏
onBeforeUnmount(() => {
  revokeImageUrls()
})
</script>
