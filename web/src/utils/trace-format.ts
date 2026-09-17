/**
 * 追溯/报工相关的展示格式化 —— 追溯查询、报工查询及各弹窗共用
 */

/** 去掉后端时间串的毫秒尾巴（'2026-07-14 09:14:57.983' → '2026-07-14 09:14:57'），空值显示 '-' */
export const fmtTime = (t: string) => t ? t.replace(/\.\d+$/, '') : '-'

/**
 * 检测结果配色：三档合格各一色，其余（不合格）红色。
 * 取值与后端 calc_check_result 的显示值一致：一次合格/返工合格/复投合格/不合格。
 */
export const checkResultClass = (v: string) => {
  if (!v || v === '-') return ''
  if (v === '一次合格' || v === 'OK') return 'text-teal-600 font-medium'
  if (v === '返工合格') return 'text-amber-600 font-medium'
  if (v === '复投合格') return 'text-blue-600 font-medium'
  return 'text-red-600 font-medium'
}
