#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""小时产量数据 WebSocket 端点"""
from trace_app.handlers.websocket_handler.handler import BaseWsHandler
from trace_app.handlers.websocket_handler.data_providers.hourly_output_provider import HourlyOutputProvider


class HourlyOutputWsHandler(BaseWsHandler):
    """小时产量数据推送，路径 /ws/hourly_output"""
    provider_cls = HourlyOutputProvider
