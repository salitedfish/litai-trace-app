// 日期时间工具（前端侧，对齐后端 utils/datetime_utils.py）
//
// ⚠️ 本项目时间口径约定（踩过坑，务必遵守）：
//   MES 各库的时间字段（idi_{org}.datas.timestamp、{org}_manual_trace.material_scan_records.op_time 等）
//   存的是**服务器本地墙上时间（北京时间）**，不是 UTC——尽管 datas.timestamp 的 BSON 类型是日期，
//   读出来会带 +00:00 标记，那是假象，值本身就是北京时间的数字。
//   因此前后端读写一律按"墙上时间"直接比较，**绝不要做本地 ↔ UTC 换算**：
//     - 后端先例：oee_service 用 datetime.now() 裸值直接比 datas.timestamp
//     - 后端先例：material_scan_record_service._normalize_time 把本地时间串直接比 op_time 字符串
//   反向教训：数采查询页曾对本地时间串调用 toISOString()，整体偏 8 小时，跳转后查不到数据。

/** 取本地日期 YYYY-MM-DD。
 *  不能用 new Date().toISOString().slice(0,10)——那是 UTC 日期，
 *  北京时间 00:00~07:59 之间会取到"昨天"。
 */
export const formatDateLocal = (d: Date) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/** datetime-local 输入值（YYYY-MM-DDTHH:mm，只到分）补齐秒 → YYYY-MM-DDTHH:mm:ss。
 *  后端 parse_iso_format_datetime 在 Python 3.6 下无 fromisoformat，走的是手写正则，
 *  其 pattern 要求秒必填；不补秒会拿到"时间格式不正确"。
 */
export const toIsoSeconds = (v: string) => {
  const s = (v || '').trim()
  return s.length == 16 ? `${s}:00` : s
}
