#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
WebSocket 连接管理器
管理单条 WebSocket 连接的生命周期、定时器、客户端状态。
数据推送由注册的 DataProvider 实现。
"""
from tornado.ioloop import IOLoop


class ConnectionManager:
    """管理一条 WebSocket 连接的定时推送和生命周期"""

    def __init__(self, handler, default_interval=10):
        """
        Args:
            handler: BaseWsHandler 实例
            default_interval: 默认推送间隔（秒）
        """
        self.handler = handler
        self.default_interval = default_interval
        self._timer = None
        self._providers = {}  # name -> DataProvider 实例

    def register(self, provider):
        """注册一个数据提供器

        Args:
            provider: DataProvider 实例，需实现 setup()、push()、handle_action(action, data)
        """
        name = provider.name
        self._providers[name] = provider
        provider.bind(self)

    def start(self):
        """启动所有 provider 的定时推送"""
        for p in self._providers.values():
            p.setup()
        self._schedule_next()

    def stop(self):
        """停止所有定时器"""
        if self._timer:
            try:
                IOLoop.current().remove_timeout(self._timer)
            except Exception:
                pass
            self._timer = None

    def handle_message(self, message):
        """分发客户端消息到对应的 provider"""
        action = message.get("action", "")
        for p in self._providers.values():
            if p.handle_action(action, message):
                return

    def _schedule_next(self):
        """安排下一次推送"""
        interval = self.default_interval
        for p in self._providers.values():
            pi = p.push_interval
            if pi and pi < interval:
                interval = pi

        loop = IOLoop.current()
        self._timer = loop.call_later(interval, self._push_all)

    def _push_all(self):
        """推送所有 provider 的数据"""
        for p in self._providers.values():
            IOLoop.current().spawn_callback(p.push)
        self._schedule_next()
