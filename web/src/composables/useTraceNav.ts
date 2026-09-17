import { ref } from 'vue'

/**
 * 跨页跳转追溯查询的「待追溯码」信箱
 *
 * 报工查询页的投入物料弹窗里点「追溯此码」时，本页没有追溯入口，
 * 于是把码投进这里并切到追溯查询视图；追溯查询视图 watch 到后自行填入投入码并查询。
 * 两个视图都是 v-show 常驻挂载，所以用 watch 而不是 onMounted。
 */
const pendingTraceCode = ref('')

/** 投入一个待追溯的码（由报工查询页调用） */
export const setPendingTraceCode = (code: string) => {
  pendingTraceCode.value = code || ''
}

/** 取走待追溯的码并清空（由追溯查询页在触发查询后调用，避免重复触发） */
export const takePendingTraceCode = () => {
  const code = pendingTraceCode.value
  pendingTraceCode.value = ''
  return code
}

/** 追溯查询页 watch 这个 ref 感知新的待追溯码 */
export const usePendingTraceCode = () => pendingTraceCode
