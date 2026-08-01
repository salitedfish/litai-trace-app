#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""OEE 数据推送提供器"""
import json
import datetime

from mg_app_framework import get_logger
from tornado.ioloop import IOLoop

from trace_app.handlers.websocket_handler.data_providers.base_provider import DataProvider
from trace_app.service.oee_service import calculate_oee


class OeeProvider(DataProvider):
    """OEE 数据推送提供器
    每 10 秒推送一次 OEE/时间开动率/性能开动率/合格率
    支持 set_date / refresh 客户端 action
    """

    name = "oee"
    push_interval = 10

    def __init__(self):
        super().__init__()
        self._query_start = None
        self._query_end = None

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

        return False

    async def push(self):
        """计算并推送 OEE 数据"""
        try:
            query_start = None
            query_end = None

            if self._query_start:
                query_start = self._query_start.replace(hour=0, minute=0, second=0, microsecond=0)
            if self._query_end:
                query_end = self._query_end.replace(hour=23, minute=59, second=59, microsecond=0)

            oee_data = await calculate_oee(start_time=query_start, end_time=query_end)

            query_label = "today"
            if self._query_start or self._query_end:
                s = self._query_start.strftime("%Y-%m-%d") if self._query_start else "..."
                e = self._query_end.strftime("%Y-%m-%d") if self._query_end else "..."
                query_label = f"{s} ~ {e}"

            self.send({
                "type": "oee",
                "data": oee_data,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query_date": query_label,
            })
        except Exception as e:
            get_logger().exception("推送 OEE 数据异常: %s", e)
