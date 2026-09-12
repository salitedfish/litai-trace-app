<template>
  <div class="min-h-full flex flex-col relative z-10 w-full max-w-[800px] mx-auto pt-8">
    <div class="bg-card rounded-2xl border border-border/40 p-8 shadow-sm">
      <div class="flex items-center gap-3 mb-8">
        <div class="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
          <svg class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065zM15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-foreground">智能看板2设置</h2>
          <p class="text-sm text-muted-foreground">配置智能看板2的显示内容</p>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-x-5 gap-y-6">
        <!-- 看板标题（整行） -->
        <div class="flex flex-col gap-2 col-span-2">
          <label class="text-sm font-medium text-foreground">
            看板标题 <span class="text-red-500">*</span>
          </label>
          <input v-model="title" type="text" placeholder="请输入看板标题"
            class="w-full px-4 py-2.5 rounded-lg border border-border bg-white text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
          <p class="text-xs text-muted-foreground">该标题将显示在智能看板2的顶部</p>
        </div>

        <!-- 开始日期 / 结束日期 -->
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-foreground">开始日期</label>
          <input v-model="startDate" type="date"
            class="w-full px-4 py-2.5 rounded-lg border border-border bg-white text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
          <p class="text-xs text-muted-foreground">统计的起始日期，为空则取当天</p>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-foreground">结束日期</label>
          <input v-model="endDate" type="date"
            class="w-full px-4 py-2.5 rounded-lg border border-border bg-white text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all" />
          <p class="text-xs text-muted-foreground">统计的截止日期，为空则取当天</p>
        </div>

        <!-- 产线 / 产品型号 -->
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-foreground">产线</label>
          <CustomSelect
            v-model="workshopCode"
            :options="lineOptions"
            :disabled="lineLoading"
            variant="outline"
            clearable
            placeholder="请选择产线"
          />
          <p class="text-xs text-muted-foreground">看板展示的产线，不选则展示全部产线</p>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-foreground">产品型号</label>
          <MultiSelect
            v-model="productType"
            :options="productTypeOptions"
            placeholder="请选择产品型号（可多选）"
          />
          <p class="text-xs text-muted-foreground">看板展示的产品型号，可多选，不选则不限</p>
        </div>

      </div>

      <!-- ==================== 模拟数据配置 ====================
           按模块单独启用：启用后看板2 对应模块展示配置的模拟数据，不再查真实数据。
           开关状态与"启用中"提示在此页如实展示，看板本体不带任何模拟字样。 -->
      <div class="mt-8 pt-6 border-t border-border/40">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
            <svg class="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-bold text-foreground">模拟数据配置</h2>
            <p class="text-sm text-muted-foreground">按模块单独启用；启用后看板2 对应模块展示配置的模拟数据，不再展示真实数据</p>
          </div>
        </div>

        <!-- 启用数量提示：一进页面就能看出当前有几块在看模拟数据 -->
        <div v-if="mockEnabledCount > 0"
          class="mb-4 px-4 py-2.5 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-700 flex items-center gap-2">
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
          当前有 {{ mockEnabledCount }} 个模块启用模拟数据，看板2 将展示模拟数据而非真实数据
        </div>

        <!-- 模块列表：一行一个模块，开关直接控制启停，数据在弹窗里编辑 -->
        <div class="rounded-xl border border-border/60 overflow-hidden">
          <div v-for="(m, idx) in mockModules" :key="m.key"
            class="flex items-center gap-4 px-4 py-3"
            :class="idx > 0 ? 'border-t border-border/40' : ''">
            <div class="flex-1 min-w-0 flex flex-col gap-0.5">
              <span class="text-sm font-medium text-foreground">{{ m.title }}</span>
              <span class="text-xs text-muted-foreground truncate" :title="m.hint">{{ m.hint }}</span>
            </div>

            <!-- 是否已填数据（不必逐个点开弹窗确认） -->
            <span v-if="mockState[m.key].text.trim()" class="text-xs text-emerald-600 shrink-0">已配置</span>
            <span v-else class="text-xs text-muted-foreground shrink-0">未配置</span>

            <!-- 启停开关 -->
            <button type="button" class="mock-switch shrink-0"
              :class="mockState[m.key].enabled ? 'on' : ''"
              :aria-pressed="mockState[m.key].enabled"
              @click="toggleMock(m.key)">
              <span class="mock-switch-knob"></span>
            </button>

            <!-- 编辑该模块的模拟数据 -->
            <button type="button"
              class="px-3 py-1.5 rounded-lg border border-border text-xs text-foreground hover:bg-muted/30 transition-colors shrink-0"
              @click="openMockEditor(m.key)">模拟数据</button>
          </div>
        </div>

        <p class="text-xs text-muted-foreground mt-2">模拟数据为 JSON 格式，「模拟数据」按钮打开弹窗编辑，弹窗内可一键填入示例</p>
      </div>

      <!-- 模拟数据编辑弹窗（本页带侧边栏，弹窗必须 Teleport 到 body 才不被导航栏遮住） -->
      <Teleport to="body">
        <transition name="modal-fade">
          <div v-if="mockEditor.visible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30"
            @click.self="closeMockEditor">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-hidden border border-border flex flex-col m-4">
              <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
                <div class="min-w-0">
                  <h3 class="text-base font-bold text-foreground">{{ mockEditorTitle }}</h3>
                  <p class="text-xs text-muted-foreground mt-0.5">{{ mockEditorHint }}</p>
                </div>
                <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors shrink-0"
                  @click="closeMockEditor">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
              </div>

              <div class="p-6 flex flex-col gap-2 overflow-auto">
                <textarea v-model="mockEditor.text" rows="12" spellcheck="false"
                  :placeholder="mockEditorExample"
                  class="w-full px-3 py-2 rounded-lg border border-border bg-white text-foreground font-mono text-xs leading-relaxed focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all resize-y"></textarea>
                <div class="flex items-center justify-between gap-3">
                  <span class="text-xs" :class="mockEditorTip.ok ? 'text-emerald-600' : 'text-red-500'">{{ mockEditorTip.text }}</span>
                  <button type="button" class="text-xs text-accent hover:underline shrink-0"
                    @click="mockEditor.text = mockEditorExample">填入示例</button>
                </div>
              </div>

              <div class="px-6 py-4 border-t border-border/50 flex items-center justify-end gap-3 shrink-0">
                <button class="px-5 py-2 rounded-lg border border-border text-sm text-foreground hover:bg-muted/30 transition-colors"
                  @click="closeMockEditor">取消</button>
                <button class="px-5 py-2 rounded-lg bg-accent text-white text-sm font-medium hover:bg-accent/90 transition-colors"
                  @click="confirmMockEditor">确定</button>
              </div>
            </div>
          </div>
        </transition>
      </Teleport>

      <!-- 保存（整行） -->
      <div class="flex items-center gap-3 pt-6">
        <button class="px-6 py-2.5 bg-accent text-white rounded-lg text-sm font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 flex items-center gap-2"
          :disabled="saving || !title.trim()" @click="handleSave">
          <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
          <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
          确认
        </button>

        <span v-if="saved" class="text-sm text-emerald-600 flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          保存成功
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import api from '../../api/trace-app'
import CustomSelect from '../../components/CustomSelect.vue'
import MultiSelect from '../../components/MultiSelect.vue'
import { showToast } from '../../utils/dialog'

const title = ref('')
const startDate = ref('')
const endDate = ref('')
const workshopCode = ref('')
const productType = ref<string[]>([])
const lineList = ref<{ workshop_code: string, workshop_name: string }[]>([])
const lineLoading = ref(false)
const productTypeList = ref<{ production_type: string, routing_code: string }[]>([])
const saving = ref(false)
const saved = ref(false)

const productTypeOptions = computed(() =>
  productTypeList.value.map(pt => ({ label: pt.production_type, value: pt.production_type }))
)

const lineOptions = computed(() =>
  lineList.value.map(line => ({ label: line.workshop_name, value: line.workshop_code }))
)

const loadLineList = async () => {
  lineLoading.value = true
  try {
    const res = await api.queryLineList()
    lineList.value = res.data || []
  } catch (err: any) {
    console.error('加载产线列表失败:', err)
  } finally {
    lineLoading.value = false
  }
}

// ==================== 模拟数据配置（客户演示用） ====================
// 四个模块与看板2 的四张卡片一一对应，key 必须与后端 MOCK_MODULES 一致。
// 各模块的 example 同时充当文本域占位提示与「填入示例」按钮的内容，是该模块 JSON 形状的唯一出处。
const DEVICE_STATUS_OPTIONS = ['运行', '待机', '故障', '关机']

const mockModules = [
  {
    key: 'oee',
    title: '设备 OEE',
    hint: '对象；oee / availability / performance / quality / target 五项均为数字',
    example: { oee: 86.5, availability: 92.3, performance: 95.1, quality: 98.6, target: 90 },
  },
  {
    key: 'device_status',
    title: '产线设备实时状态',
    hint: '对象；units 为生产单元数组，每个设备填 device_name 与 status（运行/待机/故障/关机）',
    example: {
      workshop_name: '卡特产线',
      units: [
        {
          produce_unit_name: '零件清洗',
          devices: [
            { device_code: 'dev_csbqxj_001', device_name: '超声波清洗机', device_type: '检测', status: '运行' },
            { device_code: 'dev_csbqxj_002', device_name: '高压清洗机', device_type: '非检测', status: '待机' },
          ],
        },
      ],
    },
  },
  {
    key: 'process_production',
    title: '工序加工情况',
    hint: '数组；每项填 procedure_code / procedure_name / total / first_pass_rate / total_rate',
    example: [
      { procedure_code: 'GX0020', procedure_name: '零件清洗', total: 320, first_pass_rate: 98.4, total_rate: 99.1 },
      { procedure_code: 'GX0130', procedure_name: '打标', total: 318, first_pass_rate: 99.4, total_rate: 99.7 },
    ],
  },
  {
    key: 'unqualified_reason',
    title: '不合格原因占比',
    hint: '数组；每项填 reason_name 与 count（正数）',
    example: [
      { reason_name: '毛刺', count: 12 },
      { reason_name: '尺寸超差', count: 7 },
      { reason_name: '外观划伤', count: 4 },
    ],
  },
]

// 每个模块的开关与文本域内容（文本域保留用户输入的原文，保存时才解析）
const mockState = reactive<Record<string, { enabled: boolean, text: string }>>({})
for (const m of mockModules) {
  mockState[m.key] = { enabled: false, text: '' }
}

// 启用中的模块数量（页面顶部提示用：开关会持久生效，开着不能被遗忘）
const mockEnabledCount = computed(() => mockModules.filter(m => mockState[m.key].enabled).length)

/** 是否为普通对象（非 null、非数组） */
function isPlainObject(v: any): boolean {
  return v != null && typeof v == 'object' && !Array.isArray(v)
}

/** 各模块的数据形状校验：返回错误提示，空串表示通过 */
const mockValidators: Record<string, (data: any) => string> = {
  // 看板把五项数字直接喂给仪表盘与进度条，任一项缺失或非数字都会渲染成空/NaN
  oee: (d) => {
    if (!isPlainObject(d)) return '需要对象（{...}）'
    for (const key of ['oee', 'availability', 'performance', 'quality', 'target']) {
      if (typeof d[key] != 'number') return '缺少数字字段 ' + key
    }
    return ''
  },
  // 看板按 device_type 选图标、按 status 上色，两者缺一都会退化成默认样式
  device_status: (d) => {
    if (!isPlainObject(d)) return '需要对象（{...}）'
    if (!Array.isArray(d.units)) return '缺少 units 数组'
    for (let i = 0; i < d.units.length; i++) {
      const devices = d.units[i]?.devices
      if (!Array.isArray(devices)) return 'units[' + i + '].devices 需要数组'
      for (let j = 0; j < devices.length; j++) {
        if (!devices[j]?.device_name) return 'units[' + i + '].devices[' + j + '] 缺少 device_name'
        if (DEVICE_STATUS_OPTIONS.indexOf(devices[j].status) < 0) {
          return 'units[' + i + '].devices[' + j + '].status 需为 ' + DEVICE_STATUS_OPTIONS.join('/')
        }
      }
    }
    return ''
  },
  // 看板对两个合格率调 toFixed，非数字会直接抛错炸掉整张表
  process_production: (d) => {
    if (!Array.isArray(d)) return '需要数组（[...]）'
    for (let i = 0; i < d.length; i++) {
      const item = d[i]
      if (!isPlainObject(item)) return '第 ' + (i + 1) + ' 项需要对象'
      if (!item.procedure_code) return '第 ' + (i + 1) + ' 项缺少 procedure_code'
      if (!item.procedure_name) return '第 ' + (i + 1) + ' 项缺少 procedure_name'
      for (const key of ['total', 'first_pass_rate', 'total_rate']) {
        if (typeof item[key] != 'number') return '第 ' + (i + 1) + ' 项缺少数字字段 ' + key
      }
    }
    return ''
  },
  unqualified_reason: (d) => {
    if (!Array.isArray(d)) return '需要数组（[...]）'
    for (let i = 0; i < d.length; i++) {
      const item = d[i]
      if (!isPlainObject(item)) return '第 ' + (i + 1) + ' 项需要对象'
      if (!item.reason_name) return '第 ' + (i + 1) + ' 项缺少 reason_name'
      if (typeof item.count != 'number' || item.count <= 0) return '第 ' + (i + 1) + ' 项 count 需为正数'
    }
    return ''
  },
}

/** 解析并校验单个模块的文本：返回 {ok, msg, data}；保存前校验与文本域实时提示共用 */
function parseMockText(key: string, text: string): { ok: boolean, msg: string, data: any } {
  let parsed: any
  try {
    parsed = JSON.parse(text)
  } catch (err: any) {
    return { ok: false, msg: 'JSON 解析失败：' + (err?.message || '格式不正确'), data: null }
  }
  const msg = mockValidators[key](parsed)
  if (msg) return { ok: false, msg: msg, data: null }
  return { ok: true, msg: 'JSON 格式正确', data: parsed }
}

// ========== 模拟数据编辑弹窗 ==========
// 弹窗内是草稿态：点「确定」才写回 mockState，「取消」直接丢弃
const mockEditor = reactive({ visible: false, key: '', text: '' })

const currentMockModule = computed(() => mockModules.find(m => m.key == mockEditor.key))
const mockEditorTitle = computed(() => (currentMockModule.value?.title || '') + ' · 模拟数据')
const mockEditorHint = computed(() => currentMockModule.value?.hint || '')
// 占位提示与「填入示例」同一份内容：该模块 example 即数据形状的唯一出处
const mockEditorExample = computed(() => currentMockModule.value ? JSON.stringify(currentMockModule.value.example, null, 2) : '')

// 弹窗内实时校验提示：没填不提示，填了立刻告知解析是否通过
const mockEditorTip = computed(() => {
  const text = mockEditor.text.trim()
  if (!text || !currentMockModule.value) return { ok: false, text: '' }
  const result = parseMockText(mockEditor.key, text)
  return { ok: result.ok, text: result.msg }
})

/** 打开某模块的模拟数据编辑弹窗，带出已配置内容 */
function openMockEditor(key: string) {
  if (!mockModules.some(m => m.key == key)) return
  mockEditor.key = key
  mockEditor.text = mockState[key].text
  mockEditor.visible = true
}

function closeMockEditor() {
  mockEditor.visible = false
}

/** 确定：留空 = 清空该模块数据；有内容必须合法，不合法不关闭 */
function confirmMockEditor() {
  const text = mockEditor.text.trim()
  if (text) {
    const result = parseMockText(mockEditor.key, text)
    if (!result.ok) {
      showToast(result.msg, 'error')
      return
    }
  }
  const state = mockState[mockEditor.key]
  state.text = mockEditor.text
  // 清空数据等于该模块无可展示内容，开关同步关掉——否则行上「未配置 + 开关亮着」自相矛盾
  if (!state.text.trim()) state.enabled = false
  mockEditor.visible = false
}

/** 启停开关：没有数据、或数据不合法都不允许开启（避免开启后看板该模块空着或渲染出错） */
function toggleMock(key: string) {
  const state = mockState[key]
  if (state.enabled) {
    state.enabled = false
    return
  }
  const text = state.text.trim()
  if (!text) {
    showToast('请先配置模拟数据再启用', 'warning')
    return
  }
  const result = parseMockText(key, text)
  if (!result.ok) {
    showToast('模拟数据不合法：' + result.msg, 'error')
    return
  }
  state.enabled = true
}

/** 保存前逐块校验：返回错误提示与要落库的 mock 对象（error 非空即拦下） */
function buildMockConfig(): { error: string, mock: Record<string, any> } {
  const mock: Record<string, any> = {}
  for (const m of mockModules) {
    const state = mockState[m.key]
    const text = state.text.trim()
    // 未启用且没填：该模块不落库（此前存过的会被清除，看板回到真实数据）
    if (!state.enabled && !text) continue
    if (!text) {
      // 启用却没填数据：看板该模块没数据可展示，直接拦下
      return { error: '「' + m.title + '」已启用模拟数据，请填写 JSON', mock: {} }
    }
    const result = parseMockText(m.key, text)
    if (!result.ok) return { error: '「' + m.title + '」' + result.msg, mock: {} }
    // 未启用但留了数据也一并保存，用户重新开启时不必重填
    mock[m.key] = { enabled: state.enabled, data: result.data }
  }
  return { error: '', mock: mock }
}

const loadProductTypeList = async () => {
  try {
    const res = await api.queryProductTypeList()
    productTypeList.value = res.data || []
  } catch (err: any) {
    console.error('加载产品型号列表失败:', err)
  }
}

onMounted(async () => {
  try {
    const res = await api.getDashboardConfig2()
    const cfg = res.data || {}
    title.value = cfg.title || ''
    startDate.value = cfg.start_date || ''
    endDate.value = cfg.end_date || ''
    workshopCode.value = cfg.workshop_code || ''
    productType.value = Array.isArray(cfg.product_type) ? cfg.product_type : []
    // 模拟数据配置：未配置的模块保持"未启用 + 空文本域"
    const mockCfg = isPlainObject(cfg.mock) ? cfg.mock : {}
    for (const m of mockModules) {
      const item = mockCfg[m.key]
      if (!isPlainObject(item)) continue
      mockState[m.key].enabled = Boolean(item.enabled)
      mockState[m.key].text = item.data == null ? '' : JSON.stringify(item.data, null, 2)
    }
  } catch (err: any) {
    console.error('加载看板2配置失败:', err)
  }
  await loadLineList()
  await loadProductTypeList()
})

const handleSave = async () => {
  if (!title.value.trim()) return
  // 保存前逐块校验模拟数据，任一块不合法就拦下（避免看板展示残缺数据）
  const { error, mock } = buildMockConfig()
  if (error) {
    showToast(error, 'error')
    return
  }
  saving.value = true
  saved.value = false
  try {
    await api.saveDashboardConfig2({
      title: title.value.trim(),
      start_date: startDate.value,
      end_date: endDate.value,
      workshop_code: workshopCode.value,
      product_type: productType.value,
      mock: mock,
    })
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (err: any) {
    console.error('保存看板2配置失败:', err)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* 模拟数据启用开关 */
.mock-switch {
  position: relative;
  width: 40px;
  height: 22px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.35);
  transition: background 0.2s ease;
  cursor: pointer;
}

.mock-switch.on {
  background: #f59e0b;
}

.mock-switch-knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease;
}

.mock-switch.on .mock-switch-knob {
  transform: translateX(18px);
}

/* 模拟数据编辑弹窗淡入淡出（与追溯查询页各弹窗同一套写法） */
.modal-fade-enter-active {
  transition: opacity 0.15s ease-out;
}
.modal-fade-leave-active {
  transition: opacity 0.1s ease-in;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
