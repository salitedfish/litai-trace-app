import traceback
from datetime import datetime

from mg_app_framework import get_logger, loginrequired
from tornado_request_mapping import request_mapping

from trace_app.common.base_handler import BaseHandler
from trace_app.entity.response_entity import Response
from trace_app.entity.response_model import DashboardConfigRequest, DashboardConfigResponse
from trace_app.utils.swagger_utils import swagger_doc
from trace_app.utils.db import get_collection_handler


COLLECTION_NAME = 'dashboard_config_1'


@request_mapping('/api/trace_app/dashboard')
class DashboardHandler(BaseHandler):
    """
    智能看板配置处理器
    """

    @request_mapping('/config', method='get', description='获取看板配置')
    @swagger_doc(
        tags=["智能看板"],
        summary="获取看板配置",
        description="获取智能看板的配置信息（标题等）",
        response_model=DashboardConfigResponse
    )
    @loginrequired
    async def get_config(self):
        try:
            coll = await get_collection_handler(COLLECTION_NAME)
            doc = await coll.find_one({}, {'_id': 0})
            if doc is None:
                self.send_response(Response.success({"title": "智能生产看板"}, "默认配置"))
                return
            self.send_response(Response.success(doc, "获取成功"))
        except Exception:
            get_logger().error(traceback.format_exc())
            raise

    @request_mapping('/config', method='post', description='保存看板配置')
    @swagger_doc(
        tags=["智能看板"],
        summary="保存看板配置",
        description="保存智能看板的配置信息",
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

            coll = await get_collection_handler(COLLECTION_NAME)
            doc = await coll.find_one({}, {'_id': 1})
            now = datetime.now().isoformat()

            # 空值表示清除该配置项
            set_fields = {'title': title, 'updated_at': now}
            unset_fields = []
            for field, value in [('start_date', start_date), ('end_date', end_date), ('workshop_code', workshop_code)]:
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
                for field in ('start_date', 'end_date', 'workshop_code'):
                    if set_fields.get(field):
                        insert_data[field] = set_fields[field]
                await coll.insert_one(insert_data)

            self.send_response(Response.success({"title": title}, "保存成功"))
        except Exception:
            get_logger().error(traceback.format_exc())
            raise
