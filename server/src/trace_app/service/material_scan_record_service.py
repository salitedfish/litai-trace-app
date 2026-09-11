import re

from trace_app.utils.collection_utils import get_material_scan_records_coll

# 每页最大条数，防止一次拉取过多数据
MAX_PAGE_SIZE = 200


def _normalize_time(value, is_end):
    """把前端传入的时间规整成可与 op_time 字符串直接比较的格式

    支持 'YYYY-MM-DD'（补 00:00:00 / 23:59:59）、
    'YYYY-MM-DD HH:mm'（补 :00 / :59）、'YYYY-MM-DD HH:mm:ss'（原样）三种写法。
    返回空串表示未传或格式不合法（调用方据此忽略该边界）。
    """
    if not value:
        return ""
    text = str(value).strip().replace("T", " ")
    if len(text) == 10:
        return f"{text} 23:59:59" if is_end else f"{text} 00:00:00"
    if len(text) == 16:
        return f"{text}:59" if is_end else f"{text}:00"
    if len(text) >= 19:
        return text[:19]
    return ""


async def query_material_scan_records(code, start_time, end_time, page, page_size):
    """按码值 + 时间范围分页查询扫码登料记录

    数据源为 {org}_manual_trace.material_scan_records（由 manual_line_general_traceability 落库），
    op_time 为 'YYYY-MM-DD HH:mm:ss.ffffff' 字符串，直接做字符串范围比较。

    Args:
        code: 码值（模糊匹配，可为空）
        start_time: 开始时间（可为空）
        end_time: 结束时间（可为空）
        page: 页码（从 1 开始）
        page_size: 每页条数

    Returns:
        {total, page, page_size, list}
    """
    coll = await get_material_scan_records_coll()

    # ---- 构建查询条件 ----
    query_filter = {"is_delete": {"$ne": True}}

    if code:
        # 转义正则元字符，避免用户输入的 . * 等被当作正则语法
        query_filter["code"] = {"$regex": re.escape(code)}

    dt_start = _normalize_time(start_time, False)
    dt_end = _normalize_time(end_time, True)
    if dt_start or dt_end:
        time_condition = {}
        if dt_start:
            time_condition["$gte"] = dt_start
        if dt_end:
            time_condition["$lte"] = dt_end
        query_filter["op_time"] = time_condition

    # ---- 查询并分页 ----
    total = await coll.count_documents(query_filter)

    skip = (page - 1) * page_size
    cursor = coll.find(query_filter).sort([("op_time", -1), ("_id", -1)]).skip(skip).limit(page_size)
    records = await cursor.to_list(length=page_size)

    result_list = []
    for r in records:
        result_list.append({
            "id": str(r.get("_id", "")),
            "product_code": r.get("product_code", ""),
            "product_name": r.get("product_name", ""),
            "routing_code": r.get("routing_code", ""),
            "routing_name": r.get("routing_name", ""),
            "process_code": r.get("process_code", ""),
            "process_name": r.get("process_name", ""),
            # 设备编码供前端跳转数采查询预填（工序未配置生产单元时为空）
            "device_code": r.get("device_code", ""),
            "device_name": r.get("device_name", ""),
            "material_code": r.get("material_code", ""),
            "material_name": r.get("material_name", ""),
            "op_type": r.get("op_type", ""),
            "code": r.get("code", ""),
            "code_type": r.get("code_type", ""),
            "operator": r.get("operator", ""),
            "op_time": r.get("op_time", ""),
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": result_list,
    }
