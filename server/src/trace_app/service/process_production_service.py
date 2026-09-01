#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
工序加工情况计算服务

  - 从 work_order_retrospect_records 报工记录统计各工序的产出与合格率
  - 只统计产出记录（op_type='out'），按工序编码分组
  - 三个口径（均按报工记录条数，不去重）：
      total        产出数量 = 该工序 out 记录条数
      first_pass   一次合格数 = check_result 为空 且 生产模式为 normal（首检即合格）
      total_good   总体合格数 = check_result 为空 或 为"合格"（含返工/复投后合格）
    注：同一码先报不合格再返工合格，会占两条记录（一条不合格 + 一条合格），
        返工产品会把总体合格率拉低（例如 1 条不合格 + 1 条返工合格 = 50%）。
  - 工序名称从 production_config_mgm_process_info 工序信息表查询
"""
import datetime

from mg_app_framework import get_logger

from trace_app.utils.collection_utils import get_process_coll, get_records_coll, calc_check_result


async def get_process_production(start_time=None, end_time=None):
    """计算各工序的产出数量 / 一次合格率 / 总体合格率

    Args:
        start_time: 统计起始时间（datetime，None 为当天 0 点）
        end_time: 统计结束时间（datetime，None 为当天 23:59:59）

    Returns:
        工序加工情况列表，按工序编码升序：
        [{procedure_code, procedure_name, total, first_pass, total_good,
          first_pass_rate, total_rate}]
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
        stats = {}
        async for doc in coll.find(
            {"op_type": "out", "op_time": {"$gte": start_str, "$lt": end_str}},
            {"_id": 0, "procedure_code": 1, "check_result": 1, "production_model": 1},
        ):
            code = doc.get("procedure_code")
            if not code:
                continue
            check_result = doc.get("check_result", "")
            prod_model = doc.get("production_model", "")
            s = stats.setdefault(code, {"total": 0, "first_pass": 0, "total_good": 0})
            s["total"] += 1
            # 总体合格：最终结果合格（一次合格 / 返工合格 / 复投合格）
            if check_result in ("", "合格"):
                s["total_good"] += 1
            # 一次合格：首检即合格（复用 calc_check_result 口径）
            if calc_check_result(check_result, prod_model) == "一次合格":
                s["first_pass"] += 1

        if not stats:
            return []

        # 工序名称（工序编码 → 工序名称，查不到时回退显示编码）
        name_map = await _get_process_name_map(list(stats.keys()))

        result = []
        for code, s in stats.items():
            total = s["total"]
            result.append({
                "procedure_code": code,
                "procedure_name": name_map.get(code, code),
                "total": total,
                "first_pass": s["first_pass"],
                "total_good": s["total_good"],
                "first_pass_rate": round(s["first_pass"] / total * 100, 2) if total else 0,
                "total_rate": round(s["total_good"] / total * 100, 2) if total else 0,
            })

        # 按工序编码升序
        result.sort(key=lambda x: x["procedure_code"])
        return result
    except Exception as e:
        get_logger().exception("计算工序加工情况失败: %s", e)
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
