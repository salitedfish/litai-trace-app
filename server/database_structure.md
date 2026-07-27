# MES 追溯应用 — MongoDB 数据库结构文档

> 最后更新：2026-07-27（新增 dashboard_config_1 + 文档更新）

---

## 数据库概览

| 属性 | 说明 |
|------|------|
| **数据库名称** | `manugence_root`、`{}_config`、`{}_order_retrospect`、`{}_workorder`、`{}_scan_code_data`、`idi_{}`、`idi_{}_cloud_management`、`{}_manual_trace`、`{}_trace_app`（`{}` 为组织代码） |
| **MongoDB 地址** |  |

---

## 集合清单

### 1. `manugence_root` 数据库

#### 1.1 `users` — 用户表

**用途：** 存储系统用户信息，包括账号、密码、角色、所属组织、部门和班次等。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a48baba32b50d766262b4da` |
| `work_id` | string | 工号（登录账号） | `9988` |
| `user_name` | string | 用户名 | `9988` |
| `user_password` | string | 密码（MD5 加密） | `f16bdb8078f9392c4394dc93a856432e` |
| `user_role` | string | 角色（`admin`=管理员/`operator`=操作工等） | `admin` |
| `organization` | string | 所属组织编码 | `buXiuGang` |
| `user_nickname` | string | 用户昵称/真实姓名 | `戴显雷` |
| `user_detail` | string | 用户详情 | `""` |
| `create_time` | datetime | 创建时间 | `2026-07-04 15:48:10` |
| `last_login_time` | datetime | 最后登录时间 | `2026-07-15 08:46:34` |
| `identity` | string | 身份/岗位，格式为 `{产线}/{职位}` | `,卡特产线/组长` |
| `card_id` | string | 刷卡 ID（刷卡登录用） | `""` |
| `departments` | array[string] | 所属部门列表 | `["other"]` |
| `team` | object | 班次配置，key 为岗位，value 为班次名称 | `{"卡特产线/组长": "早班"}` |

---

### 2. `{}_config` 数据库

#### 2.1 `bom_record` — BOM & 工艺路线记录

**用途：** 存储产品的 BOM（物料清单）、工艺路线、工序定义等信息，描述在某个工艺路线的某道工序中，投入什么物料、产出什么物料。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a48b26ad52304405887cea2` |
| `routing_name` | string | 工艺路线名称 | `330607-01卡特产线` |
| `routing_code` | string | 工艺路线编号 | `330607-01` |
| `process_name` | string | 工序名称 | `零件清洗` |
| `process_code` | string | 工序编号 | `GX0020` |
| `section_name` | string | 工段名称 | `零件清洗` |
| `section_code` | string | 工段编号 | `0020` |
| `output_material_name` | string | 产出物料名称 | `中冷器` |
| `output_material_code` | string | 产出物料编号 | `330607-01` |
| `is_virtual` | boolean | 是否虚拟件 | `false` |
| `input_material_name` | string | 投入物料名称 | `中冷器` |
| `input_material_code` | string | 投入物料编号 | `330607-01` |
| `item_amount` | number | 物料数量 | `1` |
| `check_process` | string | 是否检验工序（是/否） | `否` |
| `bom_version` | string | BOM 版本号 | `1.0` |

#### 2.2 `production_config_mgm_material_info` — 物料信息

**用途：** 存储物料主数据，包括物料编码、名称、类型、分类及所属车间等基础信息。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a48a817d52304405887ce47` |
| `车间` | array[string] | 所属车间列表 | `["卡特产线"]` |
| `物料编码` | string | 物料编码（唯一标识） | `660001-90` |
| `物料名称` | string | 物料名称 | `水道盖板` |
| `规格` | string | 规格型号 | `""` |
| `物料类型` | string | 物料类型（外购件/自制件/虚拟件等） | `外购件` |
| `物料分类` | string | 物料分类（原材料/半成品/成品等） | `原材料` |
| `条码类型` | string | 条码类型（批次码/序列码等） | `批次码` |

#### 2.3 `production_config_mgm_process_info` — 工序信息

**用途：** 存储工序基础信息，包括工序编码、名称及所属的工作中心和生产单元。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a4868f7d52304405887cd10` |
| `工序编码` | string | 工序编码（唯一标识） | `GX0020` |
| `工序名称` | string | 工序名称 | `零件清洗` |
| `工作中心编码` | string | 工作中心编码 | `1` |
| `工作中心名称` | number/string | 工作中心名称 | `1` |
| `生产单元编码` | string | 生产单元编码 | `202607C0001` |

#### 2.4 `production_config_mgm_record` — 物料-工艺路线配置

**用途：** 物料与工艺路线的关联配置表，指定某个物料使用哪条工艺路线进行生产。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a4370c1d52304405887ccb6` |
| `material_code` | string | 物料编码 | `ccp01` |
| `material_name` | string | 物料名称 | `产成品01` |
| `routing_code` | string | 工艺路线编号 | `ccp01gylx` |
| `routing_name` | string | 工艺路线名称 | `产成品01工艺路线` |

**关联关系：**
- `material_code` → `production_config_mgm_material_info.物料编码`（多对一）
- `routing_code` → `production_config_mgm_routing_process_info.工艺路线编码`（一对多 → 该路线的所有工序步骤）

> **说明：** 数据库中无独立的工艺路线主表。工艺路线的主信息（名称、类型、车间）由 `production_config_mgm_routing_process_info` 的明细记录冗余存储，同一工艺路线的多条明细记录重复填写相同的路线名称、类型、车间字段。

#### 2.5 `production_config_mgm_routing_process_info` — 工艺路线明细（兼主表）

**用途：** 工艺路线的明细表，每条记录定义该工艺路线中的一个工序步骤（包括工序顺序、所属工作中心等）。一个工艺路线包含多条明细记录。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a436d54d52304405887ccac` |
| `工艺路线类型` | string | 工艺路线类型（主工艺路线/返工工艺路线等） | `主工艺路线` |
| `工艺路线编码` | string | 所属工艺路线编号 | `ccp01gylx` |
| `工艺路线名称` | string | 所属工艺路线名称 | `产成品01工艺路线` |
| `车间编码` | string | 车间编码 | `buXiuGangCheJian` |
| `车间名称` | string | 车间名称 | `不锈钢车间` |
| `工序号` | string | 工序号（标识） | `1001` |
| `工作中心编码` | string | 工作中心编码 | `1001` |
| `工作中心名称` | string | 工作中心名称 | `产成品01工作中心01` |
| `工序顺序` | number | 工序顺序号（决定先后顺序） | `1` |
| `工序编码` | string | 工序编码 | `ccp01gx01` |
| `工序名称` | string | 工序名称 | `产成品01工序01` |

**关联关系：**
- `工艺路线编码` → `production_config_mgm_record.routing_code`（多对一）
- `工序编码` → `production_config_mgm_process_info.工序编码`（多对一）

---

---

### 3. `{}_order_retrospect` 数据库

#### 3.1 `work_order_retrospect_records` — 报工记录

**用途：** 记录生产报工数据，包括物料流转（投入/产出）、扫码信息、工序执行情况等。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a558d91bf3f9eed0498461c` |
| `workorder_code` | string | 工单编码（含时间戳的完整唯一码） | `202607C0015_202607140740_20260714091457983` |
| `raw_workorder_code` | string | 原始工单编码（不含时间戳后缀） | `202607C0015_202607140740` |
| `op_type` | string | 操作类型（`in`=投入/`out`=产出） | `out` |
| `material_code` | string | 物料编码 | `330607-01` |
| `material_info` | string | 物料完整信息（编码~二维码/批次信息） | `330607-01~330607-01-01*6672562*26070400001` |
| `material_type` | string | 物料类型（`raw_material`=原材料/`semi_finished_product`=半成品/`finished_product`=成品） | `semi_finished_product` |
| `qr_code` | string | 二维码/条码内容 | `330607-01-01*6672562*26070400001` |
| `code_type` | string | 条码类型（`single_code`=单件码/`batch_code`=批次码） | `single_code` |
| `produce_unit_code` | string | 生产单元编码 | `202607C0015` |
| `process_section` | string | 工序段编码 | `0120` |
| `procedure_code` | string | 工序编码 | `GX0120` |
| `device_code` | string | 设备编码 | `dev_zj_001` |
| `check_result` | string | 检验结果（空字符串表示未检验/合格） | `""` |
| `production_model` | string | 生产模式（`normal`=正常/`rework`=返工/`resubmission`=复投） | `normal` |
| `op_time` | string/datetime | 操作时间 | `2026-07-14 09:14:57.983` |
| `code_index` | number | 条码序号/索引 | `0` |
| `production_type` | string | 生产类型（暂未使用） | `""` |
| `require_num` | number | 需求数量 | `1` |
| `is_delete` | boolean | 是否删除（逻辑删除标记） | `false` |
| `operator` | string | 操作人工号 | `9988` |

**关联关系：**
- `material_code` → `{}_config.production_config_mgm_material_info.物料编码`
- `procedure_code` → `{}_config.production_config_mgm_process_info.工序编码`
- `produce_unit_code` → `{}_config.production_config_mgm_routing_process_info.生产单元编码`
- `workorder_code` → `{}_traceback.gycs_data.qr_workorder_code`（一对一，用于查询工艺参数）

**业务逻辑说明：**

1. **报工粒度：** 相同 `workorder_code` 的所有记录构成一次完整的报工操作。
2. **投入多条/产出一条：** 每次报工有一条或多条 `op_type: "in"`（投入）记录（例如投入多个物料），且必须有且仅有一条 `op_type: "out"`（产出）记录。
3. **非改变主体码的报工：** 当操作不改变物料主体码时，`out` 记录会与其中一条 `in` 记录的主体码信息一致（即 `material_info`/`qr_code` 相同），相当于该投入物料就是产出物料本身。
4. **改变主体码的报工：** 当操作改变了物料主体码时（如组装、拆分、形态转换），`in` 记录的物料信息不同于 `out` 记录，此时不存在与 `out` 相同内容的 `in` 记录。

---

---

### 4. `{}_workorder` 数据库

#### 4.1 `workorder_record` — 工单记录

**用途：** 存储工单主数据，包括工单基本信息、BOM 物料清单（各工序的投入/产出物料及定额）、生产单元配置、计划数量、工单状态等。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a48b4a044713ff963bfa6f3` |
| `workorder_code` | string | 工单编码（唯一标识） | `G202607040001` |
| `assembly_part_info` | array | 装配部件信息 | `[]` |
| `bom_info` | object | BOM 信息，key 为工序段编码 | 见下方子表 |
| `close_automatically` | boolean | 是否自动关闭 | `true` |
| `complete_reason` | string/null | 完成原因 | `null` |
| `deadline` | string | 截止日期 | `2026-07-04` |
| `defective_id` | string | 不良品 ID | `""` |
| `important_order` | boolean | 是否重要工单 | `false` |
| `is_child_workorder` | boolean | 是否子工单 | `false` |
| `is_origin` | boolean | 是否原始工单 | `false` |
| `is_parent_workorder` | boolean | 是否父工单 | `false` |
| `is_reference_workorder` | boolean | 是否参考工单 | `false` |
| `is_rework_workorder` | boolean | 是否返工工单 | `false` |
| `last_procedure_code` | string | 上一工序编码 | `""` |
| `mould_preparation` | array | 模具准备信息 | `[]` |
| `need_reference_workorder` | boolean | 是否需要参考工单 | `false` |
| `need_track` | boolean | 是否需要追踪 | `false` |
| `next_check_trigger_value` | object | 下次检查触发值 | `{}` |
| `one_pass_amount` | number | 一次性通过数量 | `0` |
| `order_id` | string | 订单 ID | `202607040001` |
| `origin_order_code` | string | 原始订单编码 | `G202607040001` |
| `plan_quality_list` | array[object] | 计划质量列表（按日计划） | 见下方子表 |
| `planned_quantity` | number | 计划数量 | `5` |
| `planned_rlj` | string | 计划热料（预留字段） | `""` |
| `procedure_code` | string | 当前工序编码 | `GX0020` |
| `procedure_name` | string | 当前工序名称 | `零件清洗` |
| `product_code` | string | 产品编码 | `330607-01` |
| `product_name` | string | 产品名称 | `中冷器` |
| `production_cell` | object | 生产单元配置（含设备列表） | 见下方子表 |
| `reference_part_complete` | boolean | 参考部件是否完成 | `false` |
| `route_code` | string | 工艺路线编码 | `330607-01` |
| `section_code` | string | 工段编码 | `202607C0001` |
| `section_name` | string | 工段名称 | `202607C0001` |
| `section_seq` | number | 工段顺序号 | `1` |
| `shift` | string | 班次 | `早班` |
| `specification_model` | string | 规格型号 | `""` |
| `sub_produce_unit_code` | string | 子生产单元编码 | `""` |
| `sub_produce_unit_name` | string | 子生产单元名称 | `""` |
| `task_type` | string | 任务类型（`zizhi_zuzhuang`=自制组装等） | `zizhi_zuzhuang` |
| `tbd_amount` | number | 待定数量 | `0` |
| `to_be_check` | boolean | 是否需要检验 | `false` |
| `unit_seq` | number | 单元顺序号 | `1` |
| `working_time` | number | 工作时间（秒/分钟） | `0` |
| `workorder_seq` | number | 工单顺序号 | `1` |
| `workorder_status` | string | 工单状态（`pending`=待生产/`processing`=生产中/`complete`=已完成/`closed`=已关闭） | `complete` |
| `workorder_to_show` | string | 显示用工单号 | `G202607040001` |
| `workshop_code` | string | 车间编码 | `202607L0001` |
| `workshop_name` | string | 车间名称 | `卡特产线` |
| `complete_time` | datetime | 完成时间 | `2026-07-05T08:00:00.102Z` |

**`bom_info` 子结构（key 为工序段编码的对象）：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `product_in` | array[object] | 投入物料清单 | 见下方子表 |
| `product_out` | array[object] | 产出物料清单 | 见下方子表 |

**`product_in` / `product_out` 数组元素结构：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `material_code` | string | 物料编码 | `330607-01` |
| `material_name` | string | 物料名称 | `中冷器` |
| `material_quota` | number | 物料定额数量 | `1` |
| `material_type` | string | 物料类型（`raw_material`=原材料/`semi_finished_product`=半成品/`finished_product`=成品） | `semi_finished_product` |
| `code_type` | string | 条码类型（`single_code`=单件码/`batch_code`=批次码） | `single_code` |
| `is_check_miss_process` | boolean | 是否检查漏工序（仅 `product_in` 有） | `false` |

**`plan_quality_list` 数组元素结构：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `plan_quality_of_day` | string | 计划日期 | `2026-07-04` |
| `quantity` | number | 计划数量 | `5` |

**`production_cell` 对象结构：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `produce_unit_name` | string | 生产单元名称 | `零件清洗` |
| `produce_unit_code` | string | 生产单元编码 | `202607C0001` |
| `beat` | number | 节拍（秒/分钟） | `5` |
| `device_list` | array[object] | 设备列表 | 见下方子表 |

**`device_list` 数组元素结构：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `device_name` | string | 设备名称 | `超声波清洗机` |
| `device_code` | string | 设备编码 | `dev_csbqxj_001` |

**关联关系：**
- `product_code` → `{}_config.production_config_mgm_material_info.物料编码`
- `procedure_code` → `{}_config.production_config_mgm_process_info.工序编码`
- `route_code` → `{}_config.production_config_mgm_record.routing_code`
- `production_cell.produce_unit_code` → `{}_config.production_config_mgm_routing_process_info.生产单元编码`
- `bom_info.*.product_in[].material_code` → `{}_config.production_config_mgm_material_info.物料编码`（多对多）
- `workorder_code` → `{}_order_retrospect.work_order_retrospect_records.raw_workorder_code`（一对多，报工记录通过原始工单号关联）

---

---

### 5. `{}_scan_code_data` 数据库

#### 5.1 `scan_code_rules` — 条码解析规则

**用途：** 定义物料条码的解析规则，配置条码各段位的含义（物料编码、批次号、流水号等），支持批次码和单件码两种条码类型。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a4314a2216973ec7b276260` |
| `workshop_name` | string | 车间名称（筛选条件，空表示通用） | `""` |
| `workshop_code` | string | 车间编码（筛选条件，空表示通用） | `""` |
| `remark` | string | 备注 | `""` |
| `material_code_in` | string | 投入物料编码筛选 | `""` |
| `material_name_in` | string | 投入物料名称筛选 | `""` |
| `material_code_out` | string | 产出物料编码筛选 | `""` |
| `material_name_out` | string | 产出物料名称筛选 | `""` |
| `code_type` | string | 条码类型（`batch_code`=批次码/`single_code`=单件码） | `batch_code` |
| `qr_code_len` | number | 条码总长度（0 表示不限制） | `0` |
| `creator` | string | 创建人 | `root` |
| `comma_quantity` | number | 分隔段数量（按分隔符拆分的段数） | `6` |
| `batch_rules` | array[object] | 批次码解析规则（各段位含义配置） | 见下方子表 |
| `single_rules` | array[object] | 单件码解析规则（可为 null） | `null` |
| `create_time` | datetime | 创建时间 | `2026-06-30 08:58:10.978` |
| `update_time` | datetime | 更新时间 | `2026-06-30 08:58:10.978` |
| `is_delete` | boolean | 是否逻辑删除 | `false` |
| `count_control` | boolean | 是否启用数量控制 | `false` |

**`batch_rules` 子结构（数组元素）：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `material_code` | number | 物料编码所在段位（从 1 开始） | `1` |
| `batch_number` | number | 批次号所在段位 | `2` |
| `batch_count` | number | 批次数量所在段位 | `6` |

**`single_rules` 子结构（数组元素，可为 null）：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `begin` | number | 起始位置（从 1 开始） | `1` |
| `end` | number | 结束位置 | `3` |
| `value` | string | 该段位的含义/标识 | `ycl` |

---

---

### 6. `idi_{}` 数据库

#### 6.1 `datas` — 数采数据

**用途：** 存储设备数据采集（数采）的实时信号数据，记录设备各信号点的最新值及时间戳。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a5715b3c8cb2a477467ddf2` |
| `code` | string | 信号编码，格式为 `{设备编码}~{信号类型}` | `dev_csbqxj_001~p_kgj_wg` |
| `value` | string | 信号值 | `0` |
| `timestamp` | datetime | 数据采集时间戳 | `2026-07-15T13:08:03.000Z` |

**说明：**
- `code` 字段由 `~` 分隔为两部分：前半段为**设备编码**，后半段为**信号类型**（如 `p_kgj_wg` 表示某个传感器信号）
- 该表为设备数采的实时数据存储，通常每条记录代表一个设备的一个信号点在某个时刻的数值

---

---

### 7. `idi_{}_cloud_management` 数据库

#### 7.1 `folder` — 工厂/产线层级

**用途：** 配置数采系统时使用的工厂与产线层级结构表，以树形结构组织各层级节点（工厂→车间→产线等）。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a56e9c044713ff96333ff08` |
| `code` | string | 节点编码（唯一标识） | `202607L0001` |
| `index` | number | 排序索引 | `1` |
| `name` | string | 节点名称 | `卡特产线` |
| `parent_code` | string | 父节点编码（根节点为空或 `0`） | `1108.0` |
| `type` | string | 节点类型（`folder`=文件夹/层级节点，也可能是 `device` 等） | `folder` |

**说明：**
- `parent_code` 指向父节点的 `code`，形成树形层级结构
- `type` 为 `folder` 时表示分组/层级节点（工厂、车间、产线等）
- `code` 被 `gateway.level_code` 引用

#### 7.2 `gateway` — 网关配置

**用途：** 存储 IoT 网关的配置信息，包括通信方式、采集时间、所属层级、IP 地址等。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a56fa8844713ff9633493bc` |
| `code` | string | 网关编码（唯一标识） | `iot_cat_gx0020` |
| `collect_time` | array[array[string]] | 数据采集时间段 | `[["00:00", "23:59"]]` |
| `gateway_type` | string | 网关类型（如 `R` 表示某种类型） | `R` |
| `index` | number | 排序索引 | `0` |
| `level_code` | string | 所属层级编码，对应 `folder.code` | `202607L0001` |
| `method` | string | 通信方式（`mqtt`/`modbus` 等） | `mqtt` |
| `monitoring` | boolean | 是否启用监控 | `true` |
| `name` | string | 网关名称 | `零件清洗` |
| `type` | string | 类型标识（固定为 `gateway`） | `gateway` |
| `ip` | string | IP 地址信息（含多网卡详情） | `以太网 ip:192.168.101.115; ...` |

**关联关系：**
- `level_code` → `folder.code`（多对一，网关所属的产线/层级）

#### 7.3 `device` — 设备配置

**用途：** 存储 IoT 设备信息及配置，包括通信参数、驱动类型、点位列表等。一个网关下挂多个设备。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a56e9c044713ff96333ff0c` |
| `code` | string | 设备编码（唯一标识） | `dev_csbqxj_001` |
| `name` | string | 设备名称 | `超声波清洗机` |
| `type` | string | 类型标识（固定为 `device`） | `device` |
| `gateway_code` | string | 所属网关编码 | `iot_cat_gx0020` |
| `driver_type` | string | 驱动类型（如 `iot_driver_melsecmc`=三菱 MC 协议） | `iot_driver_melsecmc` |
| `index` | number | 排序索引 | `0` |
| `monitoring` | boolean | 是否启用监控 | `true` |
| `collect_switch` | boolean | 采集开关 | `true` |
| `reconnect` | number | 重连次数/策略 | `1` |
| `status` | string | 设备状态（`normal`=正常/`abnormal`=异常/`offline`=离线） | `abnormal` |
| `threshold` | null/object | 阈值配置 | `null` |
| `param` | object | 通信参数（IP、端口、协议类型等） | 见下方示例 |
| `children` | array[object] | 点位列表 | 见下方子表 |
| `children_length` | number | 点位数量（冗余字段） | `0` |

**`param` 对象字段：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `iotm_melsecmc_material_interface` | string | 通信接口类型 | `tcp` |
| `iotm_port` | number | 端口号 | `4995` |
| `iotm_type` | string | 协议类型 | `mc(binary)` |
| `iotm_ip` | string | IP 地址 | `192.168.1.105` |

**`children` 子结构（点位）：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `code` | string | 信号点编码 | `p_dianliu` |
| `name` | string | 信号点名称 | `超声波电流` |
| `value` | string | 当前值（采集后更新） | `""` |
| `status` | string | 信号点状态 | `""` |
| `timestamp` | string | 最后更新时间 | `""` |
| `description` | string | 描述 | `""` |
| `addr` | string | 寄存器地址 | `ignore` |
| `data_type` | string | 数据类型（`int16`/`float`/`bool` 等） | `int16` |
| `len` | number | 数据长度 | `1` |
| `collect_circle` | number | 采集周期（秒） | `8` |
| `report_circle` | number | 上报周期（秒） | `8` |
| `report_type` | string | 上报类型 | `3` |
| `report_code` | null | 上报编码 | `null` |
| `group` | string | 分组标识 | `g_default` |
| `order_num` | string | 排序号 | `""` |
| `threshold` | null/object | 阈值配置 | `null` |
| `target` | null/object | 目标值配置 | `null` |
| `monitoring` | boolean | 是否监控 | `true` |
| `param` | object | 扩展参数 | `{}` |

**关联关系：**
- `gateway_code` → `gateway.code`（多对一，设备所属网关）
- `children[].code` 与 `idi_{}.datas.code` 关联：点位编码作为 `datas.code` 的 `~` 后半段，完整格式为 `{device_code}~{children_code}`

---

---

### 8. `{}_traceback` 数据库

#### 8.1 `gycs_data` — 工艺参数数据

**用途：** 存储生产过程中的工艺参数采集数据，记录各设备的工艺参数值、检测结果等。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a55904cbb4651c9bd7ba7ff` |
| `data_type` | string | 数据类型标识 | `p_process_para` |
| `data` | object | 工艺参数键值对，字段不固定，根据实际采集项动态生成 | `{"zpjg": "合格", "dianliu": 2, "ldspeed": 50, ...}` |
| `data_limit` | object | 参数阈值/上限配置（可为空） | `{}` |
| `value_id` | string | 二维码/追溯码（关联的物料标识） | `330607-01-01*6672562*26070400001` |
| `device_code` | string | 设备编码 | `dev_csbqxj_001` |
| `device_name` | string | 设备名称 | `超声波清洗机` |
| `produce_unit_code` | string | 生产单元编码 | `202607C0001` |
| `produce_unit_name` | string | 生产单元名称 | `零件清洗` |
| `procedure_code` | string | 工序编码 | `GX0020` |
| `procedure_name` | string | 工序名称 | `零件清洗` |
| `timestamp` | datetime | 数据采集时间 | `2026-07-14T09:26:36.794+00:00` |
| `code` | string | 设备编码（冗余） | `dev_csbqxj_001` |
| `workorder_code` | string | 工单编码（不含时间戳后缀） | `202607C0001_202607140740` |
| `qr_workorder_code` | string | 完整工单编码（含时间戳后缀） | `202607C0001_202607140740_20260714092636794` |

**`data` 子字段（示例值，实际字段不固定）：**

> `data` 内的字段由设备采集项决定，不同设备/工序的工艺参数不同。以下仅为示例，实际字段名和数量视现场配置而定。

| 字段 | 类型 | 示例值 |
|------|------|--------|
| `zpjg` | string | `合格` |
| `result` | string | `OK` |
| `dianliu` | number | `2` |
| `ldspeed` | number | `50` |
| `hgwendu1` | number | `120` |
| `hgwendu2` | number | `130` |
| `hgwendu3` | number | `130` |
| `dhwendu` | number | `50` |
| `cao1` | number | `8` |
| `cao2` | number | `9` |

**关联关系：**
- `value_id` → `{}_order_retrospect.work_order_retrospect_records.qr_code`（多对一）
- `device_code` → `idi_{}_cloud_management.device.code`（多对一）
- `procedure_code` → `{}_config.production_config_mgm_process_info.工序编码`
- `workorder_code` → `{}_order_retrospect.work_order_retrospect_records.raw_workorder_code`
- `qr_workorder_code` → `{}_order_retrospect.work_order_retrospect_records.workorder_code`（一对一，追溯页面的产出记录通过此关联查询工艺参数）

---

---

### 9. `{}_manual_trace` 数据库

#### 9.1 `process_params_config` — 工艺参数配置

**用途：** 存储各工序/设备对应的工艺参数键值定义，描述在某条工艺路线的某道工序中，需要采集哪些工艺参数及其类型。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a5717b4bb4651c9bd7ba800` |
| `id` | string | ID（预留字段） | `""` |
| `process_route_code` | string | 工艺路线编码 | `330607-01` |
| `process_route_name` | string | 工艺路线名称 | `330607-01卡特产线` |
| `product_code` | string | 产品编码 | `330607-01` |
| `product_name` | string | 产品名称 | `中冷器` |
| `process_code` | string | 工序编码 | `GX0130` |
| `process_name` | string | 工序名称 | `打标` |
| `device_code` | string | 设备编码 | `dev_db_001` |
| `device_name` | string | 设备名称 | `激光打标机` |
| `params` | array[object] | 工艺参数定义列表 | 见下方子表 |
| `created_at` | datetime | 创建时间 | `2026-07-15T13:16:36.110Z` |
| `updated_at` | datetime | 更新时间 | `2026-07-15T13:16:36.110Z` |

**`params` 数组元素结构：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `param_key` | string | 参数键名（英文标识） | `zpjg` |
| `param_desc` | string | 参数描述/中文名 | `装配结果` |
| `param_type` | string | 参数类型（`string`/`number`/`boolean` 等） | `string` |

**关联关系：**
- `process_route_code` → `{}_config.production_config_mgm_record.routing_code`（多对一）
- `process_code` → `{}_config.production_config_mgm_process_info.工序编码`（多对一）
- `device_code` → `idi_{}_cloud_management.device.code`（多对一）
- `product_code` → `{}_config.production_config_mgm_material_info.物料编码`（多对一）

---

### 10. `{}_trace_app` 数据库

#### 10.1 `dashboard_config_1` — 智能看板配置

**用途：** 存储智能看板的配置信息，目前仅包含看板标题。支持通过设置页面修改。

**字段定义：**

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `_id` | ObjectId | 主键 | `6a5717b4bb4651c9bd7ba801` |
| `title` | string | 看板标题 | `智能生产看板` |
| `created_at` | datetime | 创建时间 | `2026-07-27T10:00:00.000Z` |
| `updated_at` | datetime | 更新时间 | `2026-07-27T10:00:00.000Z` |

---

## 集合关系图

---

## 附录
