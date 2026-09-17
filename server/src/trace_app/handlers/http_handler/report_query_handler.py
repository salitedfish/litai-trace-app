import traceback

from mg_app_framework import get_logger, loginrequired
from tornado_request_mapping import request_mapping

from trace_app.common.base_handler import BaseHandler
from trace_app.entity.response_entity import Response
from trace_app.entity.response_model import (
    ReportFilterOptionsResponse,
    ReportQueryRequest,
    ReportQueryResponse,
    UnqualifiedReasonQueryRequest,
    UnqualifiedReasonQueryResponse,
    UnqualifiedReasonReportRequest,
)
from trace_app.service.report_query_service import (
    MAX_PAGE_SIZE,
    query_report_filter_options,
    query_report_records,
    query_report_records_by_reason,
    query_unqualified_reasons,
)
from trace_app.utils.swagger_utils import swagger_doc


def _parse_page(data):
    """从请求体解析页码/每页条数并做边界收敛（与扫码登料查询同口径）"""
    page = int(data.get("page", 1))
    page_size = int(data.get("page_size", 20))
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > MAX_PAGE_SIZE:
        page_size = MAX_PAGE_SIZE
    return page, page_size


@request_mapping('/api/trace_app')
class ReportQueryHandler(BaseHandler):
    """报工查询处理器 — 查 {org}_order_retrospect.work_order_retrospect_records 的产出报工记录"""

    # =====================================================================
    # 报工记录分页查询
    # =====================================================================

    @request_mapping('/report/query', method='post', description='查询报工记录')
    @swagger_doc(
        tags=["报工查询"],
        summary="查询报工记录",
        description="按产品/工艺路线/工序/人员/检测结果/设备 + 时间范围分页查询报工记录"
                    "（只取 op_type=out 的产出记录，一次报工一行）。"
                    "报工记录无工艺路线字段，工艺路线条件经该路线下的工序集合反筛 procedure_code。",
        request_model=ReportQueryRequest,
        response_model=ReportQueryResponse,
    )
    @loginrequired
    async def query_report(self):
        """报工记录查询 — 多条件 + 时间范围 + 分页"""
        try:
            data = self.data or {}
            page, page_size = _parse_page(data)

            result = await query_report_records(
                product_type=(data.get("product_type") or "").strip(),
                routing_code=(data.get("routing_code") or "").strip(),
                process_code=(data.get("process_code") or "").strip(),
                operator_id=(data.get("operator") or "").strip(),
                check_result=(data.get("check_result") or "").strip(),
                device_code=(data.get("device_code") or "").strip(),
                start_time=(data.get("start_time") or "").strip(),
                end_time=(data.get("end_time") or "").strip(),
                page=page,
                page_size=page_size,
            )
            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    # =====================================================================
    # 人员/设备下拉候选
    # =====================================================================

    @request_mapping('/report/filter_options', method='post', description='获取报工查询的人员/设备候选')
    @swagger_doc(
        tags=["报工查询"],
        summary="获取报工查询的人员/设备候选",
        description="取报工记录里实际出现过的操作人与设备，用于页面下拉；"
                    "不受页面其它筛选项约束，无请求参数",
        response_model=ReportFilterOptionsResponse,
    )
    @loginrequired
    async def query_report_filters(self):
        """人员/设备下拉候选 — 报工记录里出现过的值"""
        try:
            result = await query_report_filter_options()
            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    # =====================================================================
    # 报工不合格原因统计
    # =====================================================================

    @request_mapping('/report/unqualified_reason_query', method='post',
                     description='统计报工不合格原因次数')
    @swagger_doc(
        tags=["报工不合格原因"],
        summary="统计报工不合格原因次数",
        description="按产品/工艺路线/工序 + 报工时间范围统计报工时检验单各不合格原因被勾选次数并分页，"
                    "口径与看板2「不合格原因占比」一致；时间留空为不限（全量统计）",
        request_model=UnqualifiedReasonQueryRequest,
        response_model=UnqualifiedReasonQueryResponse,
    )
    @loginrequired
    async def query_unqualified_reason(self):
        """报工不合格原因次数统计 — 三条件 + 时间范围 + 分页"""
        try:
            data = self.data or {}
            page, page_size = _parse_page(data)

            result = await query_unqualified_reasons(
                product_type=(data.get("product_type") or "").strip(),
                routing_code=(data.get("routing_code") or "").strip(),
                process_code=(data.get("process_code") or "").strip(),
                start_time=(data.get("start_time") or "").strip(),
                end_time=(data.get("end_time") or "").strip(),
                page=page,
                page_size=page_size,
            )
            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    @request_mapping('/report/unqualified_reason_records', method='post',
                     description='查不合格原因关联的报工记录')
    @swagger_doc(
        tags=["报工不合格原因"],
        summary="查不合格原因关联的报工记录",
        description="按不合格原因（+ 页面当前的产品/工艺路线/工序/时间范围条件）查勾选了该原因的检验单，"
                    "再经 workorder_code 反查产出报工记录并分页；行结构与报工查询一致。"
                    "一次报工对应一张检验单，故条数可能少于原因次数（同一张单勾多次只算一条报工）",
        request_model=UnqualifiedReasonReportRequest,
        response_model=ReportQueryResponse,
    )
    @loginrequired
    async def query_unqualified_reason_records(self):
        """不合格原因关联的报工记录 — 原因 + 三个条件 + 时间范围 + 分页"""
        try:
            data = self.data or {}
            page, page_size = _parse_page(data)

            result = await query_report_records_by_reason(
                reason_code=(data.get("reason_code") or "").strip(),
                reason_name=(data.get("reason_name") or "").strip(),
                product_type=(data.get("product_type") or "").strip(),
                routing_code=(data.get("routing_code") or "").strip(),
                process_code=(data.get("process_code") or "").strip(),
                start_time=(data.get("start_time") or "").strip(),
                end_time=(data.get("end_time") or "").strip(),
                page=page,
                page_size=page_size,
            )
            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))
