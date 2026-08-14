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
- `App.vue` — 根布局：侧边栏导航 + 主内容区。侧边栏切换 `currentView` ref；`currentView` 用 `sessionStorage` 持久化，刷新页面保持当前页
- `views/HomeView.vue` — 首页仪表盘，展示服务状态和 API 端点列表
- `views/HistoryView.vue` — 历史记录页面（开发中）
- `views/dashboard/` — 智能生产看板；`DashboardView.vue` 只做布局 + 状态管理（WebSocket 连接、从看板配置读取查询日期/产线），各卡片拆在 `views/dashboard/components/`：`HeaderBar`（顶栏）、`OeeCard`（OEE 仪表盘）、`DeviceStatusCard`（产线设备实时状态）、`PlanActualOutputCard`（计划/实际产量，预留）、`ProcessQualifiedRateCard`（工序合格率，WebSocket 实时）、`HourlyOutputCard`（小时产量统计，WebSocket 实时柱状图）、`HistoryDataCard`（历史数据，预留）。看板标题 / 查询日期 / 产线 / 产品型号（数据源 `production_config_type` 表）等配置在 `views/dashboard/DashboardSettingsView.vue`（智能看板设置）维护，看板加载时经 `getDashboardConfig` 一并获取并应用。科技主题共用样式集中在 `views/dashboard/dashboard.theme.css`（`tech-panel` 四角括号面板 / `tech-panel-title` / `tech-badge` / `chart-card-placeholder` 预留占位 / 全局动画 keyframes），由 `DashboardView.vue` 引入，看板内组件共用
- `composables/useServiceStatus.ts` — 共享服务状态 composable，模块级单例，自动检测后端健康状态
- `api/trace-app.ts` — API 方法，使用 `httpWrap.ts` 的 `_get`/`_post`
- `api/httpWrap.ts` — Axios 实例，带登录跳转拦截器、base URL 自动识别（开发 vs 部署），定义了 `ApiResponse<T>` 统一响应类型

**可复用 UI 组件**：
- `CleanTable.vue` — 表格，支持全选 checkbox、slot 单元格定制、空状态、双击事件。Props：`data`、`columns`、`selectable`
- `CustomSelect.vue` — 下拉框，实心/描边两种样式，点击外部关闭，禁用状态。v-model 兼容
- `ui/Toast.vue` — 自动消失的通知（成功/错误/警告/信息），默认 3 秒
- `ui/ConfirmDialog.vue` — 返回 Promise\<boolean\> 的确认弹窗。通过 `utils/dialog.ts` 的 `showConfirm()` 使用

**开发服务器**：
- Vite 在 `0.0.0.0:8081`
- 开发时代理 `/api/*` → `localhost:18085`
- 构建产物输出到 `web/dist/trace_app/`
- 全局 `http_base_url` 和 `websocket_base_url` 通过 Vite `define` 定义

## 开发模式

- **后端**：每个 API 组一个 handler 类，位于 `handlers/http_handler/`，在其 `urls.py` 注册。所有 handler 继承 `BaseHandler`。业务逻辑放 `service/`。
- **前端**：新 API 方法加到 `api/trace-app.ts`。新视图加到 `views/`，并在 `App.vue` 侧边栏加 `currentView` 判断。新可复用组件放 `components/`。
- **新增 MongoDB 集合**：在 `utils/db.py` 的 `db_index_map` 加索引定义；`get_collection_handler()` 首次使用会自动建集合。
- **新增 MQ 订阅**：在 `utils/mq_config.py` 的 `subscribe_key_and_process_func` 加 `"routing_key": handler_func`。
- **未配置 TypeScript 路径别名** —— `web/src/` 里用相对导入。
- **Tailwind 自定义 token** 定义在 `tailwind.config.js` —— `bg-background`、`text-accent`、`text-muted-foreground`、`border-border` 等，保持统一使用。
- **前后端联调方式**：除非明确使用外部接口（通过 `config.py` 中 `ConfigStore` 配置的外部 API 地址），否则前端调用的 API 都是本项目 server 自身的接口。因此修改功能时通常需要 **web（前端）和 server（后端）同步修改** —— 新增/修改 handler、注册路由、更新前端 API 调用。单端改动只适用于纯 UI 调整或纯后端逻辑（如 MQ 消费、定时任务）。
