#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
最后一道工序查询服务

链路：产品型号(production_config_type) → 工艺路线(routing_code) → 最后一道工序
（production_config_mgm_routing_process_info 按工序顺序取最大）。

用于小时产量 / 实际产量只统计最后工序的报工产出，以及计划产量按最后工序
匹配 father_worksheet（该表按「任务 × 工序」拆行，同一物料每个工序都有相同 count，
不按最后工序过滤会把计划量乘以工序数）。
"""
from mg_app_framework import get_logger

from trace_app.utils.collection_utils import get_production_config_type_coll, get_routing_process_info_coll


async def get_last_process_map(product_types=None):
    """产品型号 → 最后一道工序编码 映射

    Args:
        product_types: 产品型号列表（可空；空则取全部产品型号对应的工艺路线）

    Returns:
        dict: {产品型号: 最后工序编码}
    """
    try:
        # 1. 产品型号 → 工艺路线（production_config_type）
        routing_query = {}
        if product_types:
            routing_query = {"production_type": {"$in": list(product_types)}}
        pt_to_routing = {}
        async for doc in (await get_production_config_type_coll()).find(
            routing_query, {"production_type": 1, "routing_code": 1}
        ):
            pt = doc.get("production_type")
            rc = doc.get("routing_code")
            if pt and rc and pt not in pt_to_routing:
                pt_to_routing[pt] = rc

        if not pt_to_routing:
            return {}

        # 2. 工艺路线 → 最后一道工序（工艺路线明细按工序顺序降序取第一条）
        routing_coll = await get_routing_process_info_coll()
        last_process_map = {}
        for pt, rc in pt_to_routing.items():
            doc = await routing_coll.find_one(
                {"工艺路线编码": rc},
                {"工序编码": 1},
                sort=[("工序顺序", -1)],
            )
            pc = doc.get("工序编码") if doc else None
            if pc:
                last_process_map[pt] = pc
        return last_process_map
    except Exception as e:
        get_logger().exception("查询最后一道工序失败: %s", e)
        return {}


async def get_last_process_codes(product_types=None):
    """根据产品型号查询最后一道工序编码集合（报工表过滤用）"""
    return set((await get_last_process_map(product_types)).values())
