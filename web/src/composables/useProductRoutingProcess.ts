import { ref, computed } from 'vue'
import api from '../api/trace-app'

/**
 * 「产品 → 工艺路线 → 工序」三级联动下拉（报工查询 / 报工不合格原因共用）
 *
 * 口径：
 *  - 选产品后工艺路线候选收窄到该产品对应的路线；选工艺路线后工序候选收窄到该路线的工序
 *  - **每一级都可以不选**（不选 = 不限），换上级自动清空下级
 *  - 未选工艺路线时工序候选取全部工序（`base_config/process_list`）
 *
 * 注意：`CustomSelect` 的 `change` 只在用户交互时触发（选择 / 清空），程序化赋值不触发，
 * 所以级联清空挂在 `@change` 上而不是 `watch(modelValue)`。
 */
export const useProductRoutingProcess = () => {
  const productType = ref('')
  const routingCode = ref('')
  const processCode = ref('')

  /** production_config_type 原样返回，用于「产品 → 路线」收窄 */
  const productList = ref<any[]>([])
  const allRoutingOptions = ref<{ label: string, value: string }[]>([])
  const processOptions = ref<{ label: string, value: string }[]>([])

  const productOptions = computed(() =>
    productList.value.map((p: any) => ({ label: p.production_type, value: p.production_type })))

  // 选了产品就只留该产品的路线；产品没有对应路线配置时回落全部，避免下拉空掉
  const routingOptions = computed(() => {
    if (!productType.value) return allRoutingOptions.value
    const routing = productList.value.find((p: any) => p.production_type == productType.value)?.routing_code
    const narrowed = allRoutingOptions.value.filter(o => o.value == routing)
    return narrowed.length > 0 ? narrowed : allRoutingOptions.value
  })

  /** 首屏加载：产品列表 + 全部工艺路线 + 全部工序 */
  const loadBaseOptions = async () => {
    try {
      const res = await api.queryProductTypeList()
      productList.value = res.data || []
    } catch (err: any) {
      console.error('加载产品列表失败:', err)
    }
    try {
      const res = await api.queryRoutingList()
      allRoutingOptions.value = (res.data || []).map((r: any) => ({
        label: r.routing_name ? `${r.routing_name} / ${r.routing_code}` : r.routing_code,
        value: r.routing_code,
      }))
    } catch (err: any) {
      console.error('加载工艺路线列表失败:', err)
    }
    await loadProcessOptions()
  }

  /** 工序候选：选了工艺路线取该路线的工序，否则取全部工序 */
  const loadProcessOptions = async () => {
    try {
      if (routingCode.value) {
        const res = await api.queryRoutingProcesses(routingCode.value)
        const processes = res.data?.processes || []
        processOptions.value = processes.map((p: any) => ({
          label: p.process_name ? `${p.process_name} / ${p.process_code}` : p.process_code,
          value: p.process_code,
        }))
      } else {
        const res = await api.queryProcessList()
        processOptions.value = (res.data || []).map((p: any) => ({
          label: p.process_name ? `${p.process_name} / ${p.process_code}` : p.process_code,
          value: p.process_code,
        }))
      }
    } catch (err: any) {
      console.error('加载工序列表失败:', err)
      processOptions.value = []
    }
  }

  /** 换产品：工艺路线、工序一并清空（下级候选跟着收窄） */
  const onProductChange = async () => {
    routingCode.value = ''
    processCode.value = ''
    await loadProcessOptions()
  }

  /** 换工艺路线：工序清空 */
  const onRoutingChange = async () => {
    processCode.value = ''
    await loadProcessOptions()
  }

  /** 查询用条件：未选的一律传 undefined，后端按「不限」处理 */
  const buildFilter = () => ({
    product_type: productType.value || undefined,
    routing_code: routingCode.value || undefined,
    process_code: processCode.value || undefined,
  })

  return {
    productType, routingCode, processCode,
    productOptions, routingOptions, processOptions,
    loadBaseOptions, loadProcessOptions,
    onProductChange, onRoutingChange,
    buildFilter,
  }
}
