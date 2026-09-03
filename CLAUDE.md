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

**数据库**（`utils/db.py`）：
- `get_db_handler(db_name=None)` → 返回 Motor 数据库句柄（默认 `{organization}_trace_app`）
- `get_collection_handler(name)` → 首次访问自动创建集合及其索引
- 新集合的索引定义加在 `db.py` 顶部的 `db_index_map` dict 中；`MyInitFunc` 启动时会创建

**消息队列**（`utils/mq_config.py`）：
- `subscribe_key_and_process_func` dict 映射 MQ 路由 key → 异步处理函数
- `process_mq_msg` 把入站消息分发到已注册的处理函数
- `send_rabbit_mq(data, key)` 发布消息
- 订阅 `time_interval_status` 获取设备实时状态（`device_exception_compute` 推送，value 为状态码）。`service/device_status_service.py` 在进程内维护 `{device_code: status_code}` 映射（4/5/6 → 2；对外只保留 0 关机 / 1 运行 / 2 待机 / 3 故障），启动时从 `device_exception_status_interval` 集合预填（`my_init_func`），并通过 `DeviceStatusProvider` 经 WebSocket `/ws/device_status`（每 5 秒快照）推给客户端。
- ⚠️ **设备状态对账**：`time_interval_status` 是事件驱动、只在状态变化时发，漏收一条事件会让该设备状态**永久陈旧**（且两个实例各维护一份内存 map，长期分叉）。`device_status_service.py` 每 60 秒从表重读当前活跃时间片（`end_time` 为空的最新一条）整体覆盖内存 map 对账（`refresh_device_status_if_needed`，由 WebSocket push 每 5 秒调用触发），保证实例收敛到表真值。**注意：对账只解决"实例间不一致"，若设备状态链本身冻结（如设备被 `device_exception_compute` 判为离线但时间片不更新），表里的状态本身就是旧的** —— 需上游排查。

**工具**：
- `utils.py` — 二维码生成（qrcode + reportlab）、序列号生成（MES+YYMMDD+NNNNNNN，用 MongoDB 原子计数器）
- `request_utils.py` — 异步 HTTP 客户端封装（send_url_request / send_in_url_request），基于 Tornado AsyncHTTPClient
- `datetime_utils.py` — ISO 8601 时间解析（兼容 Python 3.6）、时区处理
- `string_utils.py` — `StringUtils.is_empty(s)` / `is_empty_or(*args)`
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
- `views/TraceQueryView.vue` — 追溯查询（产出码/投入码追溯链路）。工艺参数弹窗头部有「数采数据」按钮：以当前报工记录的设备 + 报工时间为中点±30min 跳转数采查询（经 `useDeviceDataNav` 传递，见下）。两个打开工艺参数的入口（追溯行「工艺参数」/ 提交记录「工艺参数」）都补齐了 `device_code` / `op_time` 供该按钮使用。操作列「工艺参数」按钮旁有「检验单」按钮（追溯行与提交记录两个入口都有）：按报工记录的 `workorder_code` 查 `{org}_manual_trace.inspection_records`（由 manual_line_general_traceability 报工时落库，`workorder_code` = 报工的完整追溯工单号），弹窗展示整体合格/不合格徽标 + 各检验项明细（名称/类型/范围/**检验要求**/**检验工具**/填写值/结果——要求/工具为 manual_line 检验项档案配置的提示文本，历史报工缺键显示 `-`）
- `views/DeviceDataView.vue` — 数采查询（按设备/点位/时间段查 `datas` 表信号数据）。`watch(useDeviceDataNav().state.pending)` 消费追溯查询跳转预填：填充设备 + 起止时间后自动查询（点位清空查全部）
- `views/dashboard/` — 智能生产看板；`DashboardView.vue` 只做布局 + 状态管理（WebSocket 连接、从看板配置读取查询日期/产线），各卡片拆在 `views/dashboard/components/`：`HeaderBar`（顶栏）、`OeeCard`（OEE 仪表盘）、`DeviceStatusCard`（产线设备实时状态，产线为空 = 全部产线）、`PlanActualOutputCard`（计划/实际产量，WebSocket 实时，三块：计划产量 / 实际产量 / 产量进度，按配置的产品型号过滤，统计日期取配置的时间范围、不配置默认当天）、`ProcessQualifiedRateCard`（工序合格率，WebSocket 实时）、`HourlyOutputCard`（小时产量统计，WebSocket 实时柱状图）、`HistoryDataCard`（历史数据，进看板时 HTTP 查一次：前两周不含今天、每天一列的表格（行=日均一次合格率/日均小时完成量/日完成量，列=日期），按配置的产品型号过滤）。看板标题 / 查询日期 / 产线 / 产品型号（数据源 `production_config_type` 表）等配置在 `views/dashboard/DashboardSettingsView.vue`（智能看板设置）维护，看板加载时经 `getDashboardConfig` 一并获取并应用。两个设置页（含看板2 的 `BoardSettingsView.vue`）的「产线」单选均支持清空（`CustomSelect` 加 `clearable` prop），产线为空 = 查询全部产线——当前仅「产线设备」卡消费产线（空值时后端 `query_line_devices` 不过滤返回全部生产单元分组），其余卡不按产线过滤。科技主题共用样式集中在 `views/dashboard/dashboard.theme.css`（`tech-panel` 四角括号面板 / `tech-panel-title` / `tech-badge` / `chart-card-placeholder` 预留占位 / 全局动画 keyframes），由 `DashboardView.vue` 引入，看板内组件共用
- `views/dashboard2/` — 智能看板2，与看板1完全独立：`BoardView.vue` 做布局（两行两列：OEE / 产线设备实时状态 / 工序加工情况 / 检验项不合格占比）+ 状态管理（加载 `getDashboardConfig2` 配置后下发日期/产线/**产品型号**并统一启动各卡片）；`BoardSettingsView.vue` 维护配置；`components/ProcessProductionCard.vue`（工序加工情况，WebSocket `/ws/process_production` 实时，经 `composables/useProcessProduction.ts` 管理；数据行列表复用 `ui/SeamlessScroll.vue` 通用无缝滚动组件，内容超出一屏按"单步式"循环滚动（每步平滑滚一行 + 停留，约 2 秒一行）、不足一屏静止；表头拆到滚动区外固定，表头/表体拆成两表、列宽用 `col-*` class 在 `th`/`td` 上共用保证对齐）；`components/UnqualifiedPieCard.vue`（**检验项不合格占比饼图**，SVG 自绘圆环不引 echarts，进看板时 `load()` 查一次、60s 自动刷新）：数据源 `{org}_manual_trace.inspection_records`（manual_line 报工时落库的检验单），聚合口径 = **不合格项为样本**（每张检验单 `items` 中 `is_qualified=False` 的项各计 1，按 `item_code` 聚合，扇区 = 该检验项不合格数 ÷ 总不合格项数）；筛选三项与看板2 配置一致、空即不限：日期（`op_time` 字符串范围，`>=起 00:00:00`、`<止+1天 00:00:00`）、产线（`web_layout_application` 车间代号 → 生产单元代号集合 → `produce_unit_code $in`，检验单无车间字段）、产品型号（型号编码与产品编码人工一致 → `product_code $in`）；接口 `POST api/trace_app/dashboard_2/unqualified_pie`，统计在 `service/dashboard2_unqualified_pie_service.py`
- `composables/useServiceStatus.ts` — 共享服务状态 composable，模块级单例，自动检测后端健康状态
- `composables/useDeviceDataNav.ts` — 追溯查询 → 数采查询的跨视图跳转预填（应用无 router、视图 `v-show` 常驻挂载，故用模块级单例状态传递）。导出 `useDeviceDataNav()`（返回 `state`：`device_code`/`start_time`/`end_time`/`pending`）、`navigateToDeviceData({device_code, report_time})`（以报工时间为中心 ±30min 计算起止时间并置 `pending=true`）、`formatDatetimeLocal`（`YYYY-MM-DDTHH:mm`，与数采查询搜索栏一致）。写方 TraceQueryView，读方 DeviceDataView
- `api/trace-app.ts` — API 方法，使用 `httpWrap.ts` 的 `_get`/`_post`
- `api/httpWrap.ts` — Axios 实例，带登录跳转拦截器、base URL 自动识别（开发 vs 部署），定义了 `ApiResponse<T>` 统一响应类型

**可复用 UI 组件**：
- `CleanTable.vue` — 表格，支持全选 checkbox、slot 单元格定制、空状态、双击事件。Props：`data`、`columns`、`selectable`
- `CustomSelect.vue` — 下拉框，实心/描边两种样式，点击外部关闭，禁用状态。v-model 兼容。支持 `clearable` prop（默认 false）：已有值且非禁用时右侧显示 ✕ 清除按钮，点击置空并 `emit('update:modelValue','')` + `emit('change','')`（看板设置页"产线"用它实现"不选 = 全部产线"）
- `ui/Toast.vue` — 自动消失的通知（成功/错误/警告/信息），默认 3 秒
- `ui/ConfirmDialog.vue` — 返回 Promise\<boolean\> 的确认弹窗。通过 `utils/dialog.ts` 的 `showConfirm()` 使用
- `ui/SeamlessScroll.vue` — 通用无缝循环滚动组件（看板类列表自动滚动复用）：内容经默认 slot 传入，组件内双份渲染 + 单步式滚动——每 `moveMs` 平滑滚一行、停 `waitMs`，合计约 2 秒一行；每次位移正好一行（整数像素，无亚像素抖动）、滚动有缓动过渡、其余时间静止，比连续匀速 CSS 动画在低端设备上更丝滑省电。Props：`moveMs`（滚一行动画时长，默认 600）、`waitMs`（到位停留时长，默认 1400）、`hover`（悬停暂停，默认 true）；自动测量内容高度/行高，**不足一屏静止不滚动**；容器高度由使用方 class 控制（如 `flex-1 min-h-0`）；**使用方需保证行高为整数**（内容行 `line-height` 用整数 px，否则位移出现亚像素抖动）；滚动内容项勿用 margin（两份内容接缝会跳变），用 padding 代替；有表头场景需把表头拆到滚动区外固定，且列宽 class 须 `th`/`td` 共用（见 `ProcessProductionCard` 的 `col-*` 用法）

**开发服务器**：
- Vite 在 `0.0.0.0:8081`
- 开发时代理 `/api/*` → `localhost:18085`
- 构建产物输出到 `web/dist/trace_app/`
- ⚠️ **`vite.config.ts` 里 `build.target` 必须是 `chrome64`，不要调高** —— 看板要在产线电视（安卓 TV，内置浏览器/WebView 内核普遍偏老）上打开，`chrome88` 产物里的 ES2020/21 语法（`??=`/`||=`/`??`）会让老内核 `SyntaxError` 直接白屏。`chrome64` 已足够低（`import.meta` 需 64+，再低要上 `@vitejs/plugin-legacy`）
- 全局 `http_base_url` 和 `websocket_base_url` 通过 Vite `define` 定义

## 开发模式

- **后端**：每个 API 组一个 handler 类，位于 `handlers/http_handler/`，在其 `urls.py` 注册。所有 handler 继承 `BaseHandler`。业务逻辑放 `service/`。
- **前端**：新 API 方法加到 `api/trace-app.ts`。新视图加到 `views/`，并在 `App.vue` 侧边栏加 `currentView` 判断。新可复用组件放 `components/`。
- **新增 MongoDB 集合**：在 `utils/db.py` 的 `db_index_map` 加索引定义；`get_collection_handler()` 首次使用会自动建集合。
- **新增 MQ 订阅**：在 `utils/mq_config.py` 的 `subscribe_key_and_process_func` 加 `"routing_key": handler_func`。
- **未配置 TypeScript 路径别名** —— `web/src/` 里用相对导入。
- **Tailwind 自定义 token** 定义在 `tailwind.config.js` —— `bg-background`、`text-accent`、`text-muted-foreground`、`border-border` 等，保持统一使用。
- **前后端联调方式**：除非明确使用外部接口（通过 `config.py` 中 `ConfigStore` 配置的外部 API 地址），否则前端调用的 API 都是本项目 server 自身的接口。因此修改功能时通常需要 **web（前端）和 server（后端）同步修改** —— 新增/修改 handler、注册路由、更新前端 API 调用。单端改动只适用于纯 UI 调整或纯后端逻辑（如 MQ 消费、定时任务）。
