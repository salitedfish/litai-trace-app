#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
WebSocket 处理器基类
每个端点用一个 Handler 子类 + 一个 DataProvider 的组合。
新增推送类型：新建 DataProvider，再新建一个 Handler 子类指定 provider_cls。
"""
import json

from mg_app_framework import WebsocketBasicHandler

from trace_app.handlers.websocket_handler.connection_manager import ConnectionManager


class BaseWsHandler(WebsocketBasicHandler):
    """WebSocket 处理器基类
    子类只需设置 provider_cls，框架自动完成连接管理和数据推送
    """
    provider_cls = None

    def open(self):
        self._manager = ConnectionManager(self)
        self._manager.register(self.provider_cls())
        self._manager.start()

    def on_message(self, message):
        try:
            msg = json.loads(message)
            self._manager.handle_message(msg)
        except (json.JSONDecodeError, TypeError):
            pass

    def on_close(self):
        if hasattr(self, '_manager'):
            self._manager.stop()
