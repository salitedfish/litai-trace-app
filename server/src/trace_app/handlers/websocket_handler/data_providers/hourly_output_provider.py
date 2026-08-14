#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""小时产量数据推送提供器"""
import datetime

from mg_app_framework import get_logger
from tornado.ioloop import IOLoop

from trace_app.handlers.websocket_handler.data_providers.base_provider import DataProvider
from trace_app.service.hourly_output_service import get_hourly_output


class HourlyOutputProvider(DataProvider):
    """小时产量数据推送提供器
    每 10 秒推送一次各小时产量
    查询日期由客户端 set_date 指定（来自看板配置，前端传递）
    """

    name = "hourly_output"
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
        """计算并推送小时产量数据"""
        try:
            query_start = None
            query_end = None

            if self._query_start:
                query_start = self._query_start.replace(hour=0, minute=0, second=0, microsecond=0)
            if self._query_end:
                query_end = self._query_end.replace(hour=23, minute=59, second=59, microsecond=0)

            data = await get_hourly_output(
                start_time=query_start,
                end_time=query_end,
                product_types=self._product_types,
            )

            query_label = "today"
            if self._query_start or self._query_end:
                s = self._query_start.strftime("%Y-%m-%d") if self._query_start else "..."
                e = self._query_end.strftime("%Y-%m-%d") if self._query_end else "..."
                query_label = f"{s} ~ {e}"

            self.send({
                "type": "hourly_output",
                "data": data,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query_date": query_label,
            })
        except Exception as e:
            get_logger().exception("推送小时产量异常: %s", e)
