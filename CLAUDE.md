# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在此仓库内编码时提供指引。

> **先读上层**：工作区根目录 `c:\work\MES\CLAUDE.md` 包含全局信息——工作区概览、部署架构（`上位机代码/` 部署在产线 PAD，其余微服务部署在服务器，各应用间通过 RabbitMQ 交互）、全部子项目作用、MES 业务架构要点（核心数据流 / 设备状态体系 / OEE 指标口径 / 工艺路线 vs 产线 / KPI 公式存储）、数据库结构概览等。在本项目内工作前，请先阅读根 CLAUDE.md 获取全局上下文。

## 项目概览

MES 手动产线追溯微应用 —— 制造执行系统追溯微应用。

- **后端**：Python 3.6+ / Tornado（`mg_app_framework`）+ MongoDB（Motor）+ RabbitMQ
- **前端**：Vue 3 + TypeScript + Vite 8 + Tailwind CSS 3
- **尚无测试** —— 早期阶段项目

## 常用命令

### 后端

```bash
# 安装依赖（需要 server/lib/ 下的 mg_app_framework*.whl）
cd server
python -m pip install -r lib/requirements.txt

# 启动开发服务器（:18085，热重载）
cd src
python run_trace_app.py

# 生产模式启动
python run_trace_app.py product

# Swagger 文档：http://localhost:18085/trace_app/docs
```

### 前端

```bash
cd web
npm install
npm run dev      # 开发服务器 :8081，代理 /api → :18085
npm run build    # 生产构建 → web/dist/trace_app/
npm run preview  # 预览生产构建
```

### 打包与部署

```bash
bash release/package.sh                    # 打成 tar 包（原始方式）
release\package_smart_auto.bat             # 自动化打包（无 pause，报错直接退出）
release\package_smart_manu.bat             # 手动打包（有 pause，按键继续）
server/bin/install.sh                      # 安装为 systemd 服务
server/bin/run.sh {start|stop|status|debug} # 服务管理
```

## 架构

### 后端（`server/src/trace_app/`）

应用基于 `mg_app_framework` —— 一套 Tornado 微服务框架，启动装配固定有序：

**启动流程**（`start.py` → `run_trace_app.py`）：
1. `ConfigStore` 设为全局 store（端口 18085，应用名「追溯应用」）
2. 通过 `MongodbConfig` 初始化 MongoDB 连接（host：`192.168.130.252:27017`）
3. 通过 `RabbitMQConfig` 初始化 RabbitMQ 连接（host：`192.168.130.252:5672`）
4. `MyInitFunc` 启动时创建 `db_index_map` 中定义的 MongoDB 索引
5. `app_start(debug_flag)` 启动 Tornado IOLoop（开发模式热重载）
6. HTTP API 文档通过 `tornado_swagger` 在 `/swagger/` 提供

**请求流程**：
- HTTP：请求进入 → `tornado_request_mapping` Route → handler 方法上的 `@request_mapping` 装饰器 → `BaseHandler`（CORS、JSON 序列化、统一响应）→ 响应实体
- WebSocket：`websocket_handler/handler.py` → `/websocket_url` 上的 WebHandler
- Handler 用 `BaseHandler.send_response(Response.success(data, info))` —— 禁止直接用 `write()`
- `BaseHandler` 继承 `HttpBasicHandler`（来自 mg_app_framework），额外加了 CORS 头、统一错误处理，并重写 `write_error` 使 500 时返回 `{code, data, info}`

**Handler 注册**（`handlers/http_handler/urls.py`）：
- 使用 `tornado_request_mapping.Route` 模式：创建 `Route()`，用 `.register()` 注册 handler 类，扩展 `url` 列表
- 新增 handler：创建带 `@request_mapping(path)` 装饰器的类，并在 `urls.py` 中注册
- **所有 Handler 需要用 `generate_handler_classes()` 生成动态子类并注册**，否则 Swagger 文档无法自动生成。参考 `handlers/http_handler/urls.py` 中的模式。
- 现有 API 组：`device_data_handler.py` → `POST api/trace_app/device_data/{list,points,query}`（数采查询：设备列表 / 点位列表 / 信号数据分页查询，无 service 层、handler 内直查）。⚠️ 信号数据的 `name` 与点位下拉的名称**同源**，都出自模块级 `build_point_name_map(device)`：`children[].name` + 硬编码的 `p_kgj_wg→开关机状态`（该点位不在 children 里，且即使出现也统一用固定名），查不到回落点位编码；两处共用同一函数，别各写一份。`material_scan_handler.py` → `POST api/trace_app/material_scan/query`（扫码登料查询，service 见 `service/material_scan_record_service.py`）；`dashboard_handler.py` → `GET/POST api/trace_app/dashboard/config`（看板1 配置，集合 `dashboard_config_1`）；`dashboard2_handler.py` → `GET/POST api/trace_app/dashboard_2/config`（看板2 配置，集合 `dashboard_config_2`；`mock` 字段存模拟数据配置，模块白名单见该文件的 `MOCK_MODULES`，后端只做结构收敛、不校验 `data` 形状）。两个看板配置的字段集一致：`title` / `start_date` / `end_date` / `workshop_code` / `product_type` / `unused_devices`（见「未使用的设备」一节）。⚠️ 每个 `save_config` 都有**两处**字段清单要同步改——`for field, value in [...]` 的 set/unset 循环 + `for field in (...)` 的首次建文档 insert 分支，**漏改后者会让字段在首次建文档时丢失**；请求体模型 `entity/response_model.py::DashboardConfigRequest` 是两处共用的，改一次即可。`base_config_handler.py` → `POST api/trace_app/base_config/{routing_list,routing_processes,process_list,product_type_list,line_list,line_devices}`（生产基础配置查询，查 `{org}_config` 工艺路线/工序表与 `idi_{org}.web_layout_application`）；其中 **`process_list` 是「未选工艺路线时的全部工序」**，供两个新页面（报工查询 / 报工不合格原因）的三级联动在没选路线时填工序下拉，与 `routing_processes`（按路线取工序）配对。`report_query_handler.py` → `POST api/trace_app/report/{query,filter_options,unqualified_reason_query,unqualified_reason_records}`（报工查询 / 人员设备候选 / 报工不合格原因统计 / **不合格原因关联的报工记录反查**，service 见 `service/report_query_service.py`）。⚠️ 后两个端点与 `query` **共用同一个时间条件构造函数** `report_query_service._build_time_condition(start, end)`：`op_time` 存的是 `YYYY-MM-DD HH:mm:ss.SSS` 本地墙上时间字符串（已连库确认），故直接字符串比较、不做时区换算；**终点补 `.999`**——用户选到 23:59 的语义是「含这一分钟」，而 `'23:59:59.708' > '23:59:59'`，不补会把结束那一秒内的记录漏掉。三处时间条件都走它，别在别处再内联一份

**数据库**（`utils/db.py`）：
- `get_db_handler(db_name=None)` → 返回 Motor 数据库句柄（默认 `{organization}_trace_app`）
- `get_collection_handler(name)` → 首次访问自动创建集合及其索引
- 新集合的索引定义加在 `db.py` 顶部的 `db_index_map` dict 中；`MyInitFunc` 启动时会创建
- **读别人的表**：本项目跨服务取数一律**直连 MongoDB 只读**，不调对方服务的 HTTP（先例：`inspection_records`、`process_params_config`、扫码登料记录）。库名走 `collection_utils._get_db_name(db_suffix)` 拼 `{org}_{db_suffix}`，句柄写在 `collection_utils.py` 并注明写入方；**只读，不建索引、不写**

**消息队列**（`utils/mq_config.py`）：
- `subscribe_key_and_process_func` dict 映射 MQ 路由 key → 异步处理函数
- `process_mq_msg` 把入站消息分发到已注册的处理函数
- `send_rabbit_mq(data, key)` 发布消息
- 订阅 `time_interval_status` 获取设备实时状态（`device_exception_compute` 推送，value 为状态码）。`service/device_status_service.py` 在进程内维护 `{device_code: status_code}` 映射（4/5/6 → 2；对外只保留 0 关机 / 1 运行 / 2 待机 / 3 故障），启动时从 `device_exception_status_interval` 集合预填（`my_init_func`），并通过 `DeviceStatusProvider` 经 WebSocket `/ws/device_status`（每 5 秒快照）推给客户端。
- ⚠️ **设备状态对账**：`time_interval_status` 是事件驱动、只在状态变化时发，漏收一条事件会让该设备状态**永久陈旧**（且两个实例各维护一份内存 map，长期分叉）。`device_status_service.py` 每 60 秒从表重读当前活跃时间片（`end_time` 为空的最新一条）整体覆盖内存 map 对账（`refresh_device_status_if_needed`，由 WebSocket push 每 5 秒调用触发），保证实例收敛到表真值。**注意：对账只解决"实例间不一致"，若设备状态链本身冻结（如设备被 `device_exception_compute` 判为离线但时间片不更新），表里的状态本身就是旧的** —— 需上游排查。

**工具**：
- `collection_utils.py` — **跨服务只读集合句柄集中地**。`_get_db_name(db_suffix)` → `f"{org}_{db_suffix}"`；本项目**不拥有**的集合统一在这里取句柄并注明写入方，例如 `get_inspection_records_coll()` / `get_material_scan_records_coll()`（均 `{org}_manual_trace`，由 manual_line_general_traceability 写入）、`get_father_worksheet_coll()`（`{org}_scheduler`）、`get_device_coll()`（`idi_{org}_cloud_management`）。新增跨服务读表时照此办理，别在 service 里手拼库名
- `utils.py` — 二维码生成（qrcode + reportlab）、序列号生成（MES+YYMMDD+NNNNNNN，用 MongoDB 原子计数器）
- `request_utils.py` — 异步 HTTP 客户端封装（send_url_request / send_in_url_request），基于 Tornado AsyncHTTPClient
- `datetime_utils.py` — ISO 8601 时间解析（兼容 Python 3.6）、时区处理
- `string_utils.py` — `StringUtils.is_empty(s)` / `is_empty_or(*args)`
- `device_utils.py` — `normalize_device_codes(raw)`：设备编码列表归一化（转字符串、去空白、丢空项、去重保序）。看板配置的 `unused_devices` 在三个后端消费点（两个 `save_config` + `OeeProvider`）都要收一遍，故抽成一处，**不信任客户端**
- `swagger_utils.py` — Swagger 文档生成工具，提供 `@swagger_doc` 装饰器（支持 TypedDict 模型自动转 schema）和 `generate_handler_classes()`（为每个 API 方法生成动态 Handler 子类）

**响应模式**（`entity/response_entity.py` → `common/response_entity.py`）：
- `Response.success(data, info)` / `Response.fail(info, data)` — 返回统一的 `{code, data, info}` 对象
- entity 包从 common 再导出；统一用 `Response.success()` / `Response.fail()`
- `DefaultEncoder`（JSON）处理 `datetime`、`ObjectId`、`Decimal` 的序列化

### 前端（`web/src/`）

**结构**：
- `main.ts` — Vue 3 应用入口，无 router（单视图应用，用 `currentView` 状态手动切换）
- `App.vue` — 根布局：侧边栏导航 + 主内容区。侧边栏切换 `currentView` ref；`currentView` 用 `localStorage` 持久化（跨标签页/浏览器重开保留），**默认落点看板**（无历史记录时首次打开直接进看板，之后记住上次所在页）
- `views/HomeView.vue` — 首页仪表盘，展示服务状态和 API 端点列表
- `views/HistoryView.vue` — 历史记录页面（开发中）
- `views/TraceQueryView.vue` — 追溯查询（产出码/投入码追溯链路）。工艺参数弹窗头部有「数采数据」按钮：以当前报工记录的设备 + 报工时间为中点**±5min** 跳转数采查询（经 `useDeviceDataNav` 传递，见下）。两个打开工艺参数的入口（追溯行「工艺参数」/ 提交记录「工艺参数」）都补齐了 `device_code` / `op_time` 供该按钮使用。操作列「工艺参数」按钮旁有「检验单」按钮（追溯行与提交记录两个入口都有）：按报工记录的 `workorder_code` 查 `{org}_manual_trace.inspection_records`（由 manual_line_general_traceability 报工时落库，`workorder_code` = 报工的完整追溯工单号），弹窗（加宽到 `max-w-6xl`）展示整体合格/不合格徽标 + 各检验项明细（名称/类型/范围/**检验要求**/**检验工具**/填写值/结果——要求/工具为 manual_line 检验项档案配置的提示文本；不合格原因列收为「查看原因 (N)」按钮，点击后在二级小弹窗逐条展示原因快照 `unqualified_reasons`（`[{reason_code,reason_name}]`，`unqualifiedReasonCount` 计数、非空才可点）；历史报工缺键均显示 `-`）。检验单明细行末另有「查看图片 (N)」入口：项内基准图/实际图任存路径即出计数按钮（N=基准+实际，`imageCount`），点击开二级图片弹窗（`z-[1100]`）分块展示「基准图片（档案配置）/ 实际图片（报工上传）」——图片只存 manual_line_general_traceability 服务器磁盘、`inspection_records.items` 快照只存路径，由 manual_line 的 `download_image` 接口（与 mgDMS 下载文件同约定、不加登录鉴权）跨服务按路径回显，trace_app 以其同源应用前缀绝对路径 `/api/manual_line_general_traceability/inspection_item/download_image` 经自己的 axios 实例请求（生产部署前缀被保留）；基准/实际两张独立加载（每张各包 try/catch，失败互不阻塞）、错误文本统一提示，objectURL 在关闭/组件卸载时 revoke 防泄漏。**该视图全部 7 个弹窗（投入物料/工艺参数/提交记录/检验单/不合格原因二级/检验单图片/投入码选产出）都包在 `<Teleport to="body">` 里渲染**，原因见「弹窗层级」注意项
- `views/ReportQueryView.vue` — **报工查询**（侧边栏「追溯查询」下方，视图键 `report_query`）。数据源 `{org}_order_retrospect.work_order_retrospect_records`（只取 `op_type: "out"` 的产出记录，固定过滤 `is_delete $ne True`）。查询条件 = 6 个下拉单选（产品 / 工艺路线 / 工序 / 人员 / 结果 / 设备）+ 日期范围（`datetime-local`）；`onMounted` 默认填当天 `00:00~23:59` 并自动查一次（故非当天没有报工时画面是空态，属预期）。前三个下拉联动收窄、每级可留空 = 不限（见 `useProductRoutingProcess`）；人员候选 = 报工记录里出现过的 `operator`（显示「昵称 / 工号」，查不到昵称只显工号）；设备候选 = 记录里出现过的设备（显示「设备名称 / 编码」）——**这两组候选刻意不随其它筛选项收窄**（一次 `$facet` 聚合取全量），否则日期一改候选就空掉、看起来像坏了；结果候选 = **四个细分值**（一次合格 / 返工合格 / 复投合格 / 不合格，由 `production_model` + `check_result` 推出）。列表 13 列（`# / 工单号 / 产品 / 工序编码 / 工序名称 / 物料编码 / 物料类型 / 条码 / 操作时间 / 设备名称 / 检测结果 / 操作人 / 操作`），`page_size` 20。⚠️ **页面布局：搜索区收在 `<Teleport>` 弹窗里，页面上只留一条条件栏**（「查询条件」按钮 + 已选条件 chips + 「报工时间」只读回显 + 查询按钮），原因与见「弹窗层级」一节同源（另外 6 个下拉 + 2 个 datetime 平铺会把列表挤没）。列表单元格用 `px-2`、工单号/条码列 `max-w-[150px]`。**操作列 `min-w-[230px]`**：4 个按钮（每个 104px）需要 230px 才不裁切，压缩它会直接把按钮压没。查询条件弹窗 `z-[1000]`。**操作列 4 个按钮（查看投入 / 工艺参数 / 检验单 / 提交记录）用的就是追溯查询页那四个共用弹窗组件**（`components/trace/`）——即「追溯查询页有的弹窗，这一页都要有」，改动共用的弹窗组件时两个页面一起变。投入物料弹窗里的「追溯此码」在本页**不弹页内弹窗**，而是经 `useTraceNav.setPendingTraceCode()` 切到追溯查询页、由那边自动按该码查关联产出（与追溯查询页内的行为不同：那边是页内弹「选择产出码」，见 `useTraceNav`）
- `views/UnqualifiedReasonView.vue` — **报工不合格原因**（视图键 `unqualified_reason`，侧边栏紧跟报工查询）。按产品 / 工艺路线 / 工序三个联动下拉 + **报工时间范围**统计**报工时检验单的各不合格原因次数**，列表 `# / 不合格原因 / 次数 / 操作`（原因列 = 名称 + 灰色小字 `reason_code`），次数降序、同次数按原因编码升序，`page_size` 20（快照不足一屏时分页条不出现）。聚合口径与看板2 的不合格原因饼图**同源**（`service/report_query_service.collect_unqualified_reason_counts`）：只统计检验项 `is_qualified=False` 且**勾了原因**的项，未勾原因的不合格项不计入。**布局与报工查询页同款**：条件（3 个下拉 + 报工时间起/止两个 `datetime-local`）全部收在 `<Teleport>` 条件弹窗（`z-[1000]`）里，页面上只留条件栏（「查询条件」按钮 + 产品/路线/工序 chips + **「报工时间」只读回显** + 查询按钮）。⚠️ **时间留空 = 不限（全量统计）**，与报工查询页「日期必填、默认当天」**刻意不同**：本页数据是 `inspection_records`、量少且非当天，若也默认当天就会开屏即空；弹窗页脚写明「时间留空 = 不限，全量统计」。⚠️ 时间回显不做成可清除的 chip——弹窗里是两个输入框，清空即回到不限，再给一个 ✕ 属于两套入口。⚠️ **「重置」是 async**（内部 `await onProductChange()` 清下级），时间清空发生在之后的微任务里，页面验收读输入框值前要条件等待、别写死 sleep。**操作列每行一个「报工记录」按钮**：弹窗（`z-[999]`）复用报工查询那套 13 列表格与行结构 —— 后端 `_shape_records` 批量补工序名/设备名/操作人昵称，两个页面共用，故行内 4 个按钮（查看投入 / 工艺参数 / 检验单 / 提交记录）也是同一批共用弹窗组件；请求会带上**页面当前的三个条件 + 时间范围**，否则弹窗条数会与左侧次数对不上。一次报工对应一张检验单，故条数可能**少于**左侧次数（同一张单勾多次只算一条报工），断言时用 `< 次数` 而非相等。⚠️ **不在 `onMounted` 预查**：本项目视图全部常驻挂载，`onMounted` 会在用户还没进这页时就先跑一次全表聚合；改为 `watch(currentView)` 命中本页且未查过时才查（`{immediate: true}` 兜住「上次退出时正停在本页」的情形）
- `views/DeviceDataView.vue` — 数采查询（按设备/点位/时间段查 `datas` 表信号数据）。表格列为 `# / 信号名称 / 信号编码 / 信号值 / 采集时间`——**「信号名称」是后端按点位编码回填的**（`datas` 表只有 `code`，名称只存在于 `idi_{org}_cloud_management.device` 的 `children[].name`），查不到的名字回落显示点位编码本身（如 `zb_sbzt` 这类不在设备点位配置里的 KPI 点位）。**点位下拉单选且支持清空**（`CustomSelect` 传 `clearable`，✕ 清空后回到占位「全部点位」＝不传 `point_code` 查全部）。`watch(useDeviceDataNav().state.pending)` 消费追溯查询跳转预填：填充设备 + 起止时间后自动查询（点位清空查全部）。⚠️ 查询参数走 `utils/datetime.ts` 的 `toIsoSeconds`（`datetime-local` 值补秒后**原样发**），**绝不能用 `new Date(...).toISOString()`** —— 见「时间口径」注意项
- `views/MaterialScanQueryView.vue` — 扫码登料查询（视图键 `material_scan_query`，侧边栏在「报工不合格原因」下方）。查询条件 = 码值（模糊）+ 时间范围（`datetime-local`，默认当天 00:00~23:59），下方分页表格（产品/工序/物料/码值/操作人/操作时间/操作，`page_size` 默认 20）。数据源为 `{org}_manual_trace.material_scan_records`（manual_line_general_traceability 扫码登料落库）。**每行「操作」列有跳转数采查询按钮**：复用 `navigateToDeviceData({device_code, report_time: op_time})`（与追溯查询同一套 `useDeviceDataNav` 单例），成功则 `currentView = 'device_data'`；记录的 `device_code` 为空时 `navigateToDeviceData` 返回 `false`，按既有先例 toast 提示"无法跳转"。⚠️ 本项目无 router，新增视图须**同时**改两处：`Sidebar.vue` 的 `navItems` 加项 + `App.vue` 加 import 与 `v-show`，无兜底注册
- `views/dashboard/` — 智能生产看板；`DashboardView.vue` 只做布局 + 状态管理（WebSocket 连接、从看板配置读取查询日期/产线），各卡片拆在 `views/dashboard/components/`：`HeaderBar`（顶栏）、`OeeCard`（OEE 仪表盘）、`DeviceStatusCard`（产线设备实时状态，产线为空 = 全部产线）、`PlanActualOutputCard`（计划/实际产量，WebSocket 实时，三块：计划产量 / 实际产量 / 产量进度，按配置的产品型号过滤，统计日期取配置的时间范围、不配置默认当天）、`ProcessQualifiedRateCard`（工序合格率，WebSocket 实时）、`HourlyOutputCard`（小时产量统计，WebSocket 实时柱状图）、`HistoryDataCard`（历史数据，进看板时 HTTP 查一次：前两周不含今天、每天一列的表格（行=日均一次合格率/日均小时完成量/日完成量，列=日期），按配置的产品型号过滤）。看板标题 / 查询日期 / 产线 / 产品型号（数据源 `production_config_type` 表）/ 未使用的设备等配置在 `views/dashboard/DashboardSettingsView.vue`（智能看板设置）维护，看板加载时经 `getDashboardConfig` 一并获取并应用（`unused_devices` 经 prop 下发给设备卡、经 `setUnusedDevices()` 下发给 OEE，见「未使用的设备」一节）。两个设置页（含看板2 的 `BoardSettingsView.vue`）的「产线」单选均支持清空（`CustomSelect` 加 `clearable` prop），产线为空 = 查询全部产线——当前仅「产线设备」卡消费产线（空值时后端 `query_line_devices` 不过滤返回全部生产单元分组），其余卡不按产线过滤。科技主题共用样式集中在 `views/dashboard/dashboard.theme.css`（`tech-panel` 四角括号面板 / `tech-panel-title` / `tech-badge` / `chart-card-placeholder` 预留占位 / 全局动画 keyframes），由 `DashboardView.vue` 引入，看板内组件共用。⚠️ `OeeCard` / `DeviceStatusCard` 被**看板1 与看板2 共用**，为支持看板2 的模拟数据各加了一个**可选** prop `mockData`（不传 = 走原真实链路，看板1 行为不变）——改动这两个组件时须保持向后兼容
- `views/dashboard2/` — 智能看板2，与看板1完全独立：`BoardView.vue` 做布局（两行两列：OEE / 产线设备实时状态 / 工序加工情况 / 不合格原因占比）+ 状态管理（加载 `getDashboardConfig2` 配置后下发日期/产线/**产品型号**/**未使用的设备**并统一启动各卡片）；`BoardSettingsView.vue` 维护配置；`components/ProcessProductionCard.vue`（工序加工情况，WebSocket `/ws/process_production` 实时，经 `composables/useProcessProduction.ts` 管理；数据行列表复用 `ui/SeamlessScroll.vue` 通用无缝滚动组件，内容超出一屏按"单步式"循环滚动（每步平滑滚一行 + 停留，约 2 秒一行）、不足一屏静止；表头拆到滚动区外固定，表头/表体拆成两表、列宽用 `col-*` class 在 `th`/`td` 上共用保证对齐）；`components/UnqualifiedReasonPieCard.vue`（**不合格原因占比饼图**，SVG 自绘圆环不引 echarts，进看板时 `load()` 查一次、60s 自动刷新）：数据源 `{org}_manual_trace.inspection_records`（manual_line 报工时落库的检验单），聚合口径 = **勾选的原因为样本**（每张检验单 `items` 中 `is_qualified=False` 的项，其 `unqualified_reasons` 快照 `[{reason_code,reason_name}]` 逐条各计 1、一项可勾多个原因都计入；**未勾原因的不合格项**（检验项档案未配原因、或该类型原本不允许配原因的旧快照）**不进入统计**，按原因聚合、扇区 = 该原因被勾选次数 ÷ 全部勾选原因总次数）；筛选三项与看板2 配置一致、空即不限：日期（`op_time` 字符串范围，`>=起 00:00:00`、`<止+1天 00:00:00`）、产线（`web_layout_application` 车间代号 → 生产单元代号集合 → `produce_unit_code $in`，检验单无车间字段）、产品型号（型号编码与产品编码人工一致 → `product_code $in`）；接口 `POST api/trace_app/dashboard_2/unqualified_reason_pie`，统计在 `service/dashboard2_unqualified_pie_service.py` 的 `get_unqualified_reason_pie`（旧**检验项不合格占比** `components/UnqualifiedPieCard.vue` + 接口 `unqualified_pie` 保留未删，备用）；两类饼图前端组件与后端聚合共用同一 SVG 圆环/筛选骨架，区别仅口径（不合格项 vs 原因）与文案。**模拟数据配置（客户演示用）**：`BoardSettingsView.vue` 的「模拟数据配置」区块按模块（`oee` / `device_status` / `process_production` / `unqualified_reason`，key 须与后端 `dashboard2_handler.MOCK_MODULES` 一致）分行列出，每行一个启停开关 + 「模拟数据」按钮，点按钮开 `<Teleport to="body">` 弹窗（`z-[1000]`）编辑 JSON，弹窗内实时校验并可「填入示例」（各模块 `example` 同时是占位提示与示例来源，是该模块 JSON 形状的唯一出处）；开关会持久生效，**开启但未填 / JSON 不合法都不允许开启**（`toggleMock` 拦、`buildMockConfig` 保存前再拦一次），清空数据自动关开关。落库为看板配置的 `mock` 字段（`{模块: {enabled, data}}`，未启用且无内容的模块不落库，未启用但留了数据的保留以便重新开启）；`BoardView.vue` 读配置后经 `mockDataOf(key)` 把已启用模块的数据以 `:mock-data` prop 下发给四张卡片，卡片收到即直接用配置数据、**不连 WebSocket 也不查接口**。⚠️ 下发靠 prop，而 `BoardView.onMounted` 里 `setDate`/`start`/`load` 都是同步调用，**必须先 `await nextTick()`** 让 props flush，否则卡片仍读到旧值、模拟数据进不去（表现为"配了看板没反应"）。⚠️ **看板本体绝不能出现任何模拟/演示字样**（客户演示专用），故模拟模式下徽标仍显「实时」——四张卡各加了 `badgeLive`（`isMock || connected`）等替代判断，否则无 WS 连接会显成「断开」，一眼看出与正式不一致。诚实性约束：**设置页必须如实展示**（区块叫「模拟数据配置」、开关状态可见、有启用数量告警条），保证不会被误留在开启态而无人察觉
- `composables/useServiceStatus.ts` — 共享服务状态 composable，模块级单例，自动检测后端健康状态
- `composables/useDeviceDataNav.ts` — 追溯查询 → 数采查询的跨视图跳转预填（应用无 router、视图 `v-show` 常驻挂载，故用模块级单例状态传递）。导出 `useDeviceDataNav()`（返回 `state`：`device_code`/`start_time`/`end_time`/`pending`）、`navigateToDeviceData({device_code, report_time})`（以报工时间为中心 **±5min** 计算起止时间并置 `pending=true`）、`formatDatetimeLocal`（`YYYY-MM-DDTHH:mm`，与数采查询搜索栏一致）。写方 TraceQueryView（工艺参数弹窗的报工记录）/ MaterialScanQueryView（扫码登料记录行），读方 DeviceDataView。⚠️ `formatDatetimeLocal` **只到分钟**，故实际查询窗口是「报工时刻 ±5min 向下取整到分」（如报工 08:44:39 → 查 `[08:39:00, 08:49:00]`），不是 `[08:39:39, 08:49:39]`——写用例算预期条数时按前者
- `composables/useProductRoutingProcess.ts` — **产品 / 工艺路线 / 工序三级联动**（报工查询与报工不合格原因页共用）。导出 `productType`/`routingCode`/`processCode`、三组候选 `productOptions`/`routingOptions`/`processOptions`、`loadBaseOptions`/`loadProcessOptions`、`onProductChange`/`onRoutingChange`、`buildFilter`。口径：选产品 → 工艺路线只剩该产品的（该产品无路线映射时回落全部）；选路线 → 工序调 `base_config/routing_processes` 按路线取，**没选路线则调 `base_config/process_list` 取全库工序**；**每一级都能不选（不选 = 不限，`buildFilter()` 对未选项传 `undefined`）**；换上级自动清空下级。⚠️ 级联必须挂 `@change` 而**不能** `watch(modelValue)` —— `CustomSelect` 的 `change` 只在用户交互时 emit，程序化清空不触发；反过来用 watch 又会与「清空下级」互相触发成环
- `composables/useReportDialogs.ts` — 报工查询页四组弹窗的开合与二级跳转状态：`visible`/`step` + `openInput`/`openParam`/`openInspection`/`openSubmission` + `openDetailFromSubmission({kind, record, step})`（从「提交记录」行内再开投入/工艺参数/检验单，`kind` ∈ input/param/inspection）。`openParam` 会额外补 `device_code`/`op_time`，供工艺参数弹窗的「数采数据」按钮跳数采查询
- `composables/useTraceNav.ts` — **报工查询 → 追溯查询的跨视图带码跳转**（与 `useDeviceDataNav` 同套手法：模块级单例状态，因无 router、视图 `v-show` 常驻挂载）。`setPendingTraceCode(code)` 写、`takePendingTraceCode()` 取走并清空、`usePendingTraceCode()` 返回 ref 供读方 watch。写方报工查询页（投入物料弹窗的「追溯此码」），读方追溯查询页（消费后自动按该码查关联产出）
- `composables/useWebSocket.ts` — 通用 WebSocket composable，⚠️ `send()` 在连接未就绪（无 `ws` 或未 OPEN）时**静默丢弃**消息。因此所有带查询参数的 WS 业务 composable（`useDashboardWebSocket`(OEE)/`useProcessQuality`/`useHourlyOutput`/`usePlanActualOutput`/`useProcessProduction`）统一模式：内部缓存 `pendingDate`（及 `pendingProductTypes` / `pendingUnusedDevices`），`connect()` 时在 `onConnected` 回调里**补发**。父组件看板是**先 `setDate()` 再 `start()`**，配置就靠这次补发到达后端；后端每个 WS 端点按连接重建 provider（`handler.open()` → `register(provider_cls())`，OeeProvider 等 `_query_start` 归 None），查询日期不跨连接保留，断线重连后同样靠 `onConnected` 重发恢复。**新增 WS 卡务必沿用此模式**，否则配置日期会丢失、后端恒按「今天」查询（历史教训：OEE 卡曾漏掉补发导致配置区间永远不生效，见 2026-09-03 修复）
- `api/trace-app.ts` — API 方法，使用 `httpWrap.ts` 的 `_get`/`_post`
- `api/httpWrap.ts` — Axios 实例，带登录跳转拦截器、base URL 自动识别（开发 vs 部署），定义了 `ApiResponse<T>` 统一响应类型
- `utils/datetime.ts` — 日期时间工具（**时间口径约定的唯一出处**，文件头有完整说明）。`formatDateLocal(d)` 取本地日期 `YYYY-MM-DD`；`toIsoSeconds(v)` 把 `datetime-local` 值（`YYYY-MM-DDTHH:mm`，只到分）补秒成 `YYYY-MM-DDTHH:mm:ss`。新增涉及时间的前端代码一律复用这里，别自己 `new Date()` 拼
- `utils/codeList.ts` — 逗号分隔编码输入的解析/回填（`parseCodeList` / `formatCodeList`），两个看板设置页的「未使用的设备」共用，见「未使用的设备」一节

**可复用 UI 组件**：
- `CleanTable.vue` — 表格，支持全选 checkbox、slot 单元格定制、空状态、双击事件。Props：`data`、`columns`、`selectable`
- `CustomSelect.vue` — 下拉框，实心/描边两种样式，点击外部关闭，禁用状态。v-model 兼容。支持 `clearable` prop（默认 false）：已有值且非禁用时右侧显示 ✕ 清除按钮，点击置空并 `emit('update:modelValue','')` + `emit('change','')`（看板设置页"产线"用它实现"不选 = 全部产线"）
- `components/trace/` — **追溯查询与报工查询共用的四个弹窗**（两个页面的操作列按钮完全一致，行为也要一致，故抽成共用组件；**改动这里两个页面一起变**）：`MaterialInputDialog.vue`（投入物料明细，表头 `物料编码/物料类型/条码/数量/操作时间/操作`，行内「追溯此码」→ `emit('trace-code', code)`，由使用方决定是页内开「选择产出码」还是跳追溯查询页）、`ProcessParamDialog.vue`（工艺参数，头部「数采数据」按钮 → 跳数采查询）、`InspectionDialog.vue`（检验单，含二级「不合格原因」与「检验项图片」）、`SubmissionDialog.vue`（提交记录，行内三按钮 → `emit('open-detail', {kind, record, step})` 后自关）。**弹窗自己按传入的记录取数**，使用方只管传记录与开合。⚠️ 四个弹窗全部包在 `<Teleport to="body">`（见「弹窗层级」注意项），二级弹窗 `z-[1100]`、主弹窗 `z-[1000]`
- `ui/Toast.vue` — 自动消失的通知（成功/错误/警告/信息），默认 3 秒
- `ui/ConfirmDialog.vue` — 返回 Promise\<boolean\> 的确认弹窗。通过 `utils/dialog.ts` 的 `showConfirm()` 使用
- `ui/SeamlessScroll.vue` — 通用无缝循环滚动组件（看板类列表自动滚动复用）：内容经默认 slot 传入，组件内双份渲染 + 单步式滚动——每 `moveMs` 平滑滚一行、停 `waitMs`，合计约 2 秒一行；每次位移正好一行（整数像素，无亚像素抖动）、滚动有缓动过渡、其余时间静止，比连续匀速 CSS 动画在低端设备上更丝滑省电。Props：`moveMs`（滚一行动画时长，默认 600）、`waitMs`（到位停留时长，默认 1400）、`hover`（悬停暂停，默认 true）；自动测量内容高度/行高，**不足一屏静止不滚动**；容器高度由使用方 class 控制（如 `flex-1 min-h-0`）；**使用方需保证行高为整数**（内容行 `line-height` 用整数 px，否则位移出现亚像素抖动）；滚动内容项勿用 margin（两份内容接缝会跳变），用 padding 代替；有表头场景需把表头拆到滚动区外固定，且列宽 class 须 `th`/`td` 共用（见 `ProcessProductionCard` 的 `col-*` 用法）

**开发服务器**：
- Vite 在 `0.0.0.0:8081`
- 开发时代理 `/api/*` → `localhost:18085`（检验单图片回显的跨服务例外：`/api/manual_line_general_traceability/*` 需先代理 → `localhost:10082`，见 `vite.config.ts`——Vite 按对象键序匹配前缀，该跨服务键必须写在 `/api` 键**之前**，否则会被 `/api` 转发到本后端 404）
- 构建产物输出到 `web/dist/trace_app/`
- ⚠️ **`vite.config.ts` 里 `build.target` 必须是 `chrome64`，不要调高** —— 看板要在产线电视（安卓 TV，内置浏览器/WebView 内核普遍偏老）上打开，`chrome88` 产物里的 ES2020/21 语法（`??=`/`||=`/`??`）会让老内核 `SyntaxError` 直接白屏。`chrome64` 已足够低（`import.meta` 需 64+，再低要上 `@vitejs/plugin-legacy`）
- ⚠️ **弹窗层级**：App.vue 正常布局里，左导航 `Sidebar`（桌面 `relative z-20`，移动 `fixed z-50`）与主内容列（`relative z-10`，含 Header/各视图）是**兄弟层叠上下文**——任何 `fixed` 弹窗若直接写在视图模板内，会被限定在主内容列的 z-10 层叠上下文里，**永远盖不过 z-20 的导航栏**（宽弹窗左缘被导航栏遮住）。**因此带侧边栏页面里的弹窗一律用 `<Teleport to="body">` 包起来渲染**（参考 TraceQueryView 的 7 个弹窗：`<Teleport to="body"><transition name="modal-fade">…</transition></Teleport>`），teleport 到 body 后 `z-[1000/1100]` 在文档根级生效，压过导航栏。Toast / ConfirmDialog（`utils/dialog.ts`）本就 `createVNode + render` 挂到 `document.body`，不受影响；全屏看板（dashboard/dashboard2）无侧边栏、无此问题。
- ⚠️ **时间口径（踩过大坑，务必遵守）**：MES 各库的时间字段（`idi_{org}.datas.timestamp`、`{org}_manual_trace.material_scan_records.op_time` 等）存的是**服务器本地墙上时间（北京时间）**，不是 UTC——尽管 `datas.timestamp` 的 BSON 类型是日期、读出来带 `+00:00` 标记，那只是标记假象，值本身就是北京时间的数字。因此**前后端一律按"墙上时间"直接比较，绝不做本地 ↔ UTC 换算**：后端先例 `oee_service`（`datetime.now()` 裸值直接比 `datas.timestamp`）、`material_scan_record_service._normalize_time`（本地时间串直接比 `op_time` 字符串）。**反向教训（2026-09-12 修复）**：数采查询页曾对本地时间串调 `toISOString()`，整体偏 8 小时，跳转后窗口落在 `00:39~00:49` 只查到 1 条（真实窗口 `08:39~08:49` 有 415 条）；同类的还有看板里的 `new Date().toISOString().slice(0,10)` 取「今天」——`toISOString` 是 UTC 日期，**北京时间 00:00~07:59 之间会取到"昨天"**，看板会显示前一天数据。取日期用 `utils/datetime.ts` 的 `formatDateLocal`。
- 全局 `http_base_url` 和 `websocket_base_url` 通过 Vite `define` 定义

### 「未使用的设备」（两个看板配置项，2026-09-14 新增）

两个智能看板的配置页各有一个「**未使用的设备**」输入框，用户填设备编码、逗号分隔。语义：**名单里的设备不显示状态、整体不参与 OEE 统计（含合格率）**。落库为看板各自配置的 `unused_devices` 数组字段（空数组 = 不排除，与不配置等价）。

链路与三个必须知道的坑：

1. **输入解析**：设置页输入框里保持用户原样的文本（`unusedDevicesText` ref），**保存时才解析**成数组——`web/src/utils/codeList.ts` 的 `parseCodeList` / `formatCodeList`（中英文逗号都拆、去空白、丢空项、去重保序）。中英文逗号都认是刻意的：现场用中文输入法敲出来的是全角「，」，只认半角的话这个框会**安静地不生效**。后端 `normalize_device_codes` 按同口径再收一遍。⚠️ 别改成边输入边解析——会把用户正在敲的半个编码吃掉。
2. **设备状态（需求 2）必须在"设备清单"上过滤，不能只过滤状态 map**：设备清单来自 HTTP `queryLineDevices`（`units[] → devices[]`），状态来自 WS 全量 `{device_code: status_code}` map。`DeviceStatusCard.allDevices` 对查不到状态的设备**兜底"关机"**——只滤状态 map 的话，被排除的设备仍留在清单里，反倒渲染成一排灰色关机磁贴，正是需求要避免的。过滤点：`DeviceStatusCard.vue` 的 `filterUnusedUnits()`，**只在 `loadLineDevices()`（真实链路）一处收尾调用**；**某生产单元的设备被全部滤掉时连同该单元一起去掉**，否则 `units.length == 0` 与 `hasDevices` 两个判断会对不上，面板出现空网格 + 图例而不是「暂无设备数据」。实现选**前端可选 prop**（`unusedDevices`）而不是后端在 `query_line_devices` 里过滤：该接口是通用的 `base_config` 端点、不该耦合看板配置，且两个看板的名单各自独立、端点分不清调用方。
   ⚠️ **模拟链路不过滤（2026-09-14 需求方明确）**：`applyMock()` **不调用** `filterUnusedUnits`，配置的模拟数据整份照搬。口径是「**启用了模拟数据的模块就完全按模拟数据展示，其余条件一概不参与**」——模拟配置按模块各带 `enabled`（`mock.oee` / `mock.device_status`…），故按模块判定，不是整块看板级别：看板2 若只启用了 `device_status` 的模拟，设备区台台照显示，而 `oee` 未启用模拟、走真实链路，名单对 OEE 照常生效。产品上说得通：模拟数据是给客户演示的，演示时看到的设备必须与配置里写的分毫不差，不该被另一处配置悄悄删掉几台。**据此别再把过滤"补齐"到模拟链路上。**
3. **OEE（需求 3）的名单只能由前端经 WS 推给后端**：两个看板**共用同一个 `/ws/oee` 端点、同一个 `OeeProvider`、同一个 `calculate_oee`**，服务端无从判断调用方是谁（也无法去查配置——查哪一份？）。故新增 WS action `set_unused_devices`（与既有 `set_date` 对称），`OeeProvider._exclude_devices` 仅作用于本连接。**沿用「连接前缓存、连上补发」模式**（`useDashboardWebSocket` 的 `pendingUnusedDevices`），因为 provider 随连接重建、名单不跨连接保留。父组件两个看板都是**先 `setUnusedDevices()` 再 `start()`**——顺序反了首屏那次统计会把名单里的设备算进去。后端过滤落在两处：`calculate_oee` 里把编码从 `devices` 名单剔掉（下面 5 个 KPI 全按该名单聚合，一处生效），合格率另走报工记录、单独把 `excluded` 传给 `_calc_quality_rate`。⚠️ 合格率用 `device_code: {"$nin": [...]}` 而非 `$ne`：`device_code` 缺失/为空的历史报工记录**不属于任何被排除设备，要原样计入分子分母**，用 `$ne` 会把它们一起剔掉、改变既有合格率口径。

**兼容性**：`set_unused_devices` 是纯新增 action，`connection_manager.handle_message` 对未知 action 静默忽略，故**前后端可任意顺序部署**；`unused_devices` 为空/未传时全链路行为与改动前完全一致（`OeeCard` / `DeviceStatusCard` 的该 prop 均为可选，看板1 与看板2 共用组件、不传即原行为）。

**范围边界**：其余看板卡（工序合格率 / 工序加工情况 / 小时产量 / 计划实际产量 / 不合格原因占比）**不消费**该名单；`_get_workshop_device_codes()` 取全部 `type=device` 设备、**不按产线过滤**是既有口径，本次只在其上叠加排除、未改动。

## 开发模式

- **后端**：每个 API 组一个 handler 类，位于 `handlers/http_handler/`，在其 `urls.py` 注册。所有 handler 继承 `BaseHandler`。业务逻辑放 `service/`。
- **前端**：新 API 方法加到 `api/trace-app.ts`。新视图加到 `views/`，并在 `App.vue` 侧边栏加 `currentView` 判断。新可复用组件放 `components/`。
- **新增 MongoDB 集合**：在 `utils/db.py` 的 `db_index_map` 加索引定义；`get_collection_handler()` 首次使用会自动建集合。
- **新增 MQ 订阅**：在 `utils/mq_config.py` 的 `subscribe_key_and_process_func` 加 `"routing_key": handler_func`。
- **未配置 TypeScript 路径别名** —— `web/src/` 里用相对导入。
- **Tailwind 自定义 token** 定义在 `tailwind.config.js` —— `bg-background`、`text-accent`、`text-muted-foreground`、`border-border` 等，保持统一使用。
- **前后端联调方式**：除非明确使用外部接口（通过 `config.py` 中 `ConfigStore` 配置的外部 API 地址），否则前端调用的 API 都是本项目 server 自身的接口。因此修改功能时通常需要 **web（前端）和 server（后端）同步修改** —— 新增/修改 handler、注册路由、更新前端 API 调用。单端改动只适用于纯 UI 调整或纯后端逻辑（如 MQ 消费、定时任务）。
