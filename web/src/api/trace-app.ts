import { _post, _get } from './httpWrap'

export default {
  health: () => _get('api/trace_app/health'),
  echo: (data: any) => _post('api/trace_app/echo', data),
}
