#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""设备状态数据推送提供器"""
import datetime

from mg_app_framework import get_logger
from tornado.ioloop import IOLoop

from trace_app.handlers.websocket_handler.data_providers.base_provider import DataProvider
from trace_app.service.device_status_service import get_device_status_map, load_initial_device_status


class DeviceStatusProvider(DataProvider):
    """设备状态数据推送提供器
    每 5 秒推送一次全量设备状态映射，前端收到后按 device_code 更新对应设备图标
    """

    name = "device_status"
    push_interval = 5

    def __init__(self):
        super().__init__()

    def setup(self):
        """连接建立时立即推送一次"""
        IOLoop.current().spawn_callback(self.push)

    async def push(self):
        """计算并推送设备状态数据"""
        try:
            await load_initial_device_status()
            self.send({
                "type": "device_status",
                "data": {"device_map": get_device_status_map()},
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        except Exception as e:
            get_logger().exception("推送设备状态异常: %s", e)
