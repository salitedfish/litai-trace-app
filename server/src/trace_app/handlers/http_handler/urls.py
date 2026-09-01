from tornado_request_mapping import Route

from trace_app.handlers.http_handler.handler import SampleHandler
from trace_app.handlers.http_handler.trace_handler import TraceHandler
from trace_app.handlers.http_handler.device_data_handler import DeviceDataHandler
from trace_app.handlers.http_handler.dashboard_handler import DashboardHandler
from trace_app.handlers.http_handler.dashboard2_handler import Dashboard2Handler
from trace_app.handlers.http_handler.base_config_handler import BaseConfigHandler
from trace_app.utils.swagger_utils import generate_handler_classes

url = []
r = Route()
r.register(SampleHandler)
r.register(TraceHandler)
r.register(DeviceDataHandler)
r.register(DashboardHandler)
r.register(Dashboard2Handler)
r.register(BaseConfigHandler)

# SampleHandler（示例/工具接口，无数据查询）
#   /api/trace_app/health（GET）  健康检查
#   /api/trace_app/echo（POST）   回显请求参数
for path, handler_cls, methods in generate_handler_classes(SampleHandler):
    r.register(handler_cls)

# TraceHandler（追溯查询，核心查报工记录表 {org}_order_retrospect.work_order_retrospect_records，联工序信息表/工艺参数表）
#   /api/trace_app/trace/query_by_output（POST）       输入产出码 qr_code，递归追溯完整产出链路
#   /api/trace_app/trace/query_outputs_by_input（POST） 输入投入码，查其被投入的所有报工记录，返回关联产出码
#   /api/trace_app/trace/query_submission_records（POST） 输入 qr_code+工序+设备，查同工序同设备的提交记录
#   /api/trace_app/trace/query_process_params（POST）   输入工单编码 workorder_code，查 {org}_traceback.gycs_data 工艺参数
#   /api/trace_app/trace/query_inputs（POST）           输入工单编码 workorder_code，查该次报工的所有投入物料记录
for path, handler_cls, methods in generate_handler_classes(TraceHandler):
    r.register(handler_cls)

# DeviceDataHandler（数采设备数据，查 idi_{org}_cloud_management.device 设备表 / idi_{org}.datas 数采数据表）
#   /api/trace_app/device_data/list（POST）   查设备表，返回所有可用的数采设备
#   /api/trace_app/device_data/points（POST） 按设备编码查设备表，返回该设备的点位列表
#   /api/trace_app/device_data/query（POST）  按设备+点位+时间范围查 datas 表数采数据（支持分页）
for path, handler_cls, methods in generate_handler_classes(DeviceDataHandler):
    r.register(handler_cls)

# DashboardHandler（看板配置，查/存 {org}_trace_app.dashboard_config_1 看板配置集合）
#   /api/trace_app/dashboard/config（GET）  获取看板配置（标题等）
#   /api/trace_app/dashboard/config（POST） 保存看板配置
for path, handler_cls, methods in generate_handler_classes(DashboardHandler):
    r.register(handler_cls)

# Dashboard2Handler（智能看板2配置，查/存 {org}_trace_app.dashboard_config_2 看板2配置集合，与看板1独立）
#   /api/trace_app/dashboard_2/config（GET）  获取看板2配置（标题等）
#   /api/trace_app/dashboard_2/config（POST） 保存看板2配置
for path, handler_cls, methods in generate_handler_classes(Dashboard2Handler):
    r.register(handler_cls)

# BaseConfigHandler（生产基础配置查询，查 {org}_config 下工艺路线/工序信息表 + idi_{org}.web_layout_application 布局表）
#   /api/trace_app/base_config/routing_list（POST）    查 routing_process_info 按工艺路线编码去重的工艺路线列表
#   /api/trace_app/base_config/routing_processes（POST） 工艺路线→工序信息表 process_info 取生产单元→布局表 web_layout_application 取设备
#   /api/trace_app/base_config/line_list（POST）       查布局表 web_layout_application 按车间代号（产线）去重的产线列表
#   /api/trace_app/base_config/line_devices（POST）    按车间代号查布局表 web_layout_application，按生产单元分组返回设备
for path, handler_cls, methods in generate_handler_classes(BaseConfigHandler):
    r.register(handler_cls)

url.extend(r.host_handlers)
