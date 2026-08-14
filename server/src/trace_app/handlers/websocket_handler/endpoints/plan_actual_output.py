#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""计划/实际产量数据 WebSocket 端点"""
from trace_app.handlers.websocket_handler.handler import BaseWsHandler
from trace_app.handlers.websocket_handler.data_providers.plan_actual_output_provider import PlanActualOutputProvider


class PlanActualOutputWsHandler(BaseWsHandler):
    """计划/实际产量数据推送，路径 /ws/plan_actual_output"""
    provider_cls = PlanActualOutputProvider
