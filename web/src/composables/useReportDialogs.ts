import { ref } from 'vue'

/**
 * 报工详情弹窗协调器 —— 追溯查询 / 报工查询 共用
 *
 * 四个弹窗（投入物料 / 工艺参数 / 检验单 / 提交记录）各自维护自己的开关与当前行，
 * 「提交记录」行内再点开前三个时，用该行的工单/时间组装目标弹窗的报工记录
 * （弹窗组件内部自己发请求，这里只负责把记录拼对）。
 */
export const useReportDialogs = () => {
  const inputVisible = ref(false)
  const inputStep = ref<any>(null)

  const paramVisible = ref(false)
  const paramStep = ref<any>(null)

  const inspectionVisible = ref(false)
  const inspectionStep = ref<any>(null)

  const submissionVisible = ref(false)
  const submissionStep = ref<any>(null)

  const openInput = (step: any) => {
    inputStep.value = step
    inputVisible.value = true
  }

  const openParam = (step: any) => {
    paramStep.value = step
    paramVisible.value = true
  }

  const openInspection = (step: any) => {
    inspectionStep.value = step
    inspectionVisible.value = true
  }

  const openSubmission = (step: any) => {
    submissionStep.value = step
    submissionVisible.value = true
  }

  /** 提交记录行内按钮：弹窗组件已先关自己、再抛本事件，这里只管开目标弹窗 */
  const openDetailFromSubmission = (payload: { kind: string, record: any, step: any }) => {
    const { kind, record, step } = payload || {} as any
    if (kind === 'input') {
      openInput({
        workorder_code: record?.workorder_code,
        procedure_name: step?.procedure_name,
        procedure_code: step?.procedure_code,
        qr_code: step?.qr_code,
      })
    } else if (kind === 'param') {
      openParam({
        workorder_code: record?.workorder_code,
        procedure_name: step?.procedure_name,
        procedure_code: step?.procedure_code,
        qr_code: step?.qr_code,
        // 补带设备/时间，供弹窗内「数采数据」跳转用；op_time 取提交记录本身更精确
        device_code: step?.device_code || record?.device_code,
        op_time: record?.op_time || step?.op_time,
      })
    } else if (kind === 'inspection') {
      openInspection({
        workorder_code: record?.workorder_code,
        procedure_name: step?.procedure_name,
        procedure_code: step?.procedure_code,
        qr_code: step?.qr_code,
      })
    }
  }

  return {
    inputVisible, inputStep,
    paramVisible, paramStep,
    inspectionVisible, inspectionStep,
    submissionVisible, submissionStep,
    openInput, openParam, openInspection, openSubmission,
    openDetailFromSubmission,
  }
}
