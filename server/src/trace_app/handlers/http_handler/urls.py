from tornado_request_mapping import Route

from trace_app.handlers.http_handler.handler import SampleHandler
from trace_app.handlers.http_handler.trace_handler import TraceHandler
from trace_app.utils.swagger_utils import generate_handler_classes

url = []
r = Route()
r.register(SampleHandler)
r.register(TraceHandler)
for path, handler_cls, methods in generate_handler_classes(SampleHandler):
    r.register(handler_cls)
for path, handler_cls, methods in generate_handler_classes(TraceHandler):
    r.register(handler_cls)
url.extend(r.host_handlers)
