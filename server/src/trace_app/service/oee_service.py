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
from trace_app.utils.device_utils import normalize_device_codes

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


async def _calc_quality_rate(time_start, time_end, exclude_devices=None):
    """从报工记录计算合格率

    逻辑：统计当天所有产出 qr_code，有过非空 check_result（不合格）就算不良品。
    返工后合格的 qr_code 仍会计为不良品，因为它在某次检验中确实不合格过。
    """
    try:
        coll = await get_records_coll()
        start_str = time_start.strftime("%Y-%m-%d %H:%M:%S")
        end_str = time_end.strftime("%Y-%m-%d %H:%M:%S")

        match = {"op_type": "out", "op_time": {"$gte": start_str, "$lt": end_str}}

        # 未使用的设备整体排除出合格率统计（报工记录带 device_code 字段）。
        # 用 $nin 而不是 $ne：device_code 缺失或为空的历史记录不属于任何被排除设备，
        # 保持原样计入分子分母，别顺手把它们一起剔掉——那会改变既有的合格率口径。
        if exclude_devices:
            match["device_code"] = {"$nin": list(exclude_devices)}

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


async def calculate_oee(start_time=None, end_time=None, exclude_devices=None):
    """计算产线 OEE 及三个子指标

    OEE = 时间开动率 × 性能开动率 × 合格率

    exclude_devices：看板配置里的「未使用的设备」编码列表，这些设备整体不参与统计
    （含合格率）。空/未传时行为与改动前完全一致。
    """
    now = datetime.datetime.now()
    if start_time is None:
        # 默认统计区间：当天 0 点起
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if end_time is None:
        # 默认统计区间：到当天 23:59:59 止
        end_time = now.replace(hour=23, minute=59, second=59, microsecond=0)

    # 参与统计的设备列表（当前为全部 type=device 的数采设备，未按产线过滤）
    devices = await _get_workshop_device_codes()

    # 排除未使用的设备：从设备名单里剔掉即可，下面 5 个 KPI 全部按这个名单聚合，
    # 一处过滤全部生效；合格率另走报工记录，单独传下去
    excluded = normalize_device_codes(exclude_devices)
    if excluded:
        devices = [code for code in devices if code not in excluded]

    # ---- 以下 KPI 均从 datas 表聚合（按「设备码~KPI码」求和，单位：数量/小时） ----
    # 总产量：全部设备「日累计产量」zb_r_cl 之和，单位：件
    total_pcl = await _get_total_kpi(devices, KPI_DAILY_OUTPUT, start_time, end_time)
    # 总加工时间：全部设备「日加工时间」zb_r_sbjgsj 之和，单位：小时
    total_jgsj = await _get_total_kpi(devices, KPI_PROCESS_TIME, start_time, end_time)
    # 总关机时间：全部设备「日关机时间」zb_r_sbgjsj 之和，单位：小时（含关机/急停/调试）
    total_gjsj = await _get_total_kpi(devices, KPI_SHUTDOWN_TIME, start_time, end_time)
    # 总中断时间：全部设备「设备中断时间」zb_r_sbzdsj 之和，单位：小时（仅超中断阈值的部分，不含速度损失）
    total_zdsj = await _get_total_kpi(devices, KPI_INTERRUPTION, start_time, end_time)
    # 总上班时间：全部设备「日上班时间」zb_r_sbsbsj 之和，单位：小时（即计划工时）
    total_sbsj = await _get_total_kpi(devices, KPI_WORK_TIME, start_time, end_time)

    # 合格率：从报工记录表 work_order_retrospect_records 统计
    #   = 合格产出记录数 / 全部产出记录数（op_type=out，check_result 为空视为合格）
    hgl = await _calc_quality_rate(start_time, end_time, excluded)

    # 合格率展示值：转成百分数（乘 100 保留 2 位），无数据时为 '-'
    hgl_display = round(hgl * 100, 2) if isinstance(hgl, float) else '-'

    # 上班时间、产量都没有数据 → 时间/性能开动率无意义，直接返回空值（合格率仍展示）
    if not total_sbsj and not total_pcl:
        return [
            {"name": "目标值", "value": 99},
            {"name": "oee", "value": "-", "max": 100},
            {"name": "时间开动率", "value": "-"},
            {"name": "性能开动率", "value": "-"},
            {"name": "合格率", "value": hgl_display},
        ]

    # 实际工作时间（设备真正在运转的时长）= 上班时间 - 关机时间 - 中断时间，单位：小时
    total_sbgzsj = total_sbsj - total_gjsj - total_zdsj
    # 兜底：避免除数为 0
    if not total_sbgzsj:
        total_sbgzsj = 1
    if not total_sbsj:
        total_sbsj = 1

    # 时间开动率 = 实际工作时间 / 上班时间（反映计划工时内设备真正开动的比例）
    sjjdl = total_sbgzsj / total_sbsj
    # 性能开动率 = 加工时间 / 实际工作时间（反映扣除停机后，实际产出相对理论产能的比例，含速度损失）
    xnjdl = total_jgsj / total_sbgzsj

    # OEE = 时间开动率 × 性能开动率 × 合格率（乘 100 转百分数，保留 1 位）
    # 合格率非数值（'-'）时 OEE 也为 '-'（三个子指标缺一不可）
    oee_val = round(sjjdl * xnjdl * hgl * 100, 1) if isinstance(hgl, float) else '-'

    return [
        {"name": "目标值", "value": 99},
        {"name": "oee", "value": oee_val, "max": 100},
        {"name": "时间开动率", "value": round(sjjdl * 100, 2)},
        {"name": "性能开动率", "value": round(xnjdl * 100, 2)},
        {"name": "合格率", "value": hgl_display},
    ]
