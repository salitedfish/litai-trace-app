#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""工序加工情况数据 WebSocket 端点"""
from trace_app.handlers.websocket_handler.handler import BaseWsHandler
from trace_app.handlers.websocket_handler.data_providers.process_production_provider import ProcessProductionProvider


class ProcessProductionWsHandler(BaseWsHandler):
    """工序加工情况数据推送，路径 /ws/process_production"""
    provider_cls = ProcessProductionProvider
