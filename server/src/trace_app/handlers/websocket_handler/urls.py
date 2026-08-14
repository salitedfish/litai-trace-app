"""WebSocket 路由注册
每个端点一条路由，指向对应的 Handler。
"""
from trace_app.handlers.websocket_handler.endpoints.device_status import DeviceStatusWsHandler
from trace_app.handlers.websocket_handler.endpoints.oee import OeeWsHandler
from trace_app.handlers.websocket_handler.endpoints.process_quality import ProcessQualityWsHandler
from trace_app.handlers.websocket_handler.endpoints.hourly_output import HourlyOutputWsHandler

url = [
    (r'/ws/oee', OeeWsHandler),
    (r'/ws/device_status', DeviceStatusWsHandler),
    (r'/ws/process_quality', ProcessQualityWsHandler),
    (r'/ws/hourly_output', HourlyOutputWsHandler),
]
