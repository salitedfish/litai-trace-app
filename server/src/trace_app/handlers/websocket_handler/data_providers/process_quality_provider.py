#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""工序合格率数据推送提供器"""
import datetime

from mg_app_framework import get_logger
from tornado.ioloop import IOLoop

from trace_app.handlers.websocket_handler.data_providers.base_provider import DataProvider
from trace_app.service.process_quality_service import get_process_quality


class ProcessQualityProvider(DataProvider):
    """工序合格率数据推送提供器
    每 10 秒推送一次各工序合格率
    查询日期由客户端 set_date 指定（来自看板配置，前端传递）
    """

    name = "process_quality"
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
        """计算并推送工序合格率数据"""
        try:
            query_start = None
            query_end = None

            if self._query_start:
                query_start = self._query_start.replace(hour=0, minute=0, second=0, microsecond=0)
            if self._query_end:
                query_end = self._query_end.replace(hour=23, minute=59, second=59, microsecond=0)

            data = await get_process_quality(start_time=query_start, end_time=query_end)

            query_label = "today"
            if self._query_start or self._query_end:
                s = self._query_start.strftime("%Y-%m-%d") if self._query_start else "..."
                e = self._query_end.strftime("%Y-%m-%d") if self._query_end else "..."
                query_label = f"{s} ~ {e}"

            self.send({
                "type": "process_quality",
                "data": data,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query_date": query_label,
            })
        except Exception as e:
            get_logger().exception("推送工序合格率异常: %s", e)
