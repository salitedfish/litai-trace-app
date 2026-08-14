#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
工序合格率计算服务

  - 从 work_order_retrospect_records 报工记录统计各工序合格率
  - 只展示有报工记录的工序（按工序编码去重）
  - 工序名称从 production_config_mgm_process_info 工序信息表查询
"""
import datetime

from mg_app_framework import get_logger

from trace_app.utils.collection_utils import get_process_coll, get_records_coll


async def get_process_quality(start_time=None, end_time=None):
    """计算各工序合格率

    合格判定：报工记录 check_result 为空视为合格。
    只统计产出记录（op_type='out'），按工序编码分组。

    Args:
        start_time: 统计起始时间（datetime，None 为当天 0 点）
        end_time: 统计结束时间（datetime，None 为当天 23:59:59）

    Returns:
        工序合格率列表，按合格率升序（问题工序在前）：
        [{procedure_code, procedure_name, total, good, quality_rate}]
    """
    now = datetime.datetime.now()
    if start_time is None:
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if end_time is None:
        end_time = now.replace(hour=23, minute=59, second=59, microsecond=0)

    start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        coll = await get_records_coll()
        pipeline = [
            {"$match": {"op_type": "out", "op_time": {"$gte": start_str, "$lt": end_str}}},
            {"$group": {
                "_id": "$procedure_code",
                "total": {"$sum": 1},
                "good": {"$sum": {"$cond": [{"$eq": ["$check_result", ""]}, 1, 0]}},
            }},
        ]
        stats = {}
        async for doc in coll.aggregate(pipeline):
            code = doc.get("_id")
            if not code:
                continue
            stats[code] = {"total": doc.get("total", 0), "good": doc.get("good", 0)}

        if not stats:
            return []

        # 工序名称（工序编码 → 工序名称，查不到时回退显示编码）
        name_map = await _get_process_name_map(list(stats.keys()))

        result = []
        for code, s in stats.items():
            total = s["total"]
            good = s["good"]
            result.append({
                "procedure_code": code,
                "procedure_name": name_map.get(code, code),
                "total": total,
                "good": good,
                "quality_rate": round(good / total * 100, 2) if total else 0,
            })

        # 按合格率升序（问题工序在前）
        result.sort(key=lambda x: x["quality_rate"])
        return result
    except Exception as e:
        get_logger().exception("计算工序合格率失败: %s", e)
        return []


async def _get_process_name_map(codes):
    """批量查询工序编码对应的工序名称"""
    name_map = {}
    try:
        coll = await get_process_coll()
        async for doc in coll.find({"工序编码": {"$in": codes}}, {"工序编码": 1, "工序名称": 1}):
            code = doc.get("工序编码")
            if code:
                name_map[code] = doc.get("工序名称", "") or code
    except Exception as e:
        get_logger().exception("查询工序名称失败: %s", e)
    return name_map
