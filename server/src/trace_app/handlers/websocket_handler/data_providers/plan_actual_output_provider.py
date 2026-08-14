#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""计划/实际产量数据推送提供器"""
import datetime

from mg_app_framework import get_logger
from tornado.ioloop import IOLoop

from trace_app.handlers.websocket_handler.data_providers.base_provider import DataProvider
from trace_app.service.plan_actual_output_service import get_plan_actual_output


class PlanActualOutputProvider(DataProvider):
    """计划/实际产量数据推送提供器
    每 10 秒推送一次计划产量 / 实际产量 / 产量进度
    查询日期由客户端 set_date 指定（来自看板配置，不配置默认当天）；
    产品型号由客户端 set_product_type 指定（来自看板配置）
    """

    name = "plan_actual_output"
    push_interval = 10

    def __init__(self):
        super().__init__()
        self._query_start = None
        self._query_end = None
        self._product_types = None

    def setup(self):
        """连接建立时立即推送一次"""
        IOLoop.current().spawn_callback(self.push)

    def handle_action(self, action, message):
        if action == "refresh":
            IOLoop.current().spawn_callback(self.push)
            return True

        if action == "set_date":
            start_str = message.get("date_start", "")
            end_str = message.get("date_end", "")
            self._query_start = None
            self._query_end = None
            if start_str:
                try:
                    self._query_start = datetime.datetime.strptime(start_str, "%Y-%m-%d")
                except ValueError:
                    pass
            if end_str:
                try:
                    self._query_end = datetime.datetime.strptime(end_str, "%Y-%m-%d")
                except ValueError:
                    pass
            IOLoop.current().spawn_callback(self.push)
            return True

        if action == "set_product_type":
            # 产品型号过滤；空列表表示查全部
            product_types = message.get("product_types") or []
            if isinstance(product_types, list):
                self._product_types = [str(x).strip() for x in product_types if str(x).strip()]
            else:
                self._product_types = []
            IOLoop.current().spawn_callback(self.push)
            return True

        return False

    async def push(self):
        """计算并推送计划/实际产量数据"""
        try:
            data = await get_plan_actual_output(
                start_time=self._query_start,
                end_time=self._query_end,
                product_types=self._product_types,
            )
            self.send({
                "type": "plan_actual_output",
                "data": data,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        except Exception as e:
            get_logger().exception("推送计划/实际产量异常: %s", e)
