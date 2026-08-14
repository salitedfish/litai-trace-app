import traceback

from mg_app_framework import get_logger, loginrequired
from tornado_request_mapping import request_mapping

from trace_app.common.base_handler import BaseHandler
from trace_app.entity.response_entity import Response
from trace_app.entity.response_model import (
    LineDevicesRequest,
    LineDevicesResponse,
    LineListResponse,
    ProductTypeListResponse,
    RoutingListResponse,
    RoutingProcessRequest,
    RoutingProcessResponse,
)
from trace_app.utils.swagger_utils import swagger_doc
from trace_app.utils.collection_utils import (
    get_process_coll,
    get_production_config_type_coll,
    get_routing_process_info_coll,
    get_web_layout_application_coll,
)


@request_mapping('/api/trace_app/base_config')
class BaseConfigHandler(BaseHandler):
    """生产基础配置查询处理器 — 工艺路线列表、工艺路线工序列表（含生产单元及设备）"""

    # =====================================================================
    # 工艺路线列表查询
    # =====================================================================

    @request_mapping('/routing_list', method='post', description='获取工艺路线列表')
    @swagger_doc(
        tags=["生产基础配置"],
        summary="获取工艺路线列表",
        description="查询所有工艺路线（按工艺路线编码去重），返回编码、名称、类型及车间信息",
        response_model=RoutingListResponse,
    )
    @loginrequired
    async def query_routing_list(self):
        """查询工艺路线列表，用于前端下拉选择"""
        try:
            routing_coll = await get_routing_process_info_coll()
            pipeline = [
                {"$group": {
                    "_id": "$工艺路线编码",
                    "工艺路线名称": {"$first": "$工艺路线名称"},
                    "工艺路线类型": {"$first": "$工艺路线类型"},
                    "车间编码": {"$first": "$车间编码"},
                    "车间名称": {"$first": "$车间名称"},
                }},
                {"$sort": {"_id": 1}},
            ]
            cursor = routing_coll.aggregate(pipeline)
            result = []
            async for r in cursor:
                result.append({
                    "routing_code": r.get("_id", ""),
                    "routing_name": r.get("工艺路线名称", ""),
                    "routing_type": r.get("工艺路线类型", ""),
                    "workshop_code": r.get("车间编码", ""),
                    "workshop_name": r.get("车间名称", ""),
                })

            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    # =====================================================================
    # 工艺路线工序列表查询
    # 明细表(工艺路线工序) → 工序信息表(生产单元编码) → 布局表(设备编码/名称)
    # =====================================================================

    @request_mapping('/routing_processes', method='post', description='获取工艺路线对应的工序列表')
    @swagger_doc(
        tags=["生产基础配置"],
        summary="获取工艺路线对应的工序列表",
        description="按工艺路线编码查询工序列表（按工序顺序排序），联查工序信息获取生产单元，"
                    "再联查布局表获取每个生产单元对应的设备编码和名称",
        request_model=RoutingProcessRequest,
        response_model=RoutingProcessResponse,
    )
    @loginrequired
    async def query_routing_processes(self):
        """工艺路线工序列表 — 工序排序 + 生产单元 + 设备数组"""
        try:
            if not self.data or not self.data.get("routing_code"):
                self.send_response(Response.fail("请传入工艺路线编码 routing_code"))
                return

            routing_code = self.data["routing_code"].strip()
            if not routing_code:
                self.send_response(Response.fail("工艺路线编码不能为空"))
                return

            # ---- 1. 查工艺路线明细，按工序顺序排序 ----
            routing_coll = await get_routing_process_info_coll()
            details = await routing_coll.find(
                {"工艺路线编码": routing_code},
                projection={"工艺路线名称": 1, "工序号": 1, "工作中心编码": 1,
                            "工作中心名称": 1, "工序顺序": 1, "工序编码": 1, "工序名称": 1}
            ).sort("工序顺序", 1).to_list(length=1000)
            if not details:
                self.send_response(Response.success({
                    "routing_code": routing_code,
                    "routing_name": "",
                    "processes": [],
                }, "查询成功"))
                return

            routing_name = details[0].get("工艺路线名称", "")

            # ---- 2. 联查工序信息表，获取生产单元编码 ----
            process_codes = []
            for d in details:
                pc = d.get("工序编码", "")
                if pc and pc not in process_codes:
                    process_codes.append(pc)

            process_map = {}
            if process_codes:
                process_coll = await get_process_coll()
                cursor = process_coll.find(
                    {"工序编码": {"$in": process_codes}},
                    projection={"工序编码": 1, "生产单元编码": 1}
                )
                async for p in cursor:
                    process_map[p.get("工序编码", "")] = p

            # ---- 3. 收集生产单元编码 ----
            unit_codes = []
            for d in details:
                pinfo = process_map.get(d.get("工序编码", ""), {})
                uc = pinfo.get("生产单元编码", "")
                if uc and uc not in unit_codes:
                    unit_codes.append(uc)

            # ---- 4. 联查布局表，获取生产单元的设备数组（按设备顺序排序） ----
            unit_info_map = {}
            if unit_codes:
                layout_coll = await get_web_layout_application_coll()
                cursor = layout_coll.find(
                    {"生产单元代号": {"$in": unit_codes}},
                    projection={"生产单元代号": 1, "生产单元名称": 1,
                                "设备编码": 1, "设备名称": 1, "设备类型": 1}
                ).sort("设备顺序", 1)
                async for rec in cursor:
                    unit = rec.get("生产单元代号", "")
                    if not unit:
                        continue
                    entry = unit_info_map.get(unit)
                    if entry is None:
                        entry = {"produce_unit_name": rec.get("生产单元名称", ""), "devices": []}
                        unit_info_map[unit] = entry
                    elif not entry["produce_unit_name"]:
                        entry["produce_unit_name"] = rec.get("生产单元名称", "")
                    entry["devices"].append({
                        "device_code": rec.get("设备编码", ""),
                        "device_name": rec.get("设备名称", ""),
                        "device_type": rec.get("设备类型", ""),
                    })

            # ---- 5. 组装工序列表 ----
            processes = []
            for d in details:
                pinfo = process_map.get(d.get("工序编码", ""), {})
                uc = pinfo.get("生产单元编码", "")
                unit_info = unit_info_map.get(uc, {})
                processes.append({
                    "process_code": d.get("工序编码", ""),
                    "process_name": d.get("工序名称", ""),
                    "process_order": d.get("工序顺序", 0),
                    "work_center_code": d.get("工作中心编码", ""),
                    "work_center_name": d.get("工作中心名称", ""),
                    "produce_unit_code": uc,
                    "produce_unit_name": unit_info.get("produce_unit_name", ""),
                    "devices": unit_info.get("devices", []),
                })

            self.send_response(Response.success({
                "routing_code": routing_code,
                "routing_name": routing_name,
                "processes": processes,
            }, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    # =====================================================================
    # 产品型号列表查询
    # production_config_type 表按产品型号去重
    # =====================================================================

    @request_mapping('/product_type_list', method='post', description='获取产品型号列表')
    @swagger_doc(
        tags=["生产基础配置"],
        summary="获取产品型号列表",
        description="从 production_config_type 表按产品型号去重，返回产品型号及对应工艺路线编码",
        response_model=ProductTypeListResponse,
    )
    @loginrequired
    async def query_product_type_list(self):
        """查询产品型号列表（production_config_type），用于前端单选框选择"""
        try:
            coll = await get_production_config_type_coll()
            pipeline = [
                {"$group": {
                    "_id": "$production_type",
                    "routing_code": {"$first": "$routing_code"},
                }},
                {"$sort": {"_id": 1}},
            ]
            result = []
            async for r in coll.aggregate(pipeline):
                production_type = r.get("_id", "")
                if not production_type:
                    continue
                result.append({
                    "production_type": production_type,
                    "routing_code": r.get("routing_code", ""),
                })

            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    # =====================================================================
    # 产线列表查询（车间 = 产线）
    # 布局表(web_layout_application) 按车间代号去重
    # =====================================================================

    @request_mapping('/line_list', method='post', description='获取产线列表')
    @swagger_doc(
        tags=["生产基础配置"],
        summary="获取产线列表",
        description="从布局表按车间代号（产线）去重，返回产线编码及名称",
        response_model=LineListResponse,
    )
    @loginrequired
    async def query_line_list(self):
        """查询产线列表（车间=产线），用于前端下拉选择"""
        try:
            layout_coll = await get_web_layout_application_coll()
            pipeline = [
                {"$group": {
                    "_id": "$车间代号",
                    "车间名称": {"$first": "$车间名称"},
                }},
                {"$sort": {"_id": 1}},
            ]
            result = []
            async for r in layout_coll.aggregate(pipeline):
                workshop_code = r.get("_id", "")
                if not workshop_code:
                    continue
                result.append({
                    "workshop_code": workshop_code,
                    "workshop_name": r.get("车间名称", ""),
                })

            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    # =====================================================================
    # 产线设备查询
    # 布局表(web_layout_application) 按车间代号筛选，按生产单元分组返回设备
    # =====================================================================

    @request_mapping('/line_devices', method='post', description='获取产线下生产单元及设备')
    @swagger_doc(
        tags=["生产基础配置"],
        summary="获取产线下生产单元及设备",
        description="按车间代号（产线）查询布局表，按生产单元分组返回设备列表",
        request_model=LineDevicesRequest,
        response_model=LineDevicesResponse,
    )
    @loginrequired
    async def query_line_devices(self):
        """查询产线下的生产单元及设备，用于看板展示"""
        try:
            if not self.data or not self.data.get("workshop_code"):
                self.send_response(Response.fail("请传入产线编码 workshop_code"))
                return

            workshop_code = self.data["workshop_code"].strip()
            if not workshop_code:
                self.send_response(Response.fail("产线编码不能为空"))
                return

            layout_coll = await get_web_layout_application_coll()
            cursor = layout_coll.find(
                {"车间代号": workshop_code},
                projection={"车间名称": 1, "生产单元代号": 1, "生产单元名称": 1,
                            "设备编码": 1, "设备名称": 1, "设备类型": 1}
            ).sort("设备顺序", 1)

            workshop_name = ""
            unit_map = {}
            async for rec in cursor:
                if not workshop_name:
                    workshop_name = rec.get("车间名称", "")
                unit_code = rec.get("生产单元代号", "")
                if not unit_code:
                    continue
                entry = unit_map.get(unit_code)
                if entry is None:
                    entry = {
                        "produce_unit_code": unit_code,
                        "produce_unit_name": rec.get("生产单元名称", ""),
                        "devices": [],
                    }
                    unit_map[unit_code] = entry
                elif not entry["produce_unit_name"]:
                    entry["produce_unit_name"] = rec.get("生产单元名称", "")
                device_code = rec.get("设备编码", "")
                if device_code:
                    entry["devices"].append({
                        "device_code": device_code,
                        "device_name": rec.get("设备名称", ""),
                        "device_type": rec.get("设备类型", ""),
                    })

            self.send_response(Response.success({
                "workshop_code": workshop_code,
                "workshop_name": workshop_name,
                "units": list(unit_map.values()),
            }, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))
