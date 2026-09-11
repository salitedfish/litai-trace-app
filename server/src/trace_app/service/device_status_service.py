#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
设备实时状态服务

  - 订阅 MQ `time_interval_status`（device_exception_compute 推送），
    将设备状态码实时维护在进程内 map 中
  - 启动时从 device_exception_status_interval 表预填各设备最新状态码，
    避免服务重启后（在收到下一条 MQ 前）状态全空
  - 定时对账：周期重读表的最新状态覆盖内存 map，纠正漏收 MQ 消息导致的陈旧状态
  - 状态码简化：4/5/6(断流/缺料/满料) → 2(待机)，对外只保留 0 关机 / 1 运行 / 2 待机 / 3 故障

与 ylzn_board 对齐：状态码 value 直接来自 `time_interval_status` 消息，
前端按 ['关机','运行','待机','故障'] 映射展示。
"""
import asyncio
import time

from mg_app_framework import get_logger

from trace_app.utils.collection_utils import get_device_exception_status_interval_coll

# 设备实时状态映射：{device_code: status_code}
_device_status_map = {}
_loaded = False
_load_lock = asyncio.Lock()
# 定时对账周期（秒）：`time_interval_status` 是事件驱动，只在设备状态变化时发，
# 漏收一条事件就会永久陈旧，需周期从表重读兜底
_REFRESH_INTERVAL = 60
_last_refresh_time = 0


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


async def update_device_status(data):
    """MQ `time_interval_status` 处理：更新设备实时状态

    必须是协程：mq_config 的分发器对所有订阅函数统一 `await`，
    返回 None 的同步函数会让它抛 `TypeError: object NoneType can't be used in 'await' expression`，
    该条消息就被吞掉（只更新内存 map，本身不阻塞，所以写成协程无副作用）。
    """
    try:
        device_code = data.get("device_code")
        if not device_code:
            return
        status_code = to_simplify_status(data.get("value"))
        _device_status_map[device_code] = status_code
        get_logger().debug("设备状态更新 device_code:%s status:%s", device_code, status_code)
    except Exception as e:
        get_logger().error("更新设备状态失败:%s", e)


async def _load_status_from_table():
    """从 device_exception_status_interval 表重读各设备当前活跃时间片的状态码

    只取当前活跃时间片（end_time 为空/不存在），按 start_time 倒序取最新一条 ——
    约定：end_time=null 的最新一条即设备当前状态。返回 (新状态映射, 设备数)；
    查询失败返回 (None, -1)。
    """
    try:
        coll = await get_device_exception_status_interval_coll()
        pipeline = [
            {"$match": {
                "status_code": {"$exists": True},
                "$or": [{"end_time": None}, {"end_time": {"$exists": False}}],
            }},
            {"$sort": {"start_time": -1}},
            {"$group": {"_id": "$device_code", "status_code": {"$first": "$status_code"}}},
        ]
        new_map = {}
        count = 0
        async for doc in coll.aggregate(pipeline):
            device_code = doc.get("_id")
            status_code = doc.get("status_code")
            if device_code:
                new_map[device_code] = to_simplify_status(status_code)
                count += 1
        return new_map, count
    except Exception as e:
        get_logger().error("从表重读设备状态失败:%s", e)
        return None, -1


async def load_initial_device_status():
    """启动时从 device_exception_status_interval 表预填各设备最新状态码（幂等，重复调用直接返回）"""
    global _loaded
    if _loaded:
        return
    async with _load_lock:
        if _loaded:
            return
        new_map, count = await _load_status_from_table()
        if new_map is None:
            return
        _device_status_map.clear()
        _device_status_map.update(new_map)
        _loaded = True
        get_logger().info("设备状态预填完成，共 %s 台设备", count)


async def refresh_device_status():
    """周期对账：从表重读各设备最新状态整体覆盖内存 map，纠正漏收 MQ 消息导致的陈旧状态

    `time_interval_status` 是事件驱动、只在状态变化时发的，漏收一条就会让该设备永久陈旧；
    对账后任意实例最终都会收敛到表里的真值，实例之间不再长期分叉。
    """
    global _last_refresh_time
    async with _load_lock:
        new_map, count = await _load_status_from_table()
        if new_map is None:
            return
        _device_status_map.clear()
        _device_status_map.update(new_map)
        _last_refresh_time = time.time()
        if count:
            get_logger().debug("设备状态对账完成，共 %s 台设备", count)


async def refresh_device_status_if_needed():
    """按 _REFRESH_INTERVAL 节流触发对账（由 WebSocket push 每 5 秒调用）"""
    global _last_refresh_time
    if not _last_refresh_time:
        return
    if time.time() - _last_refresh_time < _REFRESH_INTERVAL:
        return
    await refresh_device_status()
