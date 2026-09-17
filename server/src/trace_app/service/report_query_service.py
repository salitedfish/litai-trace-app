#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
报工查询 / 报工不合格原因 统计服务

  - 报工记录：{org}_order_retrospect.work_order_retrospect_records，只取 op_type='out'
              （一次报工有且仅有一条产出记录，即一行 = 一次报工）
  - 检验单：  {org}_manual_trace.inspection_records（manual_line 报工时落库，只读）
  - 时间口径：op_time 是服务器本地墙上时间字符串（YYYY-MM-DD HH:mm:ss.fff），
              直接做字符串范围比较，不做任何时区换算
  - 报工记录表没有 routing_code 字段，工艺路线条件靠「路线 → 工序集合 → procedure_code $in」反筛
"""
from trace_app.utils.collection_utils import (
    calc_check_result,
    collect_unqualified_reason_counts,
    enrich_device_names,
    enrich_user_names,
    get_inspection_records_coll,
    get_process_coll,
    get_records_coll,
    get_routing_process_info_coll,
)
from trace_app.utils.datetime_utils import normalize_time_bound

# 每页最大条数，防止一次拉取过多数据
MAX_PAGE_SIZE = 200

# 人员/设备下拉候选最多返回多少项，防止记录量极大时把下拉撑爆
MAX_FILTER_OPTION = 500

# 检测结果下拉的可选值，与列表「检测结果」列的显示值一致（见 calc_check_result）
CHECK_RESULT_OPTIONS = ["一次合格", "返工合格", "复投合格", "不合格"]


def _empty_page(page, page_size):
    """条件互斥/无候选时直接返回空页，不再发查询"""
    return {"total": 0, "page": page, "page_size": page_size, "list": []}


def _build_time_condition(start_time, end_time):
    """把起止时间规整成 op_time 的字符串比较区间

    op_time 存的是「YYYY-MM-DD HH:mm:ss.SSS」本地墙上时间字符串（已连库确认），
    故直接做字符串比较，不做任何时区换算。

    终点补 `.999`：用户选到 23:59 的语义是「含这一分钟」，而字符串比较下
    '23:59:59.708' > '23:59:59'，不补就会把结束那一秒内的记录漏掉。

    Returns:
        {"$gte": ..., "$lte": ...} 子条件；两端都为空（不限）时返回 None
    """
    dt_start = normalize_time_bound(start_time, False)
    dt_end = normalize_time_bound(end_time, True)
    if not dt_start and not dt_end:
        return None
    condition = {}
    if dt_start:
        condition["$gte"] = dt_start
    if dt_end:
        condition["$lte"] = dt_end + ".999"
    return condition


def _check_result_condition(check_result):
    """把「检测结果」显示值反解成报工记录的查询条件

    与 calc_check_result() 严格互逆，四个显示值互斥且覆盖全部取值组合。
    返回 None 表示不是这四个已知值（调用方据此返回空页）。

    一次合格：原值为空 且 生产模式非返工/复投
    返工合格：原值为空且生产模式=返工，或原值='合格'（返修后检验合格）
    复投合格：原值为空 且 生产模式=复投
    不合格  ：原值既非空也非'合格'
    """
    if check_result == "一次合格":
        return {"check_result": "", "production_model": {"$nin": ["rework", "resubmission"]}}
    if check_result == "返工合格":
        return {"$or": [
            {"check_result": "", "production_model": "rework"},
            {"check_result": "合格"},
        ]}
    if check_result == "复投合格":
        return {"check_result": "", "production_model": "resubmission"}
    if check_result == "不合格":
        return {"check_result": {"$nin": ["", "合格"]}}
    return None


async def _get_routing_process_codes(routing_code):
    """取工艺路线下的全部工序编码

    报工记录表里没有 routing_code，只能反过来用路线下的工序集合去筛 procedure_code。
    路线下未配置工序时返回空集合，调用方应直接返回空页。
    """
    coll = await get_routing_process_info_coll()
    codes = set()
    async for doc in coll.find({"工艺路线编码": routing_code}, {"_id": 0, "工序编码": 1}):
        code = str(doc.get("工序编码") or "").strip()
        if code:
            codes.add(code)
    return codes


async def _shape_records(records):
    """把报工记录原始文档整理成列表行

    报工记录表不存工序名称，也不存人员昵称，故：
      - 工序名称按 procedure_code 批量回查配置表补齐
      - 设备名称 / 操作人昵称由富化工具就地填写（内部已吞异常，失败只记日志）
    报工查询与「不合格原因的报工记录」两处共用，保证两边的行长相一致。

    Args:
        records: 报工记录原始文档列表（已分页）

    Returns:
        列表行数组
    """
    result_list = []
    operator_ids = set()
    device_codes = set()
    procedure_codes = set()
    for r in records:
        op_id = str(r.get("operator") or "")
        dev_code = str(r.get("device_code") or "")
        proc_code = str(r.get("procedure_code") or "")
        if op_id:
            operator_ids.add(op_id)
        if dev_code:
            device_codes.add(dev_code)
        if proc_code:
            procedure_codes.add(proc_code)

        result_list.append({
            "id": str(r.get("_id", "")),
            "workorder_code": r.get("workorder_code", ""),
            # 报工记录的产品字段是 production_type（由 manual_line 按路线反查产品型号得来）
            "product_type": r.get("production_type", ""),
            "procedure_code": proc_code,
            # 报工记录不存工序名称，下面按编码批量回查配置表补齐
            "procedure_name": "",
            "material_code": r.get("material_code", ""),
            "material_type": r.get("material_type", ""),
            "qr_code": r.get("qr_code", ""),
            "op_time": str(r.get("op_time", "")),
            "device_code": dev_code,
            "device_name": "",
            # 显示值与原值不同：原始记录只有空/'合格'，结合生产模式才得出三档合格
            "check_result": calc_check_result(
                r.get("check_result", ""), r.get("production_model", "")),
            "operator": op_id,
        })

    # ---- 批量补名称（一次查询，避免逐行查） ----
    if procedure_codes:
        name_map = {}
        process_coll = await get_process_coll()
        async for doc in process_coll.find(
            {"工序编码": {"$in": list(procedure_codes)}},
            projection={"_id": 0, "工序编码": 1, "工序名称": 1},
        ):
            name_map[str(doc.get("工序编码") or "")] = doc.get("工序名称", "")
        for item in result_list:
            item["procedure_name"] = name_map.get(item["procedure_code"], "")

    # 原地填 device_name / 把 operator 换成昵称；内部已吞异常，失败只记日志
    await enrich_device_names(device_codes, result_list)
    await enrich_user_names(operator_ids, result_list)

    return result_list


async def query_report_records(product_type=None, routing_code=None, process_code=None,
                               operator_id=None, check_result=None, device_code=None,
                               start_time=None, end_time=None, page=1, page_size=20):
    """按条件分页查询报工记录（一次报工一行，取产出记录）

    Args:
        product_type: 产品型号（空为不限，对应记录字段 production_type）
        routing_code: 工艺路线编码（空为不限，经工序集合反筛）
        process_code: 工序编码（空为不限）
        operator_id: 操作人工号（空为不限）
        check_result: 检测结果显示值（一次合格/返工合格/复投合格/不合格，空为不限）
        device_code: 设备编码（空为不限）
        start_time: 操作时间起（空为不限）
        end_time: 操作时间止（空为不限）
        page: 页码（从 1 开始）
        page_size: 每页条数

    Returns:
        {total, page, page_size, list}
    """
    coll = await get_records_coll()

    # ---- 构建查询条件 ----
    query_filter = {"is_delete": {"$ne": True}, "op_type": "out"}

    if product_type:
        query_filter["production_type"] = product_type

    # 工序：选了工序必须落在所选工艺路线的工序集合内；只选路线则按该路线全部工序过滤
    routing_process_codes = None
    if routing_code:
        routing_process_codes = await _get_routing_process_codes(routing_code)
        if not routing_process_codes:
            return _empty_page(page, page_size)

    if process_code:
        if routing_process_codes is not None and process_code not in routing_process_codes:
            return _empty_page(page, page_size)
        query_filter["procedure_code"] = process_code
    elif routing_process_codes is not None:
        query_filter["procedure_code"] = {"$in": list(routing_process_codes)}

    if operator_id:
        query_filter["operator"] = operator_id

    if check_result:
        condition = _check_result_condition(check_result)
        if condition is None:
            return _empty_page(page, page_size)
        query_filter.update(condition)

    if device_code:
        query_filter["device_code"] = device_code

    time_condition = _build_time_condition(start_time, end_time)
    if time_condition:
        query_filter["op_time"] = time_condition

    # ---- 查询并分页 ----
    total = await coll.count_documents(query_filter)

    skip = (page - 1) * page_size
    cursor = coll.find(query_filter).sort([("op_time", -1), ("_id", -1)]).skip(skip).limit(page_size)
    records = await cursor.to_list(length=page_size)

    result_list = await _shape_records(records)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": result_list,
    }


async def query_report_filter_options():
    """报工查询页的人员/设备下拉候选（取自报工记录里实际出现过的值）

    人员/设备不受页面上其它筛选项约束（避免日期一改候选就空掉，看起来像坏了）。
    用一次 $facet 聚合同时取两组候选，不对同一张表扫两遍。

    Returns:
        {"operators": [{value, label}], "devices": [{value, label}]}
        value 为工号/设备编码（用于过滤），label 为「昵称 / 工号」「设备名称 / 编码」
    """
    coll = await get_records_coll()
    pipeline = [
        {"$match": {"is_delete": {"$ne": True}, "op_type": "out"}},
        {"$facet": {
            "operators": [
                {"$match": {"operator": {"$nin": ["", None]}}},
                {"$group": {"_id": "$operator"}},
                {"$sort": {"_id": 1}},
                {"$limit": MAX_FILTER_OPTION},
            ],
            "devices": [
                {"$match": {"device_code": {"$nin": ["", None]}}},
                {"$group": {"_id": "$device_code"}},
                {"$sort": {"_id": 1}},
                {"$limit": MAX_FILTER_OPTION},
            ],
        }},
    ]
    docs = await coll.aggregate(pipeline).to_list(length=1)
    facet = docs[0] if docs else {}
    operator_ids = [str(d.get("_id")) for d in facet.get("operators", []) if d.get("_id")]
    device_codes = [str(d.get("_id")) for d in facet.get("devices", []) if d.get("_id")]

    # ---- 人员：昵称 + 工号（查不到昵称就只显示工号） ----
    operators = [{"value": oid, "label": oid} for oid in operator_ids]
    if operators:
        # 借用公共富化函数批量查昵称（它把 operator 原地替换成昵称，故另存 work_id）
        items = [{"operator": oid, "work_id": oid} for oid in operator_ids]
        await enrich_user_names(operator_ids, items)
        for opt, item in zip(operators, items):
            nickname = item["operator"]
            if nickname and nickname != item["work_id"]:
                opt["label"] = f"{nickname} / {item['work_id']}"

    # ---- 设备：名称 + 编码 ----
    devices = [{"value": code, "label": code} for code in device_codes]
    if devices:
        items = [{"device_code": code, "device_name": ""} for code in device_codes]
        await enrich_device_names(device_codes, items)
        for opt, item in zip(devices, items):
            if item["device_name"]:
                opt["label"] = f"{item['device_name']} / {opt['value']}"

    return {"operators": operators, "devices": devices}


async def query_unqualified_reasons(product_type=None, routing_code=None, process_code=None,
                                    start_time=None, end_time=None, page=1, page_size=20):
    """按条件分页统计报工时检验单的各不合格原因次数

    口径与看板2「不合格原因占比」完全一致（共用 collect_unqualified_reason_counts）：
    每张检验单 items 中 is_qualified=False 的项，其 unqualified_reasons 逐条各计 1。

    条件都直接落在检验单自身的字段上（product_code / routing_code / process_code / op_time，
    前三项为 manual_line 报工时用户所选原值）。日期留空则不限，为全表遍历后内存聚合
    —— 检验单数据量大时不带日期查询较慢。

    Args:
        product_type: 产品型号（空为不限，匹配检验单的 product_code）
        routing_code: 工艺路线编码（空为不限）
        process_code: 工序编码（空为不限）
        start_time: 报工时间起（空为不限）
        end_time: 报工时间止（空为不限）
        page: 页码（从 1 开始）
        page_size: 每页条数

    Returns:
        {total, page, page_size, list:[{reason_code, reason_name, count}]}
        total 为原因条数（不是检验单张数），排序为次数降序、同次数按原因编码升序
    """
    coll = await get_inspection_records_coll()

    query = {"is_delete": {"$ne": True}}
    if product_type:
        query["product_code"] = product_type
    if routing_code:
        query["routing_code"] = routing_code
    if process_code:
        query["process_code"] = process_code

    time_condition = _build_time_condition(start_time, end_time)
    if time_condition:
        query["op_time"] = time_condition

    all_reasons = await collect_unqualified_reason_counts(
        coll.find(query, {"_id": 0, "items": 1}))

    total = len(all_reasons)
    skip = (page - 1) * page_size
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": all_reasons[skip:skip + page_size],
    }


async def query_report_records_by_reason(reason_code, reason_name=None,
                                         product_type=None, routing_code=None, process_code=None,
                                         start_time=None, end_time=None, page=1, page_size=20):
    """查某条不合格原因关联的报工记录（报工不合格原因页「报工记录」按钮）

    与 query_unqualified_reasons 同源：都基于检验单 items 中不合格项的
    unqualified_reasons 原因快照，故查出的报工记录与左侧统计的次数对得上。

    两步走：先取勾选了该原因的检验单的 workorder_code（distinct 去重），
    再按这些工单号查产出报工记录。一次报工对应一张检验单，故报工记录条数
    可能少于原因次数——同一张检验单上同一原因勾了多次，只算一条报工。

    原因匹配口径与 collect_unqualified_reason_counts 的 key 一致（key = reason_code or reason_name）：
      - reason_code 非空：按 reason_code 匹配
      - reason_code 为空：按「reason_code 为空且 reason_name 相同」匹配
    不合格项的口径也保持一致：is_qualified 非 True 即算不合格（缺失/None/false 都算）。

    Args:
        reason_code: 不合格原因编码（空则回落用 reason_name 匹配）
        reason_name: 不合格原因名称
        product_type: 产品型号（空为不限，匹配检验单 product_code）
        routing_code: 工艺路线编码（空为不限）
        process_code: 工序编码（空为不限）
        start_time: 报工时间起（空为不限，与左侧统计同口径，否则条数对不上）
        end_time: 报工时间止（空为不限）
        page: 页码（从 1 开始）
        page_size: 每页条数

    Returns:
        {total, page, page_size, list}，行结构与 query_report_records 完全一致
    """
    reason_code = str(reason_code or "").strip()
    reason_name = str(reason_name or "").strip()
    if not reason_code and not reason_name:
        return _empty_page(page, page_size)

    inspection_coll = await get_inspection_records_coll()

    query = {"is_delete": {"$ne": True}}
    if product_type:
        query["product_code"] = product_type
    if routing_code:
        query["routing_code"] = routing_code
    if process_code:
        query["process_code"] = process_code

    # 时间条件与左侧统计同源（都落在检验单 op_time 上），否则页面上加了日期后
    # 弹窗条数会与左侧次数对不上
    time_condition = _build_time_condition(start_time, end_time)
    if time_condition:
        query["op_time"] = time_condition

    if reason_code:
        reason_cond = {"reason_code": reason_code}
    else:
        # 统计里 reason_code 为空时以 reason_name 为 key，此处按「无编码 + 同名」匹配
        reason_cond = {"reason_code": {"$in": ["", None]}, "reason_name": reason_name}

    query["items"] = {
        "$elemMatch": {
            "is_qualified": {"$ne": True},
            "unqualified_reasons": {"$elemMatch": reason_cond},
        }
    }

    workorder_codes = [str(c).strip() for c in await inspection_coll.distinct("workorder_code", query)]
    workorder_codes = [c for c in workorder_codes if c]
    if not workorder_codes:
        return _empty_page(page, page_size)

    rec_coll = await get_records_coll()
    rec_query = {
        "is_delete": {"$ne": True},
        "op_type": "out",
        "workorder_code": {"$in": workorder_codes},
    }

    total = await rec_coll.count_documents(rec_query)
    skip = (page - 1) * page_size
    cursor = rec_coll.find(rec_query).sort([("op_time", -1), ("_id", -1)]).skip(skip).limit(page_size)
    records = await cursor.to_list(length=page_size)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": await _shape_records(records),
    }
