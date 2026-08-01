#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""数据推送提供器基类"""


class DataProvider:
    """数据推送提供器基类
    子类需定义 name、push_interval，并实现 push() 和 handle_action()
    """

    name = ""  # 唯一标识，用于消息 type 字段
    push_interval = None  # 推送间隔（秒），None 表示用默认间隔

    def __init__(self):
        self._manager = None

    def bind(self, manager):
        """绑定到连接管理器"""
        self._manager = manager

    def setup(self):
        """连接建立时调用，子类可在此初始化状态"""
        pass

    async def push(self):
        """推送数据到客户端 - 子类实现"""
        pass

    def handle_action(self, action, message):
        """处理客户端 action - 返回 True 表示已处理"""
        return False

    def send(self, data):
        """向客户端发送 JSON 消息"""
        import json
        self._manager.handler.write_message(json.dumps(data, ensure_ascii=False))
