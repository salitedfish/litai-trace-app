from typing import Any, Dict, List, Optional

from typing_extensions import TypedDict

from trace_app.utils.swagger_utils import BaseResponse, PageItem


# ==================== 健康检查 ====================

class HealthData(TypedDict):
    status: str  # 服务状态（ok 表示正常）


class HealthResponse(BaseResponse):
    data: HealthData  # 健康检查数据


# ==================== 回显 ====================

class EchoRequest(TypedDict):
    """任意请求参数，将原样返回"""
    pass


class EchoResponse(BaseResponse):
    data: Dict[str, Any]  # 回显的请求参数


# ==================== 追溯查询 ====================

class TraceQueryRequest(TypedDict):
    """追溯查询请求参数"""
    qr_code: str  # 产出码/追溯码


class TraceStepInputItem(TypedDict):
    """追溯步骤中的投入物料"""
    material_code: str  # 投入物料编码
    material_type: str  # 物料类型
    qr_code: str  # 条码内容
    require_num: int  # 需求数量


class TraceStepItem(TypedDict):
    """追溯步骤（一次报工的产出+投入）"""
    level: int  # 层级（0=最下游，越大越靠上游）
    workorder_code: str  # 工单编码
    procedure_code: str  # 工序编码
    procedure_name: str  # 工序名称
    material_code: str  # 产出物料编码
    material_type: str  # 产出物料类型
    qr_code: str  # 产出条码
    op_time: str  # 操作时间
    operator: str  # 操作人
    inputs: List[TraceStepInputItem]  # 投入物料列表


class FullTraceResponse(BaseResponse):
    data: List[TraceStepItem]  # 追溯链路（从下游到上游排列）


class TraceDetailRequest(TypedDict):
    """追溯明细请求参数"""
    workorder_code: str  # 工单编码


class TraceInputItem(TypedDict):
    """投入记录"""
    material_code: str  # 投入物料编码
    material_type: str  # 物料类型
    qr_code: str  # 条码内容
    op_time: str  # 操作时间
    code_index: int  # 条码序号
    require_num: int  # 需求数量


class TraceDetailResponse(BaseResponse):
    data: List[TraceInputItem]  # 投入记录列表


# ==================== 投入码查询 ====================

class InputCodeQueryRequest(TypedDict):
    """投入码查询请求参数"""
    input_code: str  # 投入码


class InputCodeOutputItem(TypedDict):
    """投入码关联的产出码"""
    qr_code: str  # 产出码
    material_code: str  # 物料编码
    material_type: str  # 物料类型
    procedure_code: str  # 工序编码
    procedure_name: str  # 工序名称
    op_time: str  # 操作时间
    workorder_code: str  # 工单编码


class InputCodeQueryResponse(BaseResponse):
    data: List[InputCodeOutputItem]


# ==================== 提交记录查询 ====================

class SubmissionRecordRequest(TypedDict):
    """提交记录查询请求参数"""
    qr_code: str
    procedure_code: str
    device_code: str


class SubmissionRecordItem(TypedDict):
    """提交记录"""
    workorder_code: str
    op_time: str
    operator: str
    check_result: str
    production_model: str


class SubmissionRecordResponse(BaseResponse):
    data: List[SubmissionRecordItem]


# ==================== 工艺参数查询 ====================

class ProcessParamRequest(TypedDict):
    """工艺参数查询请求参数"""
    workorder_code: str  # 工单编码


class ProcessParamItem(TypedDict):
    """工艺参数记录"""
    data_type: str  # 数据类型
    params: Dict[str, Any]  # 工艺参数键值对
    device_code: str  # 设备编码
    device_name: str  # 设备名称
    procedure_name: str  # 工序名称
    timestamp: str  # 采集时间


class ProcessParamResponse(BaseResponse):
    data: List[ProcessParamItem]  # 工艺参数记录列表


# ==================== 智能看板配置 ====================

class DashboardConfigRequest(TypedDict):
    """看板配置请求参数"""
    title: str  # 看板标题
    start_date: str  # 开始日期（YYYY-MM-DD，可选，空为当天）
    end_date: str  # 结束日期（YYYY-MM-DD，可选，空为当天）
    workshop_code: str  # 产线编码（可选，空为默认第一条产线）
    product_type: List[str]  # 产品型号列表（可选，可多选，空为不限）


class DashboardConfigResponse(BaseResponse):
    data: Dict[str, Any]  # 看板配置（title 等）


# ==================== 设备数采查询 ====================

class DeviceItem(TypedDict):
    """设备信息"""
    code: str  # 设备编码
    name: str  # 设备名称


class DeviceListResponse(BaseResponse):
    data: List[DeviceItem]  # 设备列表


class DevicePointItem(TypedDict):
    """设备点位信息"""
    code: str  # 点位编码
    name: str  # 点位名称


class DevicePointListResponse(BaseResponse):
    data: List[DevicePointItem]  # 点位列表


class DeviceDataQueryRequest(TypedDict):
    """设备数采数据查询请求参数"""
    device_code: str  # 设备编码
    point_code: str  # 点位编码（可选，为空则查该设备所有点位）
    start_time: str  # 开始时间（ISO 8601）
    end_time: str  # 结束时间（ISO 8601）
    page: int  # 页码（从 1 开始）
    page_size: int  # 每页条数


class DeviceDataItem(TypedDict):
    """设备数采数据记录"""
    code: str  # 信号编码（设备编码~信号类型）
    value: str  # 信号值
    timestamp: str  # 采集时间


class DeviceDataQueryResponse(BaseResponse):
    data: PageItem  # 分页数据（包含 total, page, page_size, list）


# ==================== 生产基础配置查询 ====================

class RoutingItem(TypedDict):
    """工艺路线"""
    routing_code: str  # 工艺路线编码
    routing_name: str  # 工艺路线名称
    routing_type: str  # 工艺路线类型
    workshop_code: str  # 车间编码
    workshop_name: str  # 车间名称


class RoutingListResponse(BaseResponse):
    data: List[RoutingItem]  # 工艺路线列表


class RoutingProcessRequest(TypedDict):
    """工艺路线工序查询请求参数"""
    routing_code: str  # 工艺路线编码


class RoutingProcessDeviceItem(TypedDict):
    """生产单元对应的设备"""
    device_code: str  # 设备编码
    device_name: str  # 设备名称
    device_type: str  # 设备类型（检测/非检测）


class RoutingProcessItem(TypedDict):
    """工艺路线中的工序"""
    process_code: str  # 工序编码
    process_name: str  # 工序名称
    process_order: int  # 工序顺序
    work_center_code: str  # 工作中心编码
    work_center_name: str  # 工作中心名称
    produce_unit_code: str  # 生产单元编码
    produce_unit_name: str  # 生产单元名称
    devices: List[RoutingProcessDeviceItem]  # 生产单元对应的设备列表


class RoutingProcessResult(TypedDict):
    """工艺路线工序查询结果"""
    routing_code: str  # 工艺路线编码
    routing_name: str  # 工艺路线名称
    processes: List[RoutingProcessItem]  # 工序列表（按工序顺序排序）


class RoutingProcessResponse(BaseResponse):
    data: RoutingProcessResult  # 工艺路线工序查询结果


class ProductTypeItem(TypedDict):
    """产品型号"""
    production_type: str  # 产品型号
    routing_code: str  # 工艺路线编码


class ProductTypeListResponse(BaseResponse):
    data: List[ProductTypeItem]  # 产品型号列表


class LineItem(TypedDict):
    """产线（车间）"""
    workshop_code: str  # 产线编码（车间代号）
    workshop_name: str  # 产线名称（车间名称）


class LineListResponse(BaseResponse):
    data: List[LineItem]  # 产线列表


class LineDevicesRequest(TypedDict):
    """产线设备查询请求参数"""
    workshop_code: str  # 产线编码（车间代号）


class LineUnitItem(TypedDict):
    """产线下的生产单元"""
    produce_unit_code: str  # 生产单元编码
    produce_unit_name: str  # 生产单元名称
    devices: List[RoutingProcessDeviceItem]  # 生产单元对应的设备列表


class LineDevicesResult(TypedDict):
    """产线设备查询结果"""
    workshop_code: str  # 产线编码
    workshop_name: str  # 产线名称
    units: List[LineUnitItem]  # 生产单元列表（按生产单元分组）


class LineDevicesResponse(BaseResponse):
    data: LineDevicesResult  # 产线设备查询结果
