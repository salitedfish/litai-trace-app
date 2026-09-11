from mg_app_framework import get_organization

from trace_app.utils.db import get_collection_handler, get_db_handler


def _get_db_name(db_suffix):
    org = get_organization()
    return f"{org}_{db_suffix}"


async def get_records_coll():
    """获取报工记录表（work_order_retrospect_records）集合句柄"""
    return await get_collection_handler("work_order_retrospect_records", _get_db_name("order_retrospect"))


async def get_father_worksheet_coll():
    """获取排产表（father_worksheet）集合句柄

    排产表在 {org}_scheduler 库，由 changyuan_scheduler_app 写入，只读不自动建集合。
    """
    org = get_organization()
    db = await get_db_handler(f"{org}_scheduler")
    return db.get_collection("father_worksheet")


async def get_process_coll():
    """获取工序信息表（production_config_mgm_process_info）集合句柄"""
    return await get_collection_handler("production_config_mgm_process_info", _get_db_name("config"))


async def get_routing_process_info_coll():
    """获取工艺路线明细表（production_config_mgm_routing_process_info）集合句柄"""
    return await get_collection_handler("production_config_mgm_routing_process_info", _get_db_name("config"))


async def get_production_config_type_coll():
    """获取产品型号-工艺路线配置表（production_config_type）集合句柄"""
    return await get_collection_handler("production_config_type", _get_db_name("config"))


async def get_web_layout_application_coll():
    """获取 Web 布局应用配置表（web_layout_application）集合句柄"""
    idi_db = f"idi_{get_organization()}"
    return await get_collection_handler("web_layout_application", idi_db)


async def get_device_coll():
    """获取设备配置表（device）集合句柄"""
    idi_db = f"idi_{get_organization()}_cloud_management"
    return await get_collection_handler("device", idi_db)


async def get_users_coll():
    """获取用户表（users）集合句柄"""
    return await get_collection_handler("users", "manugence_root")


async def get_gycs_coll():
    """获取工艺参数表（gycs_data）集合句柄"""
    return await get_collection_handler("gycs_data", _get_db_name("traceback"))


async def get_process_params_config_coll():
    """获取工艺参数配置表（process_params_config）集合句柄"""
    return await get_collection_handler("process_params_config", _get_db_name("manual_trace"))


async def get_inspection_records_coll():
    """获取检验单记录表（inspection_records）集合句柄

    检验单由 manual_line_general_traceability 落库，workorder_code 关联报工的
    完整追溯工单号（qr_workorder_code），存放在 {org}_manual_trace 库，只读。
    """
    return await get_collection_handler("inspection_records", _get_db_name("manual_trace"))


async def get_material_scan_records_coll():
    """获取扫码登料记录表（material_scan_records）集合句柄

    扫码登料记录由 manual_line_general_traceability 落库，存放在 {org}_manual_trace 库，只读。
    """
    return await get_collection_handler("material_scan_records", _get_db_name("manual_trace"))


async def get_datas_coll():
    """获取数采数据表（datas）集合句柄"""
    idi_db = f"idi_{get_organization()}"
    return await get_collection_handler("datas", idi_db)


async def get_device_exception_status_interval_coll():
    """获取设备状态时间片表（device_exception_status_interval）集合句柄"""
    idi_db = f"idi_{get_organization()}"
    return await get_collection_handler("device_exception_status_interval", idi_db)


def calc_check_result(raw_check, prod_model):
    """根据原始检测结果和生产模式计算显示用检测结果

    Args:
        raw_check: 数据库中的原始检测结果
        prod_model: 生产模式（normal/rework/resubmission）

    Returns:
        格式化后的检测结果字符串
    """
    if raw_check == "" and prod_model == "rework":
        return "返工合格"
    if raw_check == "" and prod_model == "resubmission":
        return "复投合格"
    if raw_check == "":
        return "一次合格"
    if raw_check == "合格":
        return "返工合格"
    return raw_check


async def enrich_device_names(device_codes, steps):
    """批量查询设备名称并填充到追溯步骤中

    根据 device_codes 集合从 device 表查询设备名称，填充到 steps 列表的每个元素的 device_name 字段。

    Args:
        device_codes: 设备编码集合（set 或 list）
        steps: 追溯步骤列表，每个元素需包含 device_code 字段
    """
    if not device_codes:
        return
    try:
        device_coll = await get_device_coll()
        device_name_map = {}
        async for d in device_coll.find(
            {"code": {"$in": list(device_codes)}},
            projection={"code": 1, "name": 1}
        ):
            device_name_map[d.get("code")] = d.get("name", "")
        for item in steps:
            dc = item.get("device_code", "")
            if dc in device_name_map:
                item["device_name"] = device_name_map[dc]
    except Exception:
        from mg_app_framework import get_logger
        get_logger().exception("查询设备名称失败")


async def enrich_user_names(operator_ids, steps):
    """批量查询用户昵称并填充到追溯步骤中

    根据 operator_ids 集合从 users 表查询用户昵称，替换 steps 列表的每个元素的 operator 字段。

    Args:
        operator_ids: 操作人工号集合（set 或 list）
        steps: 追溯步骤列表，每个元素需包含 operator（工号）字段
    """
    if not operator_ids:
        return
    try:
        users_coll = await get_users_coll()
        user_map = {}
        async for u in users_coll.find(
            {"work_id": {"$in": list(operator_ids)}},
            projection={"work_id": 1, "user_nickname": 1}
        ):
            user_map[u.get("work_id")] = u.get("user_nickname", "")
        for item in steps:
            op_id = item.get("operator", "")
            if op_id in user_map:
                item["operator"] = user_map[op_id]
    except Exception:
        from mg_app_framework import get_logger
        get_logger().exception("查询用户名称失败")
