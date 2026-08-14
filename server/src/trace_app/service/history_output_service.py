#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
历史数据服务（看板历史数据卡）

  - 按天统计前两周（最近 14 天，不含今天）最后一道工序的产出去重数量
  - 每天展示三个值：
      - 日完成量（total_count）：当天去重后的产出数量（只统计最后一道工序）
      - 日均小时完成量（avg_hourly）：当天产出 ÷ 当天有产出的小时数（只统计最后一道工序）
      - 日均一次合格率（first_pass_rate）：当天一次合格报工记录数 ÷ 当天报工记录总数 × 100
        （一次合格率不筛最后一道工序，按原始报工记录计算，复用 calc_check_result 口径）
  - 按看板配置的产品型号过滤（报工表 production_type）
"""
import datetime

from mg_app_framework import get_logger

from trace_app.utils.collection_utils import get_records_coll, calc_check_result
from trace_app.service.last_process_service import get_last_process_codes


def _extract_day(op_time):
    """提取操作时间的日期部分（兼容字符串 / datetime）"""
    if isinstance(op_time, datetime.datetime):
        return op_time.strftime("%Y-%m-%d")
    if isinstance(op_time, str) and len(op_time) >= 10:
        return op_time[0:10]
    return None


def _extract_hour(op_time):
    """提取操作时间的小时（含日期）部分（兼容字符串 / datetime）"""
    if isinstance(op_time, datetime.datetime):
        return op_time.strftime("%Y-%m-%d %H")
    if isinstance(op_time, str) and len(op_time) >= 13:
        return op_time[0:13]
    return None


async def get_history_output(product_types=None):
    """统计前两周每天的完成量 / 日均小时完成量 / 日均一次合格率

    Args:
        product_types: 产品型号列表（可空；非空时只统计这些产品型号）

    Returns:
        {"days": [{"date": "MM-DD", "total_count": int, "avg_hourly": float, "first_pass_rate": float}, ...]}
        按日期升序（最早在前），共 14 天
    """
    now = datetime.datetime.now()
    # 前两周（不含今天）：[今天-14天 00:00:00, 今天 00:00:00)
    start = (now - datetime.timedelta(days=14)).replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_str = start.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end.strftime("%Y-%m-%d %H:%M:%S")

    # 基础查询（不含工序过滤）：out + 时间范围 + 产品型号
    query = {
        "op_type": "out",
        "op_time": {"$gte": start_str, "$lt": end_str},
        "qr_code": {"$ne": ""},
    }
    if product_types:
        query["production_type"] = {"$in": list(product_types)}

    try:
        # 1. 一次合格率：不筛最后工序、不按码去重，直接按报工记录统计
        day_rate = await _fetch_day_rate(query)

        # 2. 日完成量 / 日均小时：加最后工序过滤 + 按码去重
        query_actual = dict(query)
        last_process_codes = await get_last_process_codes(product_types)
        if last_process_codes:
            query_actual["procedure_code"] = {"$in": list(last_process_codes)}
        day_actual = await _fetch_day_actual(query_actual)

        # 组装 14 天（升序：今天-14 ... 今天-1），无产出的天补 0
        days = []
        for offset in range(14, 0, -1):
            d = now - datetime.timedelta(days=offset)
            day_key = d.strftime("%Y-%m-%d")
            actual_entry = day_actual.get(day_key, {"total": 0, "hours": set()})
            rate_entry = day_rate.get(day_key, {"total": 0, "qualified": 0})
            hours_count = len(actual_entry["hours"])
            avg_hourly = round(actual_entry["total"] / hours_count, 2) if hours_count else 0
            first_pass_rate = round(rate_entry["qualified"] / rate_entry["total"] * 100, 2) if rate_entry["total"] else 0
            days.append({
                "date": d.strftime("%m-%d"),
                "total_count": actual_entry["total"],
                "avg_hourly": avg_hourly,
                "first_pass_rate": first_pass_rate,
            })

        return {"days": days}
    except Exception as e:
        get_logger().exception("计算历史产量失败: %s", e)
        return {"days": []}


async def _fetch_day_rate(query):
    """一次合格率按天统计：不按码去重，原样数报工记录

    Returns:
        {day: {"total": 记录数, "qualified": 一次合格记录数}}
    """
    coll = await get_records_coll()
    day_map = {}
    async for doc in coll.find(
        query,
        {"_id": 0, "op_time": 1, "check_result": 1, "production_model": 1},
    ):
        op = doc.get("op_time")
        if not isinstance(op, (str, datetime.datetime)):
            continue
        day = _extract_day(op)
        if not day:
            continue
        entry = day_map.setdefault(day, {"total": 0, "qualified": 0})
        entry["total"] += 1
        # 一次合格：检测结果为空且生产模式为 normal（复用 calc_check_result 口径）
        if calc_check_result(doc.get("check_result", ""), doc.get("production_model", "")) == "一次合格":
            entry["qualified"] += 1
    return day_map


async def _fetch_day_actual(query):
    """日完成量 / 日均小时按天统计：按码去重，取最新一条报工

    Returns:
        {day: {"total": 去重产出数, "hours": 有产出的小时集合}}
    """
    coll = await get_records_coll()
    # 同一码去重：保留最新一条报工（一个产品只计一次产出）
    latest = {}  # qr -> op_time
    async for doc in coll.find(query, {"_id": 0, "op_time": 1, "qr_code": 1}):
        op = doc.get("op_time")
        if not isinstance(op, (str, datetime.datetime)):
            continue
        qr = doc.get("qr_code", "")
        if not qr:
            continue
        prev = latest.get(qr)
        if prev is None or str(op) > str(prev):
            latest[qr] = op

    day_map = {}
    for op in latest.values():
        day = _extract_day(op)
        if not day:
            continue
        entry = day_map.setdefault(day, {"total": 0, "hours": set()})
        entry["total"] += 1
        hour = _extract_hour(op)
        if hour:
            entry["hours"].add(hour)
    return day_map
