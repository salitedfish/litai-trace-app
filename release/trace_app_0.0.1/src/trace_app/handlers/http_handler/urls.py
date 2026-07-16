from tornado_request_mapping import Route

from trace_app.handlers.http_handler.handler import SampleHandler

url = []
r = Route()
r.register(SampleHandler)
url.extend(r.host_handlers)
