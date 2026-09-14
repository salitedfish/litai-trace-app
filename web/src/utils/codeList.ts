/**
 * 编码列表（逗号分隔输入框）的解析与回填。
 *
 * 看板设置页的「未使用的设备」让用户手输设备编码、逗号分隔，落库是数组——
 * 两边口径必须一致，所以解析只此一处。
 *
 * 中英文逗号都拆：现场用中文输入法敲出来的是全角「，」，只认半角的话
 * 这个框会安静地不生效（页面照常保存、看板照常显示全部设备），排查起来很费劲。
 */

/** 逗号分隔文本 → 编码数组（去空白、丢空项、去重保序） */
export function parseCodeList(text: string): string[] {
  const result: string[] = []
  const parts = String(text || '').split(/[,，]/)
  for (const part of parts) {
    const code = part.trim()
    if (code && result.indexOf(code) < 0) result.push(code)
  }
  return result
}

/** 编码数组 → 逗号分隔文本（回填输入框用） */
export function formatCodeList(list: string[]): string {
  return Array.isArray(list) ? list.join(',') : ''
}
