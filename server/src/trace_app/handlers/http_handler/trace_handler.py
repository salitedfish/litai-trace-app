import traceback

from mg_app_framework import get_logger, loginrequired
from tornado_request_mapping import request_mapping

from trace_app.common.base_handler import BaseHandler
from trace_app.entity.response_entity import Response
from trace_app.entity.response_model import (
    TraceQueryRequest,
    TraceDetailRequest,
    TraceDetailResponse,
    InputCodeQueryRequest,
    ProcessParamRequest,
    SubmissionRecordRequest,
    InspectionRecordRequest,
)
from trace_app.utils.swagger_utils import swagger_doc
from trace_app.utils.collection_utils import (
    get_records_coll,
    get_process_coll,
    get_gycs_coll,
    get_process_params_config_coll,
    get_inspection_records_coll,
    calc_check_result,
    enrich_device_names,
    enrich_user_names,
)




@request_mapping('/api/trace_app')
class TraceHandler(BaseHandler):
    """追溯查询处理器 — 产出码/投入码双向递归追溯，关联工艺参数、设备、用户等信息"""

    # =====================================================================
    # 追溯查询（核心）
    # 双向递归：上游（往原材料） + 下游（往成品），按(工序+设备)去重
    # =====================================================================

    @request_mapping('/trace/query_by_output', method='post', description='追溯查询 — 递归查出完整产出链路')
    @swagger_doc(
        tags=["追溯查询"],
        summary="追溯查询",
        description="输入一个产出码（qr_code），递归追溯完整生产链路，返回所有关联的产出记录",
        request_model=TraceQueryRequest,
    )
    @loginrequired
    async def query_by_output(self):
        """产出码递归追溯，双向查完整生产链路"""
        try:
            # ---- 参数校验 ----
            if not self.data or 'qr_code' not in self.data:
                self.send_response(Response.fail("请传入产出码 qr_code"))
                return
            qr_code = self.data['qr_code'].strip()
            if not qr_code:
                self.send_response(Response.fail("产出码不能为空"))
                return

            # ---- 获取集合句柄 ----
            records_coll = await get_records_coll()
            process_coll = await get_process_coll()

            # 工序名称缓存，避免递归中反复查
            process_name_cache = {}

            async def get_process_name(proc_code):
                """根据工序编码查询工序名称，结果缓存"""
                if not proc_code:
                    return ""
                if proc_code not in process_name_cache:
                    p = await process_coll.find_one({"工序编码": proc_code}, projection={"工序名称": 1})
                    process_name_cache[proc_code] = p.get("工序名称", "") if p else ""
                return process_name_cache[proc_code]

            def dedup_by_proc_dev(records):
                """按(工序编码, 设备编码)去重，同一工序+设备多次报工只保留第一条（上游传入已按时间排序）"""
                seen = set()
                result = []
                for r in records:
                    key = (r.get("procedure_code", ""), r.get("device_code", ""))
                    if key not in seen:
                        seen.add(key)
                        result.append(r)
                return result

            # ---- 状态追踪变量 ----
            upstream_visited = set()
            downstream_visited = set()
            processed_workorders = set()
            all_steps = []
            operator_ids = set()
            device_codes = set()

            async def add_step(out_record):
                """将一条产出记录加入追溯链路，收集操作人和设备编码供后续 enrich"""
                wc = out_record.get("workorder_code", "")
                if not wc or wc in processed_workorders:
                    return
                processed_workorders.add(wc)

                proc_code = out_record.get("procedure_code", "")
                proc_name = await get_process_name(proc_code)
                op_id = out_record.get("operator", "") or ""
                dev_code = out_record.get("device_code", "") or ""
                if op_id:
                    operator_ids.add(op_id)
                if dev_code:
                    device_codes.add(dev_code)

                all_steps.append({
                    "workorder_code": wc,
                    "raw_workorder_code": out_record.get("raw_workorder_code", ""),
                    "procedure_code": proc_code,
                    "procedure_name": proc_name,
                    "material_code": out_record.get("material_code", ""),
                    "material_type": out_record.get("material_type", ""),
                    "qr_code": out_record.get("qr_code", ""),
                    "op_time": str(out_record.get("op_time", "")),
                    "operator": op_id,
                    "produce_unit_code": out_record.get("produce_unit_code", ""),
                    "device_code": dev_code,
                    "device_name": "",
                    # 根据生产模式转换检测结果（一次合格/返工合格/复投合格）
                    "check_result": calc_check_result(
                        out_record.get("check_result", ""),
                        out_record.get("production_model", ""),
                    ),
                })

            async def get_inputs_by_workorders(workorder_codes):
                """批量查多个工单的投入记录，避免 N+1"""
                if not workorder_codes:
                    return {}
                inputs_cursor = records_coll.find(
                    {"workorder_code": {"$in": list(workorder_codes)}, "op_type": "in", "is_delete": {"$ne": True}},
                    sort=[("code_index", 1)]
                )
                inputs_map = {}
                async for inp in inputs_cursor:
                    wc = inp.get("workorder_code", "")
                    inputs_map.setdefault(wc, []).append(inp)
                return inputs_map

            async def trace_upstream(code):
                """上游追溯 — 从当前产出码往原材料方向递归

                找到 qr_code 对应的产出记录 → 查同工单的投入记录 →
                取半成品/成品类型的投入码继续递归，原材料作为终点。
                """
                if code in upstream_visited:
                    return
                upstream_visited.add(code)

                out_cursor = records_coll.find(
                    {"qr_code": code, "op_type": "out", "is_delete": {"$ne": True}},
                    sort=[("op_time", -1)]
                )
                out_records = await out_cursor.to_list(length=20)
                if not out_records:
                    return

                out_records = dedup_by_proc_dev(out_records)

                wc_list = [r["workorder_code"] for r in out_records if r.get("workorder_code")]
                inputs_map = await get_inputs_by_workorders(wc_list)

                # 一次报工可能投入多个物料，每个投入码都需要继续追溯（1:N）
                for out in out_records:
                    await add_step(out)
                    for inp in inputs_map.get(out.get("workorder_code", ""), []):
                        await trace_upstream(inp.get("qr_code", ""))

            async def trace_downstream(code):
                """下游追溯 — 从当前产出码往成品方向递归

                找到 qr_code 对应的投入记录（该码被用在哪里）→
                查同工单的产出记录 → 取产出码继续递归。
                """
                if code in downstream_visited:
                    return
                downstream_visited.add(code)

                in_cursor = records_coll.find(
                    {"qr_code": code, "op_type": "in", "is_delete": {"$ne": True}},
                    sort=[("op_time", -1)]
                )
                in_records = await in_cursor.to_list(length=10)
                if not in_records:
                    return

                wc_list = list(set(r["workorder_code"] for r in in_records if r.get("workorder_code")))
                out_cursor = records_coll.find(
                    {"workorder_code": {"$in": wc_list}, "op_type": "out", "is_delete": {"$ne": True}},
                    sort=[("op_time", -1)]
                )
                out_records = await out_cursor.to_list(length=20)
                if not out_records:
                    return

                out_records = dedup_by_proc_dev(out_records)

                for out in out_records:
                    await add_step(out)
                    out_qr = out.get("qr_code", "")
                    # if out_qr and out.get("material_type") in ("semi_finished_product", "finished_product"):
                    await trace_downstream(out_qr)

            # ---- 执行双向递归追溯 ----
            await trace_upstream(qr_code)
            await trace_downstream(qr_code)

            if not all_steps:
                self.send_response(Response.success([], "未找到相关产出记录"))
                return

            result = sorted(all_steps, key=lambda x: x.get("op_time", ""))

            # 批量查设备名称填充到步骤中
            await enrich_device_names(device_codes, result)
            # 批量查用户昵称替换操作人工号
            await enrich_user_names(operator_ids, result)

            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    # =====================================================================
    # 投入码查询
    # 输入投入码，找到该物料被用在哪些报工中，返回关联的产出码列表
    # =====================================================================

    @request_mapping('/trace/query_outputs_by_input', method='post', description='根据投入码查询关联的产出码')
    @swagger_doc(
        tags=["追溯查询"],
        summary="根据投入码查询关联的产出码",
        description="输入一个投入码，查询该码被用作投入的所有报工记录，返回对应的产出码列表",
        request_model=InputCodeQueryRequest,
    )
    @loginrequired
    async def query_outputs_by_input(self):
        """根据投入码查询关联的产出码，供用户选择后跳转到追溯页面"""
        try:
            # ---- 参数校验 ----
            if not self.data or 'input_code' not in self.data:
                self.send_response(Response.fail("请传入投入码 input_code"))
                return
            input_code = self.data['input_code'].strip()
            if not input_code:
                self.send_response(Response.fail("投入码不能为空"))
                return

            records_coll = await get_records_coll()

            # ---- 查询该投入码相关的所有记录 ----
            # 1. 该码被用作投入物料（op_type=in）的记录 — 最常见场景
            in_records = await records_coll.find(
                {"qr_code": input_code, "op_type": "in", "is_delete": {"$ne": True}},
                sort=[("op_time", -1)]
            ).to_list(length=100)
            # 2. 该码本身就是某个工序的产出（op_type=out） — 该码也可能是本产线生产的
            out_records = await records_coll.find(
                {"qr_code": input_code, "op_type": "out", "is_delete": {"$ne": True}},
                sort=[("op_time", -1)]
            ).to_list(length=100)
            if not in_records and not out_records:
                self.send_response(Response.success([], "未找到该投入码的关联记录"))
                return

            # ---- 构建(产出码, 工序, 设备)组合 ----
            # 一个投入码可能对应多个产出码（同一物料被用在多个工单中）
            combos = set()
            if in_records:
                in_wc = [r["workorder_code"] for r in in_records if r.get("workorder_code")]
                # 查这些工单的产出记录，获取关联的产出码
                async for out in records_coll.find(
                    {"workorder_code": {"$in": list(set(in_wc))}, "op_type": "out", "is_delete": {"$ne": True}}
                ):
                    if out.get("qr_code"):
                        combos.add((out["qr_code"], out.get("procedure_code", ""), out.get("device_code", "")))
            for out in out_records:
                # 该码本身是产出码的场景：直接使用投入码作为产出码
                combos.add((input_code, out.get("procedure_code", ""), out.get("device_code", "")))
            if not combos:
                self.send_response(Response.success([], "未找到该投入码关联的产出码"))
                return

            # ---- 批量查最新产出记录 ----
            # 一次查询替代每个组合一次 find_one（原 N+1 → 1）
            combo_latest = {}
            all_qrs = list(set(qr for qr, _, _ in combos))
            async for out in records_coll.find(
                {"qr_code": {"$in": all_qrs}, "op_type": "out", "is_delete": {"$ne": True}},
                sort=[("op_time", -1)]
            ):
                key = (out.get("qr_code", ""), out.get("procedure_code", ""), out.get("device_code", ""))
                if key in combos and key not in combo_latest:
                    combo_latest[key] = out
            if not combo_latest:
                self.send_response(Response.success([], "未找到该投入码关联的产出码"))
                return

            # ---- 有效性验证 ----
            # 确保最新工单中确实仍使用了该投入码
            # 避免出现"该码曾被用作投入但后续工单已变更"的脏数据
            latest_wc = set(o["workorder_code"] for o in combo_latest.values())
            valid_wc = {r["workorder_code"] async for r in records_coll.find(
                {"workorder_code": {"$in": list(latest_wc)}, "op_type": "in",
                 "qr_code": input_code, "is_delete": {"$ne": True}}
            )}

            # ---- 批量查工序名称 ----
            process_coll = await get_process_coll()
            proc_codes = set(p for _, p, _ in combo_latest if p)
            proc_name_map = {}
            if proc_codes:
                async for p in process_coll.find(
                    {"工序编码": {"$in": list(proc_codes)}}, projection={"工序编码": 1, "工序名称": 1}
                ):
                    proc_name_map[p["工序编码"]] = p.get("工序名称", "")

            # ---- 组装结果 ----
            result = []
            for (qr, proc_code, dev_code), out in combo_latest.items():
                # 如果产出码不是该投入码本身，需要验证有效性
                if qr != input_code and out["workorder_code"] not in valid_wc:
                    continue
                result.append({
                    "qr_code": qr,
                    "material_code": out.get("material_code", ""),
                    "material_type": out.get("material_type", ""),
                    "procedure_code": proc_code,
                    "procedure_name": proc_name_map.get(proc_code, ""),
                    "op_time": str(out.get("op_time", "")),
                    "workorder_code": out.get("workorder_code", ""),
                })

            result.sort(key=lambda x: x.get("op_time", ""))

            if not result:
                self.send_response(Response.success([], "未找到该投入码关联的产出码"))
                return
            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    # =====================================================================
    # 提交记录查询
    # 同一个(产出码+工序+设备)可能有多次报工（返工/复投），查看完整提交历史
    # =====================================================================

    @request_mapping('/trace/query_submission_records', method='post', description='根据产出码+工序+设备查询提交记录')
    @swagger_doc(
        tags=["追溯查询"],
        summary="查询提交记录",
        description="输入 qr_code + procedure_code + device_code，查询同工序同设备的所有提交记录",
        request_model=SubmissionRecordRequest,
    )
    @loginrequired
    async def query_submission_records(self):
        """查询提交记录 — 同产出码+工序+设备下的所有历史报工"""
        try:
            if not self.data:
                self.send_response(Response.fail('参数不能为空'))
                return
            qr_code = self.data.get('qr_code', '').strip()
            procedure_code = self.data.get('procedure_code', '').strip()
            device_code = self.data.get('device_code', '').strip()
            if not qr_code or not procedure_code:
                self.send_response(Response.fail('产出码和工序编码不能为空'))
                return

            records_coll = await get_records_coll()
            records_cursor = records_coll.find(
                {'qr_code': qr_code, 'procedure_code': procedure_code, 'device_code': device_code,
                 'op_type': 'out', 'is_delete': {'$ne': True}},
                sort=[('op_time', -1)]
            )
            records = await records_cursor.to_list(length=100)
            if not records:
                self.send_response(Response.success([], '未找到提交记录'))
                return

            result = []
            operator_ids = set()
            for r in records:
                # 转换检测结果（一次合格/返工合格/复投合格）
                check_result = calc_check_result(
                    r.get('check_result', ''),
                    r.get('production_model', ''),
                )

                op_id = r.get('operator', '') or ''
                if op_id:
                    operator_ids.add(op_id)

                result.append({
                    'workorder_code': r.get('workorder_code', ''),
                    'op_time': str(r.get('op_time', '')),
                    'operator': op_id,
                    'check_result': check_result,
                    'production_model': r.get('production_model', ''),
                })

            # 批量查询用户昵称替换操作人工号
            await enrich_user_names(operator_ids, result)

            self.send_response(Response.success(result, '查询成功'))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail('查询失败，服务器内部错误'))

    # =====================================================================
    # 工艺参数查询
    # 根据工单编码查 gycs_data 表，获取该次报工对应的设备工艺参数采集数据
    # =====================================================================

    @request_mapping('/trace/query_process_params', method='post', description='根据工单编码查询工艺参数')
    @swagger_doc(
        tags=["追溯查询"],
        summary="查询工艺参数",
        description="输入 workorder_code，查询该工单对应的工艺参数数据",
        request_model=ProcessParamRequest,
    )
    @loginrequired
    async def query_process_params(self):
        """查询工艺参数 — 工单对应的设备工艺参数采集数据"""
        try:
            if not self.data or 'workorder_code' not in self.data:
                self.send_response(Response.fail("请传入工单编码 workorder_code"))
                return
            workorder_code = self.data['workorder_code'].strip()
            if not workorder_code:
                self.send_response(Response.fail("工单编码不能为空"))
                return

            gycs_coll = await get_gycs_coll()
            records = await gycs_coll.find(
                {"qr_workorder_code": workorder_code},
                sort=[("timestamp", -1)]
            ).to_list(length=20)
            if not records:
                self.send_response(Response.success([], "未找到工艺参数数据"))
                return

            # 收集所有 (device_code, procedure_code) 对，批量查询工艺参数配置
            config_pairs = set()
            for r in records:
                dc = r.get("device_code", "")
                pc = r.get("procedure_code", "")
                if dc and pc:
                    config_pairs.add((dc, pc))

            # 查询 process_params_config，构建 device+procedure -> param_desc_map
            config_coll = await get_process_params_config_coll()
            desc_map_cache = {}  # key: f"{device_code}|{procedure_code}"
            if config_pairs and config_coll is not None:
                for dc, pc in config_pairs:
                    config = await config_coll.find_one(
                        {"device_code": dc, "process_code": pc},
                        projection={"params": 1}
                    )
                    if config and config.get("params"):
                        desc_map = {}
                        for p in config["params"]:
                            if p.get("param_key"):
                                desc_map[p["param_key"]] = p.get("param_desc", "")
                        if desc_map:
                            desc_map_cache[f"{dc}|{pc}"] = desc_map

            result = []
            for r in records:
                params_data = r.get("data", {})
                if not isinstance(params_data, dict):
                    params_data = {}
                device_code = r.get("device_code", "")
                procedure_code = r.get("procedure_code", "")
                # 从缓存中获取该设备+工序的参数描述映射
                cache_key = f"{device_code}|{procedure_code}"
                param_descs = desc_map_cache.get(cache_key, {})
                result.append({
                    "data_type": r.get("data_type", ""),
                    "params": params_data,
                    "param_descs": param_descs,
                    "device_code": device_code,
                    "device_name": r.get("device_name", ""),
                    "procedure_name": r.get("procedure_name", ""),
                    "timestamp": str(r.get("timestamp", "")),
                })

            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    # =====================================================================
    # 检验单查询
    # 根据工单编码查 {org}_manual_trace.inspection_records 表，获取该次报工
    # 关联的检验单（由 manual_line_general_traceability 报工时落库）
    # =====================================================================

    @request_mapping('/trace/query_inspection_record', method='post', description='根据工单编码查询检验单')
    @swagger_doc(
        tags=["追溯查询"],
        summary="查询检验单",
        description="输入 workorder_code，查询该次报工关联的检验单记录",
        request_model=InspectionRecordRequest,
    )
    @loginrequired
    async def query_inspection_record(self):
        """查询检验单 — 该次报工关联的检验单记录"""
        try:
            if not self.data or 'workorder_code' not in self.data:
                self.send_response(Response.fail("请传入工单编码 workorder_code"))
                return
            workorder_code = self.data['workorder_code'].strip()
            if not workorder_code:
                self.send_response(Response.fail("工单编码不能为空"))
                return

            inspection_coll = await get_inspection_records_coll()
            record = await inspection_coll.find_one(
                {"workorder_code": workorder_code, "is_delete": {"$ne": True}},
                sort=[("op_time", -1)]
            )
            if not record:
                self.send_response(Response.success(None, "该报工无检验单记录"))
                return

            result = {
                "workorder_code": record.get("workorder_code", ""),
                "raw_workorder_code": record.get("raw_workorder_code", ""),
                "product_code": record.get("product_code", ""),
                "routing_code": record.get("routing_code", ""),
                "process_code": record.get("process_code", ""),
                "process_name": record.get("process_name", ""),
                "produce_unit_code": record.get("produce_unit_code", ""),
                "device_code": record.get("device_code", ""),
                "items": record.get("items", []),
                "is_qualified": record.get("is_qualified", False),
                "operator": record.get("operator", ""),
                "op_time": str(record.get("op_time", "")),
                "created_at": str(record.get("created_at", "")),
            }

            # 操作人工号转昵称
            operator = result.get("operator", "") or ""
            if operator:
                await enrich_user_names({operator}, [result])

            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))

    # =====================================================================
    # 投入记录查询（弹窗用）
    # 一次报工 = 1 条产出(out) + N 条投入(in)。返回某次报工的所有投入物料。
    # 特殊处理换码场景：产出码不在投入列表中时追加一条产出码。
    # =====================================================================

    @request_mapping('/trace/query_inputs', method='post', description='根据工单编码查询投入记录')
    @swagger_doc(
        tags=["追溯查询"],
        summary="根据工单编码查询投入记录",
        description="输入 workorder_code，查询该次报工的所有投入物料记录",
        request_model=TraceDetailRequest,
        response_model=TraceDetailResponse
    )
    @loginrequired
    async def query_inputs(self):
        """查询投入记录 — 某次报工的投入物料明细，支持换码场景"""
        try:
            if not self.data or 'workorder_code' not in self.data:
                self.send_response(Response.fail("请传入工单编码 workorder_code"))
                return
            workorder_code = self.data['workorder_code'].strip()
            if not workorder_code:
                self.send_response(Response.fail("工单编码不能为空"))
                return

            records_coll = await get_records_coll()

            in_records = await records_coll.find(
                {"workorder_code": workorder_code, "op_type": "in", "is_delete": {"$ne": True}},
                sort=[("code_index", 1)]
            ).to_list(length=100)

            out_record = await records_coll.find_one(
                {"workorder_code": workorder_code, "op_type": "out", "is_delete": {"$ne": True}}
            )

            in_qr_codes = set()
            result = []
            for r in in_records:
                qr = r.get("qr_code", "") or ""
                if qr:
                    in_qr_codes.add(qr)
                result.append({
                    "material_code": r.get("material_code", ""),
                    "material_type": r.get("material_type", ""),
                    "qr_code": qr,
                    "op_time": str(r.get("op_time", "")),
                    "code_index": r.get("code_index", 0),
                    "require_num": r.get("require_num", 1),
                })

            # 换码场景：产出码不在投入列表中时也加入，方便用户继续追溯
            if out_record:
                out_qr = out_record.get("qr_code", "")
                if out_qr and out_qr not in in_qr_codes:
                    result.append({
                        "material_code": out_record.get("material_code", ""),
                        "material_type": out_record.get("material_type", ""),
                        "qr_code": out_qr,
                        "op_time": str(out_record.get("op_time", "")),
                        "code_index": -1,
                        "require_num": 1,
                    })

            self.send_response(Response.success(result, "查询成功"))

        except Exception:
            get_logger().error(traceback.format_exc())
            self.send_response(Response.fail("查询失败，服务器内部错误"))
