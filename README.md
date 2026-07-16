# 追溯应用 (Trace App)

MES 手动产线追溯微应用，基于 `mg_app_framework` 构建。

## 技术栈

- **后端**: Python 3.6 + Tornado (mg_app_framework) + MongoDB + RabbitMQ
- **前端**: Vue 3 + TypeScript + Vite 8 + Tailwind CSS
- **部署**: systemd / virtualenv

## 目录结构

```
trace_app/
├── .gitignore
├── README.md
├── release/              # 打包脚本
├── server/               # Python 后端
│   ├── bin/              # install/run 脚本
│   ├── lib/              # 依赖 (mg_app_framework*.whl + requirements.txt)
│   ├── log/              # 运行时日志
│   └── src/              # Python 源码
│       ├── run_trace_app.py           # 入口文件
│       └── trace_app/                 # 业务模块
│           ├── start.py               # 启动初始化
│           ├── config.py              # 开发配置 (端口 18085)
│           ├── config_product.py      # 生产配置 (端口 18085)
│           ├── my_init_func.py        # 启动时索引初始化
│           ├── common/                # 框架基类 (BaseHandler, Response, Encoder)
│           ├── entity/                # 请求/响应模型 (TypedDict)
│           ├── handlers/              # HTTP + WebSocket 处理器
│           │   └── http_handler/      # REST API 端点
│           ├── service/               # 业务逻辑层
│           └── utils/                 # 工具类 (DB, MQ, HTTP, Swagger)
└── web/                   # Vue 3 前端
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── main.ts
        ├── App.vue
        ├── api/          # HTTP 请求封装
        ├── views/        # 页面组件
        └── utils/        # 前端工具
    ├── bin/              # install/run 脚本
    ├── lib/              # 依赖 (mg_app_framework*.whl + requirements.txt)
    ├── log/              # 运行时日志
    └── src/
        ├── run_trace_app.py           # 入口文件
        └── trace_app/                 # 业务模块
            ├── start.py               # 启动初始化
            ├── config.py              # 开发配置 (端口 18085)
            ├── config_product.py      # 生产配置 (端口 18085)
            ├── my_init_func.py        # 启动时索引初始化
            ├── common/                # 框架基类 (BaseHandler, Response, Encoder)
            ├── entity/                # 请求/响应模型 (TypedDict)
            ├── handlers/              # HTTP + WebSocket 处理器
            │   └── http_handler/      # REST API 端点
            ├── service/               # 业务逻辑层
            └── utils/                 # 工具类 (DB, MQ, HTTP, Swagger)
```

## 开发

### 后端

```bash
# 1. 将 mg_app_framework*.whl 放入 server/lib/
# 2. 安装依赖
cd server
python -m pip install -r lib/requirements.txt

# 3. 启动调试模式 (热重载)
cd src
python run_trace_app.py

# 4. 访问 Swagger 文档
# http://localhost:18085/swagger/
```

### 前端

```bash
cd web
npm install
npm run dev        # 开发服务器 (端口 8081, 代理 /api → :18085)
npm run build      # 生产构建
```

## 打包部署

```bash
bash release/package.sh
```

打包后执行 `server/bin/install.sh` 安装为 systemd 服务，通过 `server/bin/run.sh {start|stop|status|debug}` 管理。
