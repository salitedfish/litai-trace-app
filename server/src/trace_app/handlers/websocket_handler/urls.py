"""WebSocket 路由注册
每个端点一条路由，指向对应的 Handler。
"""
from trace_app.handlers.websocket_handler.endpoints.oee import OeeWsHandler

url = [
    (r'/ws/oee', OeeWsHandler),
]
