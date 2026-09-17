#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
智能看板2 - 检验项不合格占比统计服务

  - 数据源 inspection_records（{org}_manual_trace，manual_line 报工时落库的检验单，只读）
  - 口径：样本 = 不合格检验项。每张检验单 items 中 is_qualified=False 的项各计 1，
        按 item_code 聚合；扇区占比 = 该检验项不合格次数 ÷ 全部不合格项总数（前端算百分比）
  - 筛选（与看板2 配置一致，空即不限）：
      1) 查询日期区间：op_time 字符串比较（YYYY-MM-DD HH:MM:SS.fff，>= 起 00:00:00、< 止+1天 00:00:00）
      2) 产线：车间代号 → 布局表 web_layout_application 取该车间生产单元代号集合，
               按 produce_unit_code $in 过滤（检验单无车间字段）
      3) 产品型号：型号编码（production_config_type.production_type）人工与产品编码一致，
               按 product_code $in 过滤
"""
import datetime

from mg_app_framework import get_logger

from trace_app.utils.collection_utils import (
    collect_unqualified_reason_counts,
    get_inspection_records_coll,
    get_web_layout_application_coll,
)


async def get_unqualified_pie(start_date=None, end_date=None, workshop_code=None, product_types=None):
    """统计各检验项不合格次数（供看板2 饼图展示）

    Args:
        start_date: 起始日期（YYYY-MM-DD，None/空为当天）
        end_date: 截止日期（YYYY-MM-DD，含当天；None/空为当天）
        workshop_code: 产线编码（车间代号，None/空为全部产线）
        product_types: 产品型号列表（None/空为不限）

    Returns:
        按不合格次数降序的列表：[{item_code, item_name, count}]
    """
    try:
        start_str, end_exclusive_str = _resolve_time_range(start_date, end_date)

        query = {
            "op_time": {"$gte": start_str, "$lt": end_exclusive_str},
            "is_delete": {"$ne": True},
        }

        # 产线过滤：布局表查该车间全部生产单元代号；车间无生产单元 → 无数据
        if workshop_code:
            unit_codes = await _get_workshop_unit_codes(workshop_code)
            if not unit_codes:
                return []
            query["produce_unit_code"] = {"$in": list(unit_codes)}

        # 产品型号过滤：型号编码与产品编码人工保持一致，直接匹配 product_code
        if product_types:
            query["product_code"] = {"$in": list(product_types)}

        coll = await get_inspection_records_coll()
        stats = {}
        async for doc in coll.find(query, {"_id": 0, "items": 1}):
            for item in doc.get("items") or []:
                if item.get("is_qualified"):
                    continue
                item_code = item.get("item_code") or ""
                if not item_code:
                    continue
                entry = stats.setdefault(item_code, {"item_name": "", "count": 0})
                entry["count"] += 1
                if not entry["item_name"]:
                    entry["item_name"] = item.get("item_name") or item_code

        if not stats:
            return []

        # item_name 缺失时回退显示编码
        result = [
            {"item_code": code, "item_name": s["item_name"] or code, "count": s["count"]}
            for code, s in stats.items()
        ]
        result.sort(key=lambda x: x["count"], reverse=True)
        return result
    except Exception as e:
        get_logger().exception("统计检验项不合格占比失败: %s", e)
        return []


async def get_unqualified_reason_pie(start_date=None, end_date=None, workshop_code=None, product_types=None):
    """统计各不合格原因被勾选次数（供看板2 不合格原因占比饼图展示）

    口径：样本 = 不合格检验项勾选的原因快照。每张检验单 items 中 is_qualified=False 的项，
    其 unqualified_reasons（[{reason_code, reason_name}]）逐条各计 1（一项可勾多个原因都计入）；
    未勾原因的不合格项（检验项档案未配原因、或该类型原本不允许配原因的旧快照）不进入统计。
    占比 = 该原因被勾选次数 ÷ 全部勾选原因总次数（前端算百分比）。

    Args:
        start_date: 起始日期（YYYY-MM-DD，None/空为当天）
        end_date: 截止日期（YYYY-MM-DD，含当天；None/空为当天）
        workshop_code: 产线编码（车间代号，None/空为全部产线）
        product_types: 产品型号列表（None/空为不限）

    Returns:
        按被勾选次数降序的列表：[{reason_code, reason_name, count}]
    """
    try:
        start_str, end_exclusive_str = _resolve_time_range(start_date, end_date)

        query = {
            "op_time": {"$gte": start_str, "$lt": end_exclusive_str},
            "is_delete": {"$ne": True},
        }

        # 产线过滤：布局表查该车间全部生产单元代号；车间无生产单元 → 无数据
        if workshop_code:
            unit_codes = await _get_workshop_unit_codes(workshop_code)
            if not unit_codes:
                return []
            query["produce_unit_code"] = {"$in": list(unit_codes)}

        # 产品型号过滤：型号编码与产品编码人工保持一致，直接匹配 product_code
        if product_types:
            query["product_code"] = {"$in": list(product_types)}

        coll = await get_inspection_records_coll()
        # 聚合口径见 collect_unqualified_reason_counts（报工不合格原因页共用同一份）
        return await collect_unqualified_reason_counts(coll.find(query, {"_id": 0, "items": 1}))
    except Exception as e:
        get_logger().exception("统计不合格原因占比失败: %s", e)
        return []


def _resolve_time_range(start_date, end_date):
    """把日期参数解析成 op_time 字符串比较区间（含起、不含止）

    Returns:
        (start_str, end_exclusive_str)：'YYYY-MM-DD HH:MM:SS' 字符串，空日期取当天
    """
    now = datetime.datetime.now()
    start_dt = _parse_date(start_date) or now
    end_dt = _parse_date(end_date) or now
    start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    end_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    if end_dt < start_dt:
        start_dt, end_dt = end_dt, start_dt
    # 截止日期含当天 → 上限取次日 0 点（开区间），保证整日数据都纳入
    end_exclusive = end_dt + datetime.timedelta(days=1)
    return start_dt.strftime("%Y-%m-%d %H:%M:%S"), end_exclusive.strftime("%Y-%m-%d %H:%M:%S")


def _parse_date(date_str):
    """解析 YYYY-MM-DD 日期字符串，解析失败返回 None"""
    if not date_str:
        return None
    try:
        return datetime.datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
    except (TypeError, ValueError):
        return None


async def _get_workshop_unit_codes(workshop_code):
    """布局表按车间代号（产线）取该车间下全部生产单元代号集合（去重）

    检验单只带生产单元编码（produce_unit_code），没有车间/产线字段；
    产线过滤须先经布局表把车间代号映射到生产单元代号。
    """
    unit_codes = set()
    try:
        layout_coll = await get_web_layout_application_coll()
        async for doc in layout_coll.find(
            {"车间代号": workshop_code},
            {"_id": 0, "生产单元代号": 1},
        ):
            code = doc.get("生产单元代号")
            if code:
                unit_codes.add(code)
    except Exception as e:
        get_logger().exception("查询产线生产单元失败: %s", e)
    return unit_codes
