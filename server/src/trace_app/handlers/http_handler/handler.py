import traceback

from mg_app_framework import get_logger, loginrequired
from tornado_request_mapping import request_mapping

from trace_app.common.base_handler import BaseHandler
from trace_app.entity.response_entity import Response
from trace_app.entity.response_model import HealthResponse, EchoRequest, EchoResponse
from trace_app.utils.swagger_utils import swagger_doc


@request_mapping('/api/trace_app')
class SampleHandler(BaseHandler):
    """
    示例处理器 — 可作为新业务 Handler 的模板
    """

    @request_mapping('/health', method='get', description='健康检查')
    @swagger_doc(
        tags=["系统管理"],
        summary="健康检查",
        description="检查服务是否正常运行",
        response_model=HealthResponse
    )
    @loginrequired
    async def health(self):
        try:
            self.send_response(Response.success({"status": "ok"}, "服务运行正常"))
        except Exception:
            get_logger().error(traceback.format_exc())
            raise

    @request_mapping('/echo', method='post', description='回显请求参数')
    @swagger_doc(
        tags=["系统管理"],
        summary="回显请求参数",
        description="将请求参数原样返回，用于接口调试",
        request_model=EchoRequest,
        response_model=EchoResponse
    )
    @loginrequired
    async def echo(self):
        try:
            if not self.data:
                self.send_response(Response.fail("请求参数不能为空"))
                return
            self.send_response(Response.success(self.data, "回显成功"))
        except Exception:
            get_logger().error(traceback.format_exc())
            raise
