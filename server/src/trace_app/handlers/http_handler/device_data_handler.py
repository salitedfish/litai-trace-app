import traceback

from mg_app_framework import get_logger, loginrequired
from tornado_request_mapping import request_mapping

from trace_app.common.base_handler import BaseHandler
from trace_app.entity.response_entity import Response
from trace_app.entity.response_model import (
    DeviceListResponse,
    DeviceDataQueryRequest,
    DeviceDataQueryResponse,
)
from trace_app.utils.swagger_utils import swagger_doc
from trace_app.utils.collection_utils import get_device_coll, get_datas_coll


@request_mapping('/api/trace_app')
class DeviceDataHandler(BaseHandler):
    """设备数采查询处理器 — 设备列表查询、数采信号数据查询"""

    # =====================================================================
    # 设备列表查询
    # =====================================================================

    @request_mapping('/device_data/list', method='post', description='获取设备列表')
    @swagger_doc(
        tags=["数采查询"],
        summary="获取设备列表",
        description="查询所有可用的数采设备，返回设备编码和名称",
        response_model=DeviceListResponse,
    )
    @loginrequired
    async def query_device_list(self):
        """查询设备列表，用于前端下拉选择"""
        try:
            device_coll = await get_device_coll()
            devices = await device_coll.find(
                {"type": "device"},
                projection={"code": 1, "name": 1}
            ).sort("index", 1).to_list(length=500)

            result = []
            for d in devices:
                result.append({
                    "code": d.get("code", ""),
                    "name": d.get("name", ""),
                })

            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    # =====================================================================
    # 设备数采数据查询
    # 按设备编码 + 时间范围查询 datas 表，分页返回
    # =====================================================================

    @request_mapping('/device_data/query', method='post', description='查询设备数采数据')
    @swagger_doc(
        tags=["数采查询"],
        summary="查询设备数采数据",
        description="按设备编码和时间范围查询数采数据，支持分页",
        request_model=DeviceDataQueryRequest,
        response_model=DeviceDataQueryResponse,
    )
    @loginrequired
    async def query_device_data(self):
        """设备数采数据查询 — 设备 + 时间范围 + 分页"""
        try:
            # ---- 参数校验 ----
            if not self.data:
                self.send_response(Response.fail("参数不能为空"))
                return

            device_code = (self.data.get("device_code") or "").strip()
            start_time = (self.data.get("start_time") or "").strip()
            end_time = (self.data.get("end_time") or "").strip()

            if not device_code:
                self.send_response(Response.fail("请选择设备"))
                return
            if not start_time or not end_time:
                self.send_response(Response.fail("请选择查询时间范围"))
                return

            page = int(self.data.get("page", 1))
            page_size = int(self.data.get("page_size", 20))
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 20
            if page_size > 200:
                page_size = 200

            # ---- 构建查询条件 ----
            from datetime import datetime
            try:
                dt_start = datetime.fromisoformat(start_time)
                dt_end = datetime.fromisoformat(end_time)
            except ValueError:
                self.send_response(Response.fail("时间格式不正确，请使用 ISO 8601 格式"))
                return

            query_filter = {
                "code": {"$regex": f"^{device_code}~"},
                "timestamp": {"$gte": dt_start, "$lte": dt_end},
            }

            # ---- 查询并分页 ----
            datas_coll = await get_datas_coll()

            total = await datas_coll.count_documents(query_filter)

            skip = (page - 1) * page_size
            cursor = datas_coll.find(
                query_filter,
                projection={"code": 1, "value": 1, "timestamp": 1}
            ).sort("timestamp", -1).skip(skip).limit(page_size)

            records = await cursor.to_list(length=page_size)

            result_list = []
            for r in records:
                ts = r.get("timestamp")
                result_list.append({
                    "code": r.get("code", ""),
                    "value": r.get("value", ""),
                    "timestamp": str(ts) if ts else "",
                })

            self.send_response(Response.success({
                "total": total,
                "page": page,
                "page_size": page_size,
                "list": result_list,
            }, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))
