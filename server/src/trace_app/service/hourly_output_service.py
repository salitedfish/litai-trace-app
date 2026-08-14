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


async def get_hourly_output(start_time=None, end_time=None):
    """按小时统计产出数量

    只统计产出记录（op_type='out'）；同一工序同一码的重复报工
    （返工/重复扫码等）只计一条产出，取最新报工时间归属小时。

    Args:
        start_time: 统计起始时间（datetime，None 为当天 0 点）
        end_time: 统计结束时间（datetime，None 为当天 23:59:59）

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
        cursor = coll.find(
            {"op_type": "out", "op_time": {"$gte": start_str, "$lt": end_str}},
            {"_id": 0, "op_time": 1, "procedure_code": 1, "qr_code": 1},
        )
        # 同一工序同一码去重：保留最新一条报工（返工等重复报工只算一次产出）
        latest = {}
        async for doc in cursor:
            op = doc.get("op_time")
            if not isinstance(op, (str, datetime.datetime)):
                continue
            key = (doc.get("procedure_code", ""), doc.get("qr_code", ""))
            prev = latest.get(key)
            if prev is None or str(op) > str(prev):
                latest[key] = op

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
