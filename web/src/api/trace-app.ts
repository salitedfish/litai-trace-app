import { _post, _get } from './httpWrap'

export default {
  health: () => _get('api/trace_app/health'),
  echo: (data: any) => _post('api/trace_app/echo', data),

  // 追溯查询
  queryByOutput: (qrCode: string) => _post('api/trace_app/trace/query_by_output', { qr_code: qrCode }),
  queryInputs: (workorderCode: string) => _post('api/trace_app/trace/query_inputs', { workorder_code: workorderCode }),
  queryOutputsByInput: (inputCode: string) => _post('api/trace_app/trace/query_outputs_by_input', { input_code: inputCode }),
  queryProcessParams: (workorderCode: string) => _post('api/trace_app/trace/query_process_params', { workorder_code: workorderCode }),
  queryInspectionRecord: (workorderCode: string) => _post('api/trace_app/trace/query_inspection_record', { workorder_code: workorderCode }),
  querySubmissionRecords: (qrCode: string, procedureCode: string, deviceCode: string) =>
    _post('api/trace_app/trace/query_submission_records', { qr_code: qrCode, procedure_code: procedureCode, device_code: deviceCode }),

  // 设备数采查询
  queryDeviceList: () => _post('api/trace_app/device_data/list'),
  queryDevicePoints: (deviceCode: string) =>
    _post('api/trace_app/device_data/points', { device_code: deviceCode }),
  queryDeviceData: (params: {
    device_code: string,
    point_code?: string,
    start_time: string,
    end_time: string,
    page: number,
    page_size: number,
  }) => _post('api/trace_app/device_data/query', params),

  // 智能看板配置
  getDashboardConfig: () => _get('api/trace_app/dashboard/config'),
  saveDashboardConfig: (params: { title: string, start_date?: string, end_date?: string, workshop_code?: string, product_type?: string[] }) =>
    _post('api/trace_app/dashboard/config', params),
  // 历史数据（前两周日完成量 / 日均小时完成量，进看板时查一次）
  queryHistoryOutput: (productTypes: string[]) =>
    _post('api/trace_app/dashboard/history_output', { product_types: productTypes }),

  // 智能看板2配置（独立于看板1）
  getDashboardConfig2: () => _get('api/trace_app/dashboard_2/config'),
  saveDashboardConfig2: (params: { title: string, start_date?: string, end_date?: string, workshop_code?: string, product_type?: string[] }) =>
    _post('api/trace_app/dashboard_2/config', params),
  // 智能看板2 - 检验项不合格占比（饼图，日期/产线/产品型号筛选，空即不限）
  queryUnqualifiedPie: (params: { start_date?: string, end_date?: string, workshop_code?: string, product_types?: string[] }) =>
    _post('api/trace_app/dashboard_2/unqualified_pie', params),
  // 智能看板2 - 不合格原因占比（饼图，样本=不合格项勾选的原因，无原因项不计入）
  queryUnqualifiedReasonPie: (params: { start_date?: string, end_date?: string, workshop_code?: string, product_types?: string[] }) =>
    _post('api/trace_app/dashboard_2/unqualified_reason_pie', params),

  // 生产基础配置
  queryRoutingList: () => _post('api/trace_app/base_config/routing_list'),
  queryRoutingProcesses: (routingCode: string) =>
    _post('api/trace_app/base_config/routing_processes', { routing_code: routingCode }),
  queryLineList: () => _post('api/trace_app/base_config/line_list'),
  queryProductTypeList: () => _post('api/trace_app/base_config/product_type_list'),
  queryLineDevices: (workshopCode: string) =>
    _post('api/trace_app/base_config/line_devices', { workshop_code: workshopCode }),
}
