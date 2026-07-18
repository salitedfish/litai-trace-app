from typing import Any, Dict, List, Optional

from typing_extensions import TypedDict

from trace_app.utils.swagger_utils import BaseResponse


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
