#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
设备实时状态服务

  - 订阅 MQ `time_interval_status`（device_exception_compute 推送），
    将设备状态码实时维护在进程内 map 中
  - 启动时从 device_exception_status_interval 表预填各设备最新状态码，
    避免服务重启后（在收到下一条 MQ 前）状态全空
  - 状态码简化：4/5/6(断流/缺料/满料) → 2(待机)，对外只保留 0 关机 / 1 运行 / 2 待机 / 3 故障

与 ylzn_board 对齐：状态码 value 直接来自 `time_interval_status` 消息，
前端按 ['关机','运行','待机','故障'] 映射展示。
"""
import asyncio

from mg_app_framework import get_logger

from trace_app.utils.collection_utils import get_device_exception_status_interval_coll

# 设备实时状态映射：{device_code: status_code}
_device_status_map = {}
_loaded = False
_load_lock = asyncio.Lock()


def to_simplify_status(status_code):
    """简化状态码：断流/缺料/满料(4/5/6) 归并为待机(2)，其余原样"""
    try:
        value = int(status_code)
    except (TypeError, ValueError):
        return 0
    if value in (4, 5, 6):
        return 2
    return value


def get_device_status_map():
    """获取全量设备状态映射副本 {device_code: status_code}"""
    return dict(_device_status_map)


def get_device_status(device_code):
    """获取单设备状态码，无记录默认 0（关机）"""
    return _device_status_map.get(device_code, 0)


def update_device_status(data):
    """MQ `time_interval_status` 处理：更新设备实时状态"""
    try:
        device_code = data.get("device_code")
        if not device_code:
            return
        status_code = to_simplify_status(data.get("value"))
        _device_status_map[device_code] = status_code
        get_logger().debug("设备状态更新 device_code:%s status:%s", device_code, status_code)
    except Exception as e:
        get_logger().error("更新设备状态失败:%s", e)


async def load_initial_device_status():
    """启动时从 device_exception_status_interval 表预填各设备最新状态码（幂等，重复调用直接返回）"""
    global _loaded
    if _loaded:
        return
    async with _load_lock:
        if _loaded:
            return
        try:
            coll = await get_device_exception_status_interval_coll()
            pipeline = [
                {"$match": {"status_code": {"$exists": True}}},
                {"$sort": {"start_time": -1}},
                {"$group": {"_id": "$device_code", "status_code": {"$first": "$status_code"}}},
            ]
            count = 0
            async for doc in coll.aggregate(pipeline):
                device_code = doc.get("_id")
                status_code = doc.get("status_code")
                if device_code:
                    _device_status_map[device_code] = to_simplify_status(status_code)
                    count += 1
            _loaded = True
            get_logger().info("设备状态预填完成，共 %s 台设备", count)
        except Exception as e:
            get_logger().error("设备状态预填失败:%s", e)
