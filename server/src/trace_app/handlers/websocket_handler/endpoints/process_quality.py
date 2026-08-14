#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""工序合格率数据 WebSocket 端点"""
from trace_app.handlers.websocket_handler.handler import BaseWsHandler
from trace_app.handlers.websocket_handler.data_providers.process_quality_provider import ProcessQualityProvider


class ProcessQualityWsHandler(BaseWsHandler):
    """工序合格率数据推送，路径 /ws/process_quality"""
    provider_cls = ProcessQualityProvider
