import { defineComponent, h } from 'vue'

/**
 * 物料类型标签 —— 追溯查询 / 报工查询 共用
 *
 * raw_material=原材料(amber) / semi_finished_product=半成品(blue) / finished_product=成品(teal)，
 * 未知类型原样显示编码、走灰色兜底样式。
 */
export default defineComponent({
  name: 'MaterialTypeTag',
  props: { type: String },
  setup(props: any) {
    const labels: Record<string, string> = {
      raw_material: '原材料',
      semi_finished_product: '半成品',
      finished_product: '成品',
    }
    const colors: Record<string, string> = {
      raw_material: 'bg-amber-50 text-amber-600 border-amber-200',
      semi_finished_product: 'bg-blue-50 text-blue-600 border-blue-200',
      finished_product: 'bg-teal-50 text-teal-600 border-teal-200',
    }
    return () => {
      const type = props.type || ''
      const label = labels[type] || type
      const color = colors[type] || 'bg-gray-50 text-gray-600 border-gray-200'
      return h('span', {
        class: `inline-block whitespace-nowrap px-2 py-0.5 rounded text-xs font-medium border ${color}`
      }, label)
    }
  }
})
