#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
计划/实际产量服务

  - 实际产量：从 work_order_retrospect_records 报工记录统计区间内、最后一道工序的产出去重数量（同一码只算一次）
  - 计划产量：从排产表 father_worksheet 统计日期区间内、最后一道工序的已发布（pushed）计划量
  - 产量进度：实际产量 / 计划产量 × 100
  - 均按看板配置的产品型号过滤（报工表 production_type / 排产表 material_code + process_code）；
    统计日期区间由看板配置的时间范围决定，不配置时默认当天
"""
import datetime

from mg_app_framework import get_logger

from trace_app.utils.collection_utils import get_records_coll, get_father_worksheet_coll
from trace_app.service.last_process_service import get_last_process_codes, get_last_process_map


async def get_plan_actual_output(start_time=None, end_time=None, product_types=None):
    """统计计划产量 / 实际产量 / 进度

    Args:
        start_time: 统计起始日期（datetime，None 为当天 0 点）
        end_time: 统计结束日期（datetime，None 为当天）
        product_types: 产品型号列表（可空；非空时只统计这些产品型号）

    Returns:
        {"plan_count": 计划产量, "actual_count": 实际产量, "progress": 进度%}
    """
    now = datetime.datetime.now()
    if start_time is None:
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    if end_time is None:
        end_time = now.replace(hour=23, minute=59, second=59, microsecond=0)
    else:
        end_time = end_time.replace(hour=23, minute=59, second=59, microsecond=0)

    # 报工记录 op_time 范围：[起始日 00:00:00, 结束日次日 00:00:00)
    start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_exclusive_str = (end_time + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    # 排产表 worksheet_date 范围（闭区间）：起始日 ~ 结束日
    plan_start_str = start_time.strftime("%Y/%m/%d")
    plan_end_str = end_time.strftime("%Y/%m/%d")

    actual_count = await _count_actual(start_str, end_exclusive_str, product_types)
    plan_count = await _count_plan(plan_start_str, plan_end_str, product_types)
    progress = round(actual_count / plan_count * 100, 2) if plan_count else 0

    return {"plan_count": plan_count, "actual_count": actual_count, "progress": progress}


async def _count_actual(start_str, end_str, product_types):
    """实际产量：报工记录区间内最后一道工序产出去重数量（同一码只算一次）"""
    try:
        coll = await get_records_coll()
        query = {
            "op_type": "out",
            "op_time": {"$gte": start_str, "$lt": end_str},
            "qr_code": {"$ne": ""},
        }
        # 指定了产品型号时按 production_type 过滤，否则统计全部
        if product_types:
            query["production_type"] = {"$in": list(product_types)}
        # 只统计最后一道工序的报工产出（产品型号 → 工艺路线 → 最后工序）
        last_process_codes = await get_last_process_codes(product_types)
        if last_process_codes:
            query["procedure_code"] = {"$in": list(last_process_codes)}
        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$qr_code"}},
            {"$count": "count"},
        ]
        count = 0
        async for doc in coll.aggregate(pipeline):
            count = doc.get("count", 0)
        return count
    except Exception as e:
        get_logger().exception("计算实际产量失败: %s", e)
        return 0


async def _count_plan(plan_start_str, plan_end_str, product_types):
    """计划产量：排产表在日期区间内、最后一道工序的已发布计划量求和"""
    try:
        coll = await get_father_worksheet_coll()
        query = {
            "worksheet_date": {"$gte": plan_start_str, "$lte": plan_end_str},
            "status": "pushed",
        }
        # father_worksheet 按「任务 × 工序」拆行，同一物料每个工序都有相同 count，
        # 必须按 (物料, 最后工序) 精确匹配，否则计划量会被工序数重复累加；
        # 查不到最后工序映射时退回按物料过滤（数据配置不完整时的兜底）
        last_process_map = await get_last_process_map(product_types)
        if last_process_map:
            query["$or"] = [
                {"material_code": pt, "process_code": pc}
                for pt, pc in last_process_map.items()
            ]
        elif product_types:
            query["material_code"] = {"$in": list(product_types)}
        pipeline = [
            {"$match": query},
            {"$group": {"_id": None, "total": {"$sum": "$count"}}},
        ]
        total = 0
        async for doc in coll.aggregate(pipeline):
            total = doc.get("total", 0)
        return total
    except Exception as e:
        get_logger().exception("计算计划产量失败: %s", e)
        return 0
