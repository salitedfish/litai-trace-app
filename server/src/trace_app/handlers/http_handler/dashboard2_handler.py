import traceback
from datetime import datetime

from mg_app_framework import get_logger, loginrequired
from tornado_request_mapping import request_mapping

from trace_app.common.base_handler import BaseHandler
from trace_app.entity.response_entity import Response
from trace_app.entity.response_model import (
    DashboardConfigRequest,
    DashboardConfigResponse,
    UnqualifiedPieRequest,
    UnqualifiedPieResponse,
    UnqualifiedReasonPieRequest,
    UnqualifiedReasonPieResponse,
)
from trace_app.utils.swagger_utils import swagger_doc
from trace_app.utils.db import get_collection_handler
from trace_app.service.dashboard2_unqualified_pie_service import get_unqualified_pie, get_unqualified_reason_pie


COLLECTION_NAME = 'dashboard_config_2'


@request_mapping('/api/trace_app/dashboard_2')
class Dashboard2Handler(BaseHandler):
    """
    智能看板2配置处理器
    """

    @request_mapping('/config', method='get', description='获取看板2配置')
    @swagger_doc(
        tags=["智能看板2"],
        summary="获取看板2配置",
        description="获取智能看板2的配置信息（标题等）",
        response_model=DashboardConfigResponse
    )
    @loginrequired
    async def get_config(self):
        try:
            coll = await get_collection_handler(COLLECTION_NAME)
            doc = await coll.find_one({}, {'_id': 0})
            if doc is None:
                self.send_response(Response.success({"title": "智能看板2"}, "默认配置"))
                return
            self.send_response(Response.success(doc, "获取成功"))
        except Exception:
            get_logger().error(traceback.format_exc())
            raise

    @request_mapping('/config', method='post', description='保存看板2配置')
    @swagger_doc(
        tags=["智能看板2"],
        summary="保存看板2配置",
        description="保存智能看板2的配置信息",
        request_model=DashboardConfigRequest,
        response_model=DashboardConfigResponse
    )
    @loginrequired
    async def save_config(self):
        try:
            data = self.data or {}
            title = str(data.get('title') or '').strip()
            if not title:
                self.send_response(Response.fail("看板标题不能为空"))
                return

            start_date = str(data.get('start_date') or '').strip()
            end_date = str(data.get('end_date') or '').strip()
            workshop_code = str(data.get('workshop_code') or '').strip()

            # 产品型号支持多选，存数组；空列表表示清除
            product_type_raw = data.get('product_type') or []
            if not isinstance(product_type_raw, list):
                product_type_raw = []
            product_type = [str(x).strip() for x in product_type_raw if str(x).strip()]

            coll = await get_collection_handler(COLLECTION_NAME)
            doc = await coll.find_one({}, {'_id': 1})
            now = datetime.now().isoformat()

            # 空值表示清除该配置项
            set_fields = {'title': title, 'updated_at': now}
            unset_fields = []
            for field, value in [
                ('start_date', start_date),
                ('end_date', end_date),
                ('workshop_code', workshop_code),
                ('product_type', product_type),
            ]:
                if value:
                    set_fields[field] = value
                else:
                    unset_fields.append(field)

            if doc:
                update = {'$set': set_fields}
                if unset_fields:
                    update['$unset'] = {field: '' for field in unset_fields}
                await coll.update_one({'_id': doc['_id']}, update)
            else:
                insert_data = {
                    'title': title,
                    'created_at': now,
                    'updated_at': now,
                }
                for field in ('start_date', 'end_date', 'workshop_code', 'product_type'):
                    if set_fields.get(field):
                        insert_data[field] = set_fields[field]
                await coll.insert_one(insert_data)

            self.send_response(Response.success({"title": title}, "保存成功"))
        except Exception:
            get_logger().error(traceback.format_exc())
            raise

    # =====================================================================
    # 检验项不合格占比统计
    # 数据源 {org}_manual_trace.inspection_records（manual_line 报工时落库）
    # 筛选：日期 / 产线 / 产品型号（空即不限），返回各检验项不合格次数
    # =====================================================================

    @request_mapping('/unqualified_pie', method='post', description='统计检验项不合格占比')
    @swagger_doc(
        tags=["智能看板2"],
        summary="统计检验项不合格占比",
        description="从检验单（inspection_records）取出不合格检验项，按检验项聚合计数，"
                    "供看板2 饼图展示；支持日期 / 产线 / 产品型号筛选，空即不限",
        request_model=UnqualifiedPieRequest,
        response_model=UnqualifiedPieResponse,
    )
    @loginrequired
    async def query_unqualified_pie(self):
        """统计各检验项不合格次数（日期/产线/产品型号筛选，空即不限）"""
        try:
            data = self.data or {}
            start_date = str(data.get('start_date') or '').strip()
            end_date = str(data.get('end_date') or '').strip()
            workshop_code = str(data.get('workshop_code') or '').strip()

            # 产品型号支持多选，传数组；非数组视为不限
            product_type_raw = data.get('product_types') or []
            if not isinstance(product_type_raw, list):
                product_type_raw = []
            product_types = [str(x).strip() for x in product_type_raw if str(x).strip()]

            result = await get_unqualified_pie(
                start_date=start_date or None,
                end_date=end_date or None,
                workshop_code=workshop_code or None,
                product_types=product_types or None,
            )
            self.send_response(Response.success(result, "查询成功"))
        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    # =====================================================================
    # 不合格原因占比统计
    # 数据源同 {org}_manual_trace.inspection_records，按不合格项勾选的原因快照聚合
    # 筛选：日期 / 产线 / 产品型号（空即不限），返回各原因被勾选次数
    # =====================================================================

    @request_mapping('/unqualified_reason_pie', method='post', description='统计不合格原因占比')
    @swagger_doc(
        tags=["智能看板2"],
        summary="统计不合格原因占比",
        description="从检验单（inspection_records）不合格项勾选的原因快照 unqualified_reasons 聚合计数，"
                    "供看板2 饼图展示；支持日期 / 产线 / 产品型号筛选，空即不限",
        request_model=UnqualifiedReasonPieRequest,
        response_model=UnqualifiedReasonPieResponse,
    )
    @loginrequired
    async def query_unqualified_reason_pie(self):
        """统计各不合格原因被勾选次数（日期/产线/产品型号筛选，空即不限）"""
        try:
            data = self.data or {}
            start_date = str(data.get('start_date') or '').strip()
            end_date = str(data.get('end_date') or '').strip()
            workshop_code = str(data.get('workshop_code') or '').strip()

            # 产品型号支持多选，传数组；非数组视为不限
            product_type_raw = data.get('product_types') or []
            if not isinstance(product_type_raw, list):
                product_type_raw = []
            product_types = [str(x).strip() for x in product_type_raw if str(x).strip()]

            result = await get_unqualified_reason_pie(
                start_date=start_date or None,
                end_date=end_date or None,
                workshop_code=workshop_code or None,
                product_types=product_types or None,
            )
            self.send_response(Response.success(result, "查询成功"))
        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))
