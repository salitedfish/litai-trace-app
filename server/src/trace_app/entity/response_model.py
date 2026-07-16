from typing import Any, Dict

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
