# Cloud Backend 模块化重构实施方案与任务清单

> [!IMPORTANT]
> **重构最高原则：零破坏性变更**
> 1. 本地边缘端和树莓派端调用的上报接口（`POST /api/interaction-results`）及元数据 JSON（V1.1 协议）必须保持**绝对向下兼容**。
> 2. 原有的教师登录路由、管理员管理后台、以及 PostgreSQL/SQLite 双底座设计必须功能完整，重构过程中通过单元与回归脚本进行小步验证。

---

## 1. 目标目录树设计 (Target Layout)

我们将混乱的单包扁平结构，拆分为职责清晰的包结构：

```text
cloud_backend/
├── main.py                    # 主入口：只进行应用初始化、中间件挂载、组件生命周期管理与路由 include
├── config.py                  # 全局配置 settings 保持在最外层，方便根目录模块调用
├── models/                    # 【新增】数据库 ORM 模型包
│   ├── __init__.py
│   ├── base.py                # Base = declarative_base()
│   ├── user.py                # 对应 users 表
│   └── classroom.py           # 对应 teacher_classrooms, classroom_results 表
├── schemas/                   # 【新增】数据校验与序列化 Pydantic 模型包
│   ├── __init__.py
│   ├── auth.py                # 登录注册相关的 schemas
│   └── interaction.py         # 课堂交互数据 schema (兼容 v1.1 协议)
├── routers/                   # 【新增】控制器/路由包，通过 APIRouter 剥离接口
│   ├── __init__.py
│   ├── auth.py                # 权限与登录相关路由 (/api/auth/*)
│   ├── ingestion.py           # 边缘端上报路由 (/api/interaction-results/*)
│   ├── teacher.py             # 教师端页面渲染路由 (/teacher/*)
│   └── admin.py               # 管理员端页面渲染路由 (/admin/*)
│   └── dashboard.py           # 教师详情大屏路由 (/dashboard/*)
├── services/                  # 【新增】数据库与存储服务包 (仓储模式 CRUD)
│   ├── __init__.py
│   ├── base_repository.py     # repository_interface 定义
│   ├── postgres_service.py    # PostgreSQL 的增删改查实现
│   └── sqlite_service.py      # SQLite / File-based 的存储实现
├── views/                     # 【新增】前端视图与模板包
│   ├── __init__.py
│   ├── style.py               # 样式定义 (提取自 ui_style.py)
│   ├── login_templates.py     # 登录/注册 HTML
│   ├── teacher_templates.py   # 教师后台 HTML
│   ├── admin_templates.py     # 管理后台 HTML
│   └── dashboard_v11.py       # 大屏图表 HTML
└── utils/                     # 【新增】公共基础工具包
    ├── __init__.py
    ├── security.py            # 密码 Hash、JWT 校验逻辑
    └── logging_utils.py       # 日志格式化工具
```

---

## 2. 渐进式重构路线图 (Refactoring Checklist)

为了保证开发过程中服务“随时可用”，整个重构将分为 **5 个独立步骤** 进行，每一步执行完毕后必须通过静态检查与启动测试：

### 🛠️ 第一阶段：创建包骨架与迁移基础工具
*   [x] 创建新包文件夹：`models/`、`schemas/`、`routers/`、`services/`、`views/`、`utils/`，并在每个目录下创建空的 `__init__.py`。
*   [x] **迁移工具类**：
    *   将 [security.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/security.py) 移入 `utils/security.py`。
    *   将 [logging_utils.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/logging_utils.py) 移入 `utils/logging_utils.py`。
    *   修复其余文件中对应的引用路径（例如 `from .security import ...` 改为 `from .utils.security import ...`）。
*   [x] **验证**：编译并重启服务，验证基本导入未受损。

### 💾 第二阶段：数据模型层与数据校验层剥离 (Models & Schemas)
*   [x] **提取 ORM 模型**：
    *   在 `models/base.py` 中定义 SQLAlchemy 的 `Base`。
    *   在 `models/user.py` 中写入 `User` 及 `TeacherClassroom` 类（提取自 [postgres_repository.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/postgres_repository.py)）。
    *   在 `models/classroom.py` 中写入 `ClassroomResult` 模型类。
*   [x] **整合 Pydantic Schemas**：
    *   将旧版 [schemas.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/schemas.py) 和 [schemas_v11.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/schemas_v11.py) 合并进 `schemas/`。
    *   `schemas/interaction.py` 严格保持 Pydantic 模型 `InteractionResultPayload` 和 `ApiResponse` 字段一致。
*   [x] **验证**：执行 `python -m py_compile cloud_backend/models/*.py cloud_backend/schemas/*.py`。

### ⚙️ 第三阶段：存储逻辑与服务层重构 (Services / CRUD)
*   [x] 迁移 `ResultRepository` 接口类至 `services/base_repository.py`。
*   [x] 将文件系统与轻量 SQLite 的数据操作代码从 [storage.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/storage.py) 迁移至 `services/sqlite_service.py`。
*   [x] 将 PostgreSQL 数据落地与会话绑定代码从 [postgres_repository.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/postgres_repository.py) 迁移至 `services/postgres_service.py`。
*   [x] 在 `services/__init__.py` 中提供统一的工厂方法 `build_query_repository`，隐藏具体的底层数据库细节。
*   [x] **验证**：确保服务能使用 `file` 和 `postgres` 数据库模式无缝初始化。

### 🎨 第四阶段：HTML 页面与样式剥离 (Views / Templates)
*   [x] 将 [ui_style.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/ui_style.py) 迁移并改名为 `views/style.py`。
*   [x] 将 [login_pages.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/login_pages.py) 移入 `views/login_templates.py`，负责拼接生成登录及注册页的 HTML 字符串。
*   [x] 将 [teacher_pages.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/teacher_pages.py) 移入 `views/teacher_templates.py`。
*   [x] 将 [admin_pages.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/admin_pages.py) 移入 `views/admin_templates.py`。
*   [x] 将 [dashboard_v11.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/dashboard_v11.py) 移入 `views/dashboard_v11.py`。
*   [x] **验证**：检查渲染函数是否干净，无 API 或数据库会话的逻辑交叉（仅接受结构化参数，返回 HTML 字符串）。

### 🔌 第五阶段：路由分发与主入口彻底瘦身 (Routers & App Assembly)
*   [x] **路由拆解**：
    *   在 `routers/auth.py` 中挂载原 [auth.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/auth.py) 拆解出的登录、退出、`/api/auth/me` 等 API 路由。
    *   在 `routers/ingestion.py` 中引入上报接收路由（`POST /api/interaction-results` 等）。
    *   在 `routers/teacher.py`、`routers/admin.py` 中分别引入教师端、管理员端的页面访问路由，调用 `views/` 包下的 HTML 生成器。
*   [x] **瘦身 main.py**：
    *   清空 [main.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/main.py) 中的冗余业务逻辑。
    *   在 [main.py](file:///D:/Codes/Python/Assitant/class-assitant-robot/cloud_backend/main.py) 中通过 `app.include_router()` 包含所有新挂载的子路由。
*   [x] **验证**：完全重启服务，并在本地运行所有 API 和页面验证。

---

## 3. 回归测试与验证矩阵 (Verification Scripts)

每一步重构均可调用项目现有的验证脚本。以下是关键验证映射，重构结束后必须保证所有输出为 `true`：

*   **身份验证与角色路由回归**：
    ```bash
    API_BASE_URL="http://127.0.0.1:8011" RESULT_ID="cls_20260417_101_001" CLASSROOM_ID="classroom_101" bash scripts/validate_phase2_9_auth.sh
    ```
*   **大屏数据与显示边界回归**：
    ```bash
    API_BASE_URL="http://127.0.0.1:8011" bash scripts/validate_phase3_8_dashboard_display_scope.sh
    ```
*   **Trend Insights 移除逻辑回归**：
    ```bash
    API_BASE_URL="http://127.0.0.1:8011" bash scripts/validate_phase3_19_remove_trend_insights.sh
    ```
