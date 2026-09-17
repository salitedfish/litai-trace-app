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


# ==================== 检验单查询 ====================

class InspectionRecordRequest(TypedDict):
    """检验单查询请求参数"""
    workorder_code: str  # 工单编码


class InspectionRecordItemDetail(TypedDict):
    """检验单中的单项检验记录"""
    item_code: str  # 检验项编码
    item_name: str  # 检验项名称
    inspect_type: str  # 检验类型（range=数据范围 / qualified=是否合格）
    range_value: str  # 数据范围（最小值-最大值，range 类型才有值）
    requirement: str  # 检验要求（操作指导文本，可选，空串/缺键=未填）
    tool: str  # 检验工具（可选，空串/缺键=未填）
    input_value: str  # 填写值
    is_qualified: bool  # 该项是否合格
    unqualified_reasons: List[dict]  # 选中的不合格原因明细快照（[{reason_code, reason_name}]，合格/未配置/历史旧记录为空数组）


class InspectionRecordItem(TypedDict):
    """检验单记录"""
    workorder_code: str  # 工单编码（与报工追溯记录关联）
    raw_workorder_code: str  # 原始工单号（不含时间戳后缀）
    product_code: str  # 产品编码
    routing_code: str  # 工艺路线编码
    process_code: str  # 工序编码
    process_name: str  # 工序名称
    produce_unit_code: str  # 生产单元编码
    device_code: str  # 设备编码
    items: List[InspectionRecordItemDetail]  # 检验明细快照
    is_qualified: bool  # 整体是否合格
    operator: str  # 操作人
    op_time: str  # 检验时间
    created_at: str  # 创建时间


class InspectionRecordResponse(BaseResponse):
    data: InspectionRecordItem  # 检验单记录（无则 null）


# ==================== 智能看板配置 ====================

class DashboardConfigRequest(TypedDict):
    """看板配置请求参数"""
    title: str  # 看板标题
    start_date: str  # 开始日期（YYYY-MM-DD，可选，空为当天）
    end_date: str  # 结束日期（YYYY-MM-DD，可选，空为当天）
    workshop_code: str  # 产线编码（可选，空为默认第一条产线）
    product_type: List[str]  # 产品型号列表（可选，可多选，空为不限）
    unused_devices: List[str]  # 未使用的设备编码列表（可选，这些设备不显示状态、不计入 OEE，空为不排除）
    mock: Dict[str, Any]  # 模拟数据配置（可选，客户演示用；{模块: {enabled, data}}，模块白名单见 handler 的 MOCK_MODULES）


class DashboardConfigResponse(BaseResponse):
    data: Dict[str, Any]  # 看板配置（title 等，含模拟数据配置 mock）


class HistoryOutputRequest(TypedDict):
    """历史数据请求参数"""
    product_types: List[str]  # 产品型号列表（可选，可多选，空为不限）


class HistoryOutputDay(TypedDict):
    """某天的完成量"""
    date: str  # 日期（MM-DD）
    total_count: int  # 日完成量
    avg_hourly: float  # 日均小时完成量（当天平均每小时产出）
    first_pass_rate: float  # 日均一次合格率（当天一次合格数 ÷ 完成量 × 100）


class HistoryOutputData(TypedDict):
    """历史数据"""
    days: List[HistoryOutputDay]  # 前两周每天的数据（升序，不含今天）


class HistoryOutputResponse(BaseResponse):
    data: HistoryOutputData  # 历史数据


# ==================== 智能看板2 检验项不合格占比 ====================

class UnqualifiedPieRequest(TypedDict):
    """检验项不合格占比请求参数"""
    start_date: str  # 开始日期（YYYY-MM-DD，可选，空为当天）
    end_date: str  # 结束日期（YYYY-MM-DD，可选，空为当天）
    workshop_code: str  # 产线编码（可选，空为全部产线）
    product_types: List[str]  # 产品型号列表（可选，多选，空为不限）


class UnqualifiedPieItem(TypedDict):
    """单个检验项的不合格统计"""
    item_code: str  # 检验项编码
    item_name: str  # 检验项名称（取检验单快照，缺失时回退编码）
    count: int  # 该检验项不合格次数


class UnqualifiedPieResponse(BaseResponse):
    data: List[UnqualifiedPieItem]  # 各检验项不合格计数（按次数降序）


# ==================== 智能看板2 不合格原因占比 ====================

class UnqualifiedReasonPieRequest(TypedDict):
    """不合格原因占比请求参数"""
    start_date: str  # 开始日期（YYYY-MM-DD，可选，空为当天）
    end_date: str  # 截止日期（YYYY-MM-DD，可选，空为当天）
    workshop_code: str  # 产线编码（可选，空为全部产线）
    product_types: List[str]  # 产品型号列表（可选，多选，空为不限）


class UnqualifiedReasonPieItem(TypedDict):
    """单个不合格原因的统计"""
    reason_code: str  # 不合格原因编码（快照缺失/为空时回退名称作键）
    reason_name: str  # 不合格原因名称（取检验单快照，缺失时回退编码）
    count: int  # 该原因在不合格项中被勾选的次数


class UnqualifiedReasonPieResponse(BaseResponse):
    data: List[UnqualifiedReasonPieItem]  # 各不合格原因被勾选次数（按次数降序）


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
    name: str  # 信号名称（来自设备点位配置 children[].name，查不到时回落为点位编码）
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


class ProcessItem(TypedDict):
    """工序"""
    process_code: str  # 工序编码
    process_name: str  # 工序名称


class ProcessListResponse(BaseResponse):
    data: List[ProcessItem]  # 全部工序列表


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


# ==================== 扫码登料查询 ====================

class MaterialScanQueryRequest(TypedDict):
    """扫码登料查询请求参数"""
    code: str  # 码值（可选，模糊匹配）
    start_time: str  # 开始时间（YYYY-MM-DD HH:mm:ss，可选）
    end_time: str  # 结束时间（YYYY-MM-DD HH:mm:ss，可选）
    page: int  # 页码（从 1 开始）
    page_size: int  # 每页条数


class MaterialScanRecordItem(TypedDict):
    """扫码登料记录"""
    id: str  # 记录ID
    product_code: str  # 产品编码
    product_name: str  # 产品名称
    routing_code: str  # 工艺路线编码
    routing_name: str  # 工艺路线名称
    process_code: str  # 工序编码
    process_name: str  # 工序名称
    device_code: str  # 设备编码（前端跳转数采查询用，工序未配置生产单元时为空）
    device_name: str  # 设备名称
    material_code: str  # 物料编码
    material_name: str  # 物料名称
    op_type: str  # 操作类型（in=投入/out=产出）
    code: str  # 码值
    code_type: str  # 条码类型
    operator: str  # 操作人工号
    op_time: str  # 操作时间


class MaterialScanQueryResponse(BaseResponse):
    data: PageItem  # 分页数据（包含 total, page, page_size, list）


# ==================== 报工查询 ====================

class ReportQueryRequest(TypedDict):
    """报工查询请求参数"""
    product_type: str  # 产品型号（可选，对应记录 production_type）
    routing_code: str  # 工艺路线编码（可选，经该路线工序集合反筛）
    process_code: str  # 工序编码（可选）
    operator: str  # 操作人工号（可选）
    check_result: str  # 检测结果（可选，一次合格/返工合格/复投合格/不合格）
    device_code: str  # 设备编码（可选）
    start_time: str  # 操作时间起（YYYY-MM-DD HH:mm:ss，可选）
    end_time: str  # 操作时间止（YYYY-MM-DD HH:mm:ss，可选）
    page: int  # 页码（从 1 开始）
    page_size: int  # 每页条数


class ReportRecordItem(TypedDict):
    """报工记录（一次报工一行，取产出记录）"""
    id: str  # 记录ID
    workorder_code: str  # 工单编码
    product_type: str  # 产品型号
    procedure_code: str  # 工序编码
    procedure_name: str  # 工序名称
    material_code: str  # 物料编码
    material_type: str  # 物料类型（raw_material/semi_finished_product/finished_product）
    qr_code: str  # 产出条码
    op_time: str  # 操作时间
    device_code: str  # 设备编码
    device_name: str  # 设备名称
    check_result: str  # 检测结果（一次合格/返工合格/复投合格/不合格）
    operator: str  # 操作人（查到昵称时为昵称，否则为工号）


class ReportQueryResponse(BaseResponse):
    data: PageItem  # 分页数据（包含 total, page, page_size, list）


class ReportFilterOptionItem(TypedDict):
    """报工查询下拉候选项"""
    value: str  # 提交给后端的值（工号/设备编码）
    label: str  # 显示文本（昵称 / 工号、设备名称 / 编码）


class ReportFilterOptionsData(TypedDict):
    """报工查询页下拉候选"""
    operators: List[ReportFilterOptionItem]  # 人员候选（记录里出现过的操作人）
    devices: List[ReportFilterOptionItem]  # 设备候选（记录里出现过的设备）


class ReportFilterOptionsResponse(BaseResponse):
    data: ReportFilterOptionsData  # 人员/设备候选


# ==================== 报工不合格原因 ====================

class UnqualifiedReasonQueryRequest(TypedDict):
    """报工不合格原因查询请求参数"""
    product_type: str  # 产品型号（可选，匹配检验单 product_code）
    routing_code: str  # 工艺路线编码（可选）
    process_code: str  # 工序编码（可选）
    start_time: str  # 报工时间起（可选，留空为不限）
    end_time: str  # 报工时间止（可选，留空为不限）
    page: int  # 页码（从 1 开始）
    page_size: int  # 每页条数


class UnqualifiedReasonItem(TypedDict):
    """不合格原因统计项"""
    reason_code: str  # 不合格原因编码
    reason_name: str  # 不合格原因名称（缺失时回退为编码）
    count: int  # 被勾选次数


class UnqualifiedReasonQueryResponse(BaseResponse):
    data: PageItem  # 分页数据（total 为原因条数，list 为 {reason_code, reason_name, count}）


class UnqualifiedReasonReportRequest(TypedDict):
    """不合格原因关联报工记录查询请求参数"""
    reason_code: str  # 不合格原因编码（空则用 reason_name 匹配）
    reason_name: str  # 不合格原因名称
    product_type: str  # 产品型号（可选，与列表现有筛选条件保持一致）
    routing_code: str  # 工艺路线编码（可选）
    process_code: str  # 工序编码（可选）
    start_time: str  # 报工时间起（可选，与列表现有筛选条件保持一致）
    end_time: str  # 报工时间止（可选）
    page: int  # 页码（从 1 开始）
    page_size: int  # 每页条数
