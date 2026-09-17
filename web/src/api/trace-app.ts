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

  // 扫码登料查询（数据源：{org}_manual_trace.material_scan_records）
  queryMaterialScanRecords: (params: {
    code?: string,
    start_time?: string,
    end_time?: string,
    page: number,
    page_size: number,
  }) => _post('api/trace_app/material_scan/query', params),

  // 智能看板配置
  // unused_devices：未使用的设备编码列表（这些设备不显示状态、不计入 OEE）
  getDashboardConfig: () => _get('api/trace_app/dashboard/config'),
  saveDashboardConfig: (params: { title: string, start_date?: string, end_date?: string, workshop_code?: string, product_type?: string[], unused_devices?: string[] }) =>
    _post('api/trace_app/dashboard/config', params),
  // 历史数据（前两周日完成量 / 日均小时完成量，进看板时查一次）
  queryHistoryOutput: (productTypes: string[]) =>
    _post('api/trace_app/dashboard/history_output', { product_types: productTypes }),

  // 智能看板2配置（独立于看板1）
  // mock：模拟数据配置（客户演示用），{模块: {enabled, data}}，模块见 BoardSettingsView 的 mockModules
  // unused_devices：未使用的设备编码列表（这些设备不显示状态、不计入 OEE）
  getDashboardConfig2: () => _get('api/trace_app/dashboard_2/config'),
  saveDashboardConfig2: (params: { title: string, start_date?: string, end_date?: string, workshop_code?: string, product_type?: string[], unused_devices?: string[], mock?: any }) =>
    _post('api/trace_app/dashboard_2/config', params),
  // 智能看板2 - 检验项不合格占比（饼图，日期/产线/产品型号筛选，空即不限）
  queryUnqualifiedPie: (params: { start_date?: string, end_date?: string, workshop_code?: string, product_types?: string[] }) =>
    _post('api/trace_app/dashboard_2/unqualified_pie', params),
  // 智能看板2 - 不合格原因占比（饼图，样本=不合格项勾选的原因，无原因项不计入）
  queryUnqualifiedReasonPie: (params: { start_date?: string, end_date?: string, workshop_code?: string, product_types?: string[] }) =>
    _post('api/trace_app/dashboard_2/unqualified_reason_pie', params),

  // 报工查询（数据源：{org}_order_retrospect.work_order_retrospect_records 的产出记录）
  queryReportRecords: (params: {
    product_type?: string,
    routing_code?: string,
    process_code?: string,
    operator?: string,
    check_result?: string,
    device_code?: string,
    start_time?: string,
    end_time?: string,
    page: number,
    page_size: number,
  }) => _post('api/trace_app/report/query', params),
  // 人员/设备下拉候选（取自报工记录里出现过的值，无请求参数）
  queryReportFilterOptions: () => _post('api/trace_app/report/filter_options'),
  // 报工不合格原因次数统计（数据源：{org}_manual_trace.inspection_records，按需求不带日期条件）
  queryUnqualifiedReasons: (params: {
    product_type?: string,
    routing_code?: string,
    process_code?: string,
    start_time?: string,
    end_time?: string,
    page: number,
    page_size: number,
  }) => _post('api/trace_app/report/unqualified_reason_query', params),
  // 不合格原因关联的报工记录（按原因反查勾选该原因的检验单 → 产出报工记录，行结构同报工查询）
  queryUnqualifiedReasonRecords: (params: {
    reason_code?: string,
    reason_name?: string,
    product_type?: string,
    routing_code?: string,
    process_code?: string,
    start_time?: string,
    end_time?: string,
    page: number,
    page_size: number,
  }) => _post('api/trace_app/report/unqualified_reason_records', params),

  // 生产基础配置
  queryRoutingList: () => _post('api/trace_app/base_config/routing_list'),
  queryRoutingProcesses: (routingCode: string) =>
    _post('api/trace_app/base_config/routing_processes', { routing_code: routingCode }),
  queryProcessList: () => _post('api/trace_app/base_config/process_list'),
  queryLineList: () => _post('api/trace_app/base_config/line_list'),
  queryProductTypeList: () => _post('api/trace_app/base_config/product_type_list'),
  queryLineDevices: (workshopCode: string) =>
    _post('api/trace_app/base_config/line_devices', { workshop_code: workshopCode }),
}
