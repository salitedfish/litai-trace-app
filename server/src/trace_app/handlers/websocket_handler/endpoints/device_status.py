#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""设备状态 WebSocket 端点"""
from trace_app.handlers.websocket_handler.handler import BaseWsHandler
from trace_app.handlers.websocket_handler.data_providers.device_status_provider import DeviceStatusProvider


class DeviceStatusWsHandler(BaseWsHandler):
    """设备状态数据推送，路径 /ws/device_status"""
    provider_cls = DeviceStatusProvider
