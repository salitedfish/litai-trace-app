import json
import traceback

from mg_app_framework import HttpBasicHandler, get_logger, MesCode

from .encoder import DefaultEncoder
from ..entity.response_entity import Response


class BaseHandler(HttpBasicHandler):
    def data_received(self, chunk):
        pass

    def get_remote_ip(self):
        return self.request.headers.get("X-Real-IP") or \
               self.request.headers.get("X-Forwarded-For") or \
               self.request.remote_ip

    def options(self):
        self.set_status(200)
        self.finish()

    def write_error(self, status_code, **kwargs):
        exc_cls, exc_instance, trace = kwargs.get("exc_info")
        if status_code == 500:
            get_logger().error(traceback.format_exc())
            self.set_status(status_code)
            self.send_response_data(MesCode.fail, None, '服务器内部错误')

    def set_default_headers(self):
        super().set_default_headers()
        self.set_header('Access-Control-Allow-Methods', 'PUT,DELETE,OPTIONS,GET,POST')
        self.set_header("Content-Type", "application/json; charset=utf-8")

    def send_response(self, response: Response):
        self.send_response_data(response.code, response.data, response.info)

    def _set_response_data(self, result, encoder=None):
        if encoder is None:
            encoder = DefaultEncoder
        try:
            self.finish(json.dumps(result, ensure_ascii=False, cls=encoder))
        except Exception as e:
            self.finish(json.dumps(
                {"code": MesCode.fail, "info": str(e)}))
            traceback.print_exc()
