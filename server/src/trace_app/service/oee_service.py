#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
OEE 计算服务

  - OEE、时间开动率、性能开动率 → datas 集合的 zb_r_* KPI 数据
  - 合格率 → work_order_retrospect_records 报工记录
"""
import datetime

from mg_app_framework import get_logger

from trace_app.utils.collection_utils import get_datas_coll, get_device_coll, get_records_coll

# KPI 编码常量
KPI_DAILY_OUTPUT = "zb_r_cl"  # 日累计产量
KPI_PROCESS_TIME = "zb_r_sbjgsj"  # 日加工时间
KPI_WORK_TIME = "zb_r_sbsbsj"  # 日上班时间（计划工时）
KPI_SHUTDOWN_TIME = "zb_r_sbgjsj"  # 日关机时间
KPI_INTERRUPTION = "zb_r_sbzdsj"  # 设备中断时间


async def _get_total_kpi(device_codes, kpi_suffix, time_start, time_end):
    """按设备列表聚合指定 KPI 在时间范围内的总值"""
    if not device_codes:
        return 0

    coll = await get_datas_coll()
    kpi_codes = [f"{dev}~{kpi_suffix}" for dev in device_codes]

    match = {
        "code": {"$in": kpi_codes},
        "timestamp": {"$gte": time_start, "$lt": time_end},
    }
    group = {"_id": None, "count": {"$sum": "$value"}}

    total = 0
    try:
        async for doc in coll.aggregate([{"$match": match}, {"$group": group}]):
            total += doc["count"]
    except Exception as e:
        get_logger().exception("聚合 KPI 失败: %s", e)

    return total


async def _get_workshop_device_codes():
    """获取产线设备编码列表"""
    try:
        coll = await get_device_coll()
        devices = await coll.find(
            {"type": "device"},
            projection={"code": 1},
        ).to_list(length=500)
        return [d["code"] for d in devices if d.get("code")]
    except Exception as e:
        get_logger().exception("查询设备列表失败: %s", e)
        return []


async def _calc_quality_rate(time_start, time_end):
    """从报工记录计算合格率

    逻辑：统计当天所有产出 qr_code，有过非空 check_result（不合格）就算不良品。
    返工后合格的 qr_code 仍会计为不良品，因为它在某次检验中确实不合格过。
    """
    try:
        coll = await get_records_coll()
        start_str = time_start.strftime("%Y-%m-%d %H:%M:%S")
        end_str = time_end.strftime("%Y-%m-%d %H:%M:%S")

        match = {"op_type": "out", "op_time": {"$gte": start_str, "$lt": end_str}}

        # 总记录数
        total = await coll.count_documents(match)
        if total == 0:
            return None

        # 合格记录数（check_result 为空）
        good_match = {**match, "check_result": ""}
        good = await coll.count_documents(good_match)

        return good / total
    except Exception as e:
        get_logger().exception("计算合格率失败: %s", e)
        return None


async def calculate_oee(start_time=None, end_time=None):
    """计算产线 OEE 及三个子指标"""
    now = datetime.datetime.now()
    if start_time is None:
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if end_time is None:
        end_time = now.replace(hour=23, minute=59, second=59, microsecond=0)

    devices = await _get_workshop_device_codes()

    # OEE、时间开动率、性能开动率 ← datas
    total_pcl = await _get_total_kpi(devices, KPI_DAILY_OUTPUT, start_time, end_time)
    total_jgsj = await _get_total_kpi(devices, KPI_PROCESS_TIME, start_time, end_time)
    total_gjsj = await _get_total_kpi(devices, KPI_SHUTDOWN_TIME, start_time, end_time)
    total_zdsj = await _get_total_kpi(devices, KPI_INTERRUPTION, start_time, end_time)
    total_sbsj = await _get_total_kpi(devices, KPI_WORK_TIME, start_time, end_time)

    # 合格率 ← work_order_retrospect_records
    hgl = await _calc_quality_rate(start_time, end_time)

    # 合格率 — 始终计算
    hgl_display = round(hgl * 100, 2) if isinstance(hgl, float) else '-'

    # OEE / 时间开动率 / 性能开动率：没有 KPI 时间数据就返回空
    if not total_sbsj and not total_pcl:
        return [
            {"name": "目标值", "value": 99},
            {"name": "oee", "value": "-", "max": 100},
            {"name": "时间开动率", "value": "-"},
            {"name": "性能开动率", "value": "-"},
            {"name": "合格率", "value": hgl_display},
        ]

    total_sbgzsj = total_sbsj - total_gjsj - total_zdsj  # 实际工作时间
    if not total_sbgzsj:
        total_sbgzsj = 1
    if not total_sbsj:
        total_sbsj = 1

    sjjdl = total_sbgzsj / total_sbsj  # 时间开动率
    xnjdl = total_jgsj / total_sbgzsj  # 性能开动率

    # OEE（三个子指标都必须有值才能算）
    oee_val = round(sjjdl * xnjdl * hgl * 100, 1) if isinstance(hgl, float) else '-'

    return [
        {"name": "目标值", "value": 99},
        {"name": "oee", "value": oee_val, "max": 100},
        {"name": "时间开动率", "value": round(sjjdl * 100, 2)},
        {"name": "性能开动率", "value": round(xnjdl * 100, 2)},
        {"name": "合格率", "value": hgl_display},
    ]
