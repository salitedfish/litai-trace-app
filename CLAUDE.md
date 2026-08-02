# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MES 手动产线追溯微应用 — a manufacturing execution system traceability micro-application.

- **Backend**: Python 3.6+ / Tornado via `mg_app_framework` + MongoDB (Motor) + RabbitMQ
- **Frontend**: Vue 3 + TypeScript + Vite 8 + Tailwind CSS 3
- **No tests exist yet** — this is an early-stage project

## Key Commands

### Backend

```bash
# Install deps (requires mg_app_framework*.whl in server/lib/)
cd server
python -m pip install -r lib/requirements.txt

# Start dev server on :18085 (hot-reload enabled)
cd src
python run_trace_app.py

# Production start
python run_trace_app.py product

# Swagger docs at http://localhost:18085/trace_app/docs
```

### Frontend

```bash
cd web
npm install
npm run dev      # Dev server on :8081, proxies /api → :18085
npm run build    # Production build → web/dist/trace_app/
npm run preview  # Preview production build
```

### Packaging & Deployment

```bash
bash release/package.sh                    # Package into tarball (original)
release\package_smart_auto.bat             # 自动化打包（无 pause，报错直接退出）
release\package_smart_manu.bat             # 手动打包（有 pause，按键继续）
server/bin/install.sh                      # Install as systemd service
server/bin/run.sh {start|stop|status|debug} # Service management
```

## Architecture

### Backend (`server/src/trace_app/`)

The app uses `mg_app_framework` — a Tornado-based microservice framework with opinionated startup wiring:

**Startup flow** (`start.py` → `run_trace_app.py`):
1. `ConfigStore` is set as the global store (port 18085, app name "追溯应用")
2. MongoDB connection is initialized via `MongodbConfig` (host: `192.168.130.252:27017`)
3. RabbitMQ connection is initialized via `RabbitMQConfig` (host: `192.168.130.252:5672`)
4. `MyInitFunc` runs on startup to create MongoDB indexes defined in `db_index_map`
5. `app_start(debug_flag)` starts the Tornado IOLoop with hot-reload in dev mode
6. HTTP API docs are available at `/swagger/` via `tornado_swagger`

**Request flow**:
- HTTP: Incoming → `tornado_request_mapping` Route → `@request_mapping` decorator on handler methods → `BaseHandler` (CORS, JSON serialization, unified response) → Response entity
- WebSocket: `websocket_handler/handler.py` → WebHandler on `/websocket_url`
- Handlers use `BaseHandler.send_response(Response.success(data, info))` — never raw `write()`
- `BaseHandler` extends `HttpBasicHandler` (from mg_app_framework) and adds CORS headers, unified error handling, and a `write_error` override that returns `{code, data, info}` on 500

**Handler registration** (`handlers/http_handler/urls.py`):
- Uses `tornado_request_mapping.Route` pattern: create a `Route()`, register handler classes with `.register()`, extend the `url` list
- Add new handlers by creating a class with `@request_mapping(path)` decorator and registering it in `urls.py`
- 所有 Handler 需要用 `generate_handler_classes()` 生成动态子类并注册，否则 Swagger 文档无法自动生成。参考 `handlers/http_handler/urls.py` 中的模式。

**Database** (`utils/db.py`):
- `get_db_handler(db_name=None)` → returns a Motor database handle (defaults to `{organization}_trace_app`)
- `get_collection_handler(name)` → auto-creates collections and their indexes on first access
- Add new collection indexes in the `db_index_map` dict at the top of `db.py`; they get created on app startup via `MyInitFunc`
- 详细的数据库结构（集合、字段、索引等）记录在 `server/database_structure.md`，需要时读取该文件

**Message queue** (`utils/mq_config.py`):
- `subscribe_key_and_process_func` dict maps MQ routing keys to async handler functions
- `process_mq_msg` dispatches incoming messages to the registered handler
- `send_rabbit_mq(data, key)` publishes messages
- `time_interval_status` is subscribed for real-time device status (pushed by `device_exception_compute`, value is a status code). `service/device_status_service.py` keeps an in-memory `{device_code: status_code}` map (4/5/6 → 2; only 0 off / 1 running / 2 standby / 3 fault), pre-filled from the `device_exception_status_interval` collection at startup (`my_init_func`), and pushed to clients over WebSocket `/ws/device_status` (5s snapshot) via `DeviceStatusProvider`.

**Utils**:
- `utils.py` — QR code generation (qrcode + reportlab), serial ID generation (MES+YYMMDD+NNNNNNN) using MongoDB atomic counters
- `request_utils.py` — async HTTP client wrapper (send_url_request / send_in_url_request) via Tornado's AsyncHTTPClient
- `datetime_utils.py` — ISO 8601 datetime parsing (compatible with Python 3.6), timezone handling
- `string_utils.py` — `StringUtils.is_empty(s)` / `is_empty_or(*args)`
- `swagger_utils.py` — Swagger 文档生成工具，提供 `@swagger_doc` 装饰器（支持 TypedDict 模型自动转 schema）和 `generate_handler_classes()`（为每个 API 方法生成动态 Handler 子类）

**Response pattern** (`entity/response_entity.py` → `common/response_entity.py`):
- `Response.success(data, info)` / `Response.fail(info, data)` — returns unified `{code, data, info}` objects
- The entity package re-exports from common; use `Response.success()` / `Response.fail()` everywhere
- `DefaultEncoder` (JSON) handles `datetime`, `ObjectId`, `Decimal` serialization

### Frontend (`web/src/`)

**Structure**:
- `main.ts` — Vue 3 app entry, no router (single-view app with manual `currentView` state)
- `App.vue` — Root layout with sidebar nav + main content area. Sidebar toggles `currentView` ref
- `views/HomeView.vue` — Dashboard showing service status and API endpoint list
- `views/HistoryView.vue` — 历史记录页面（开发中）
- `views/dashboard/` — 智能生产看板；`DashboardView.vue` 只做布局 + 状态管理（WebSocket 连接、产线/日期选择），各卡片拆在 `views/dashboard/components/`：`HeaderBar`（顶栏）、`OeeCard`（OEE 仪表盘）、`DeviceStatusCard`（产线设备实时状态）、`ProductionTrendCard`（近7日产量）、`FilterModal`（操作弹窗）
- `composables/useServiceStatus.ts` — 共享服务状态 composable，模块级单例，自动检测后端健康状态
- `api/trace-app.ts` — API methods using `_get`/`_post` from `httpWrap.ts`
- `api/httpWrap.ts` — Axios instance with login redirect interceptor, base URL auto-detection (dev vs deployment), 定义了 `ApiResponse<T>` 统一响应类型

**Reusable UI components**:
- `CleanTable.vue` — Table with select-all checkbox, slot-based cell customization, empty state, double-click emit. Props: `data`, `columns`, `selectable`
- `CustomSelect.vue` — Dropdown with solid/outline variants, click-outside close, disabled state. v-model compatible
- `ui/Toast.vue` — Auto-dismissing notification (success/error/warning/info), 3s default duration
- `ui/ConfirmDialog.vue` — Modal confirm dialog returning Promise\<boolean\>. Used via `showConfirm()` in `utils/dialog.ts`

**Dev server**:
- Vite on `0.0.0.0:8081`
- Proxies `/api/*` → `localhost:18085` during development
- Build output goes to `web/dist/trace_app/`
- Global `http_base_url` and `websocket_base_url` defined via Vite `define`

## Development Patterns

- **Backend**: One handler class per API group at `handlers/http_handler/`, registered in its `urls.py`. All handlers extend `BaseHandler`. Business logic goes in `service/`.
- **Frontend**: New API methods go in `api/trace-app.ts`. New views go in `views/`, add a `currentView` check in `App.vue` sidebar. New reusable components in `components/`.
- **Adding a MongoDB collection**: Add its index definition to `db_index_map` in `utils/db.py`; let `get_collection_handler()` auto-create it at first use.
- **Adding MQ subscription**: Add `"routing_key": handler_func` to `subscribe_key_and_process_func` in `utils/mq_config.py`.
- **No TypeScript path aliases** configured — use relative imports in `web/src/`.
- **Tailwind custom tokens** defined in `tailwind.config.js` — `bg-background`, `text-accent`, `text-muted-foreground`, `border-border`, etc. Use these consistently.
- **前后端联调方式**：除非明确使用外部接口（通过 `config.py` 中 `ConfigStore` 配置的外部 API 地址），否则前端调用的 API 都是本项目 server 自身的接口。因此修改功能时通常需要 **web（前端）和 server（后端）同步修改** — 新增/修改 handler、注册路由、更新前端 API 调用。单端改动只适用于纯 UI 调整或纯后端逻辑（如 MQ 消费、定时任务）。
