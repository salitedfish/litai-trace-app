#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
小时产量统计服务

  - 从 work_order_retrospect_records 报工记录统计产出数量
  - 按小时分组（op_time 的小时部分），返回 [{hour, count}]
  - 兼容 op_time 为字符串或 datetime 两种存储类型
"""
import datetime

from mg_app_framework import get_logger

from trace_app.utils.collection_utils import get_records_coll
from trace_app.service.last_process_service import get_last_process_codes


def _extract_hour(op_time):
    """提取操作时间的小时（含日期）部分（兼容字符串 / datetime）

    按「日期 + 小时」分组，避免跨天统计时各天同一小时被合并。
    Returns:
        "YYYY-MM-DD HH" 或 None
    """
    if isinstance(op_time, datetime.datetime):
        return op_time.strftime("%Y-%m-%d %H")
    if isinstance(op_time, str) and len(op_time) >= 13:
        return op_time[0:13]
    return None


async def get_hourly_output(start_time=None, end_time=None, product_types=None):
    """按小时统计产出数量

    只统计产出记录（op_type='out'），且只统计最后一道工序的报工
    （产品型号 → 工艺路线 → 最后工序）；同一码（产品）的重复报工
    （返工/重复扫码等）只计一条产出，取最新报工时间归属小时。

    Args:
        start_time: 统计起始时间（datetime，None 为当天 0 点）
        end_time: 统计结束时间（datetime，None 为当天 23:59:59）
        product_types: 产品型号列表（可空；非空时只统计这些产品型号的产出）

    Returns:
        按小时升序：[{hour, count}]
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
        query = {"op_type": "out", "op_time": {"$gte": start_str, "$lt": end_str}}
        # 指定了产品型号时按 production_type 过滤，否则统计全部
        if product_types:
            query["production_type"] = {"$in": list(product_types)}
        # 只统计最后一道工序的报工产出（产品型号 → 工艺路线 → 最后工序）
        last_process_codes = await get_last_process_codes(product_types)
        if last_process_codes:
            query["procedure_code"] = {"$in": list(last_process_codes)}
        cursor = coll.find(
            query,
            {"_id": 0, "op_time": 1, "qr_code": 1},
        )
        # 同一码去重：保留最新一条报工（一个产品只计一次产出），按最新报工时间归属小时
        latest = {}
        async for doc in cursor:
            op = doc.get("op_time")
            if not isinstance(op, (str, datetime.datetime)):
                continue
            qr = doc.get("qr_code", "")
            if not qr:
                continue
            prev = latest.get(qr)
            if prev is None or str(op) > str(prev):
                latest[qr] = op

        hour_counts = {}
        for op in latest.values():
            hour = _extract_hour(op)
            if hour is None:
                continue
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        return [{"hour": h, "count": hour_counts[h]} for h in sorted(hour_counts.keys())]
    except Exception as e:
        get_logger().exception("计算小时产量失败: %s", e)
        return []
