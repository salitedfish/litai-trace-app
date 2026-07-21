import { _post, _get } from './httpWrap'

export default {
  health: () => _get('api/trace_app/health'),
  echo: (data: any) => _post('api/trace_app/echo', data),

  // 追溯查询
  queryByOutput: (qrCode: string) => _post('api/trace_app/trace/query_by_output', { qr_code: qrCode }),
  queryInputs: (workorderCode: string) => _post('api/trace_app/trace/query_inputs', { workorder_code: workorderCode }),
  queryOutputsByInput: (inputCode: string) => _post('api/trace_app/trace/query_outputs_by_input', { input_code: inputCode }),
  queryProcessParams: (workorderCode: string) => _post('api/trace_app/trace/query_process_params', { workorder_code: workorderCode }),
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
}
