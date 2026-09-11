import traceback

from mg_app_framework import get_logger, loginrequired
from tornado_request_mapping import request_mapping

from trace_app.common.base_handler import BaseHandler
from trace_app.entity.response_entity import Response
from trace_app.entity.response_model import (
    MaterialScanQueryRequest,
    MaterialScanQueryResponse,
)
from trace_app.service.material_scan_record_service import (
    MAX_PAGE_SIZE,
    query_material_scan_records,
)
from trace_app.utils.swagger_utils import swagger_doc


@request_mapping('/api/trace_app')
class MaterialScanHandler(BaseHandler):
    """扫码登料查询处理器 — 查 {org}_manual_trace.material_scan_records"""

    @request_mapping('/material_scan/query', method='post', description='查询扫码登料记录')
    @swagger_doc(
        tags=["扫码登料查询"],
        summary="查询扫码登料记录",
        description="按码值（模糊）+ 时间范围分页查询扫码登料记录，"
                    "数据源为 manual_line_general_traceability 落库的 material_scan_records",
        request_model=MaterialScanQueryRequest,
        response_model=MaterialScanQueryResponse,
    )
    @loginrequired
    async def query_material_scan(self):
        """扫码登料记录查询 — 码值 + 时间范围 + 分页"""
        try:
            data = self.data or {}

            code = (data.get("code") or "").strip()
            start_time = (data.get("start_time") or "").strip()
            end_time = (data.get("end_time") or "").strip()

            page = int(data.get("page", 1))
            page_size = int(data.get("page_size", 20))
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 20
            if page_size > MAX_PAGE_SIZE:
                page_size = MAX_PAGE_SIZE

            result = await query_material_scan_records(code, start_time, end_time, page, page_size)
            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))
