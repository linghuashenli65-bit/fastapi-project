# 学生管理系统

一个基于 FastAPI 和原生 JavaScript 的学生信息管理系统，集成了 AI 智能分析和用户认证功能。

## 功能特性

### 核心功能
- 🎓 **学生管理**：学生信息的增删改查
- 👨‍🏫 **教师管理**：教师信息和带班管理
- 🏫 **班级管理**：班级信息和课程安排
- 📊 **成绩管理**：学生考核成绩记录和统计
- 💼 **就业管理**：学生就业信息和 Offer 记录
- 🤖 **AI 智能助手**：自然语言查询和数据分析
- 🔐 **用户认证**：基于 fastapi-users 的 JWT 认证系统
- 👥 **用户管理**：管理员可对所有用户进行增删改查

### AI 功能
- 💬 **自然语言 SQL 查询**：用自然语言描述查询，自动生成 SQL 并执行
- 📈 **智能数据分析**：自动生成图表和分析报告
- 🎯 **多模型支持**：支持通义千问 (Qwen) 和 DeepSeek
- 🔄 **流式响应**：实时显示分析进度和结果

### 用户认证与管理
- 🔑 **JWT 认证**：基于 Token 的用户登录/注册
- 🛡️ **角色权限**：区分普通用户和管理员
- 👤 **用户信息**：用户名、姓名、手机号等扩展字段
- 📋 **用户管理**：管理员可查看、新增、编辑、删除用户
- 🔒 **安全防护**：密码哈希存储、Token 过期机制

## 技术栈

### 后端
- **框架**：FastAPI
- **认证**：fastapi-users (JWT)
- **数据库**：MySQL
- **ORM**：SQLAlchemy (Async)
- **AI 集成**：
  - 通义千问 API (Qwen)
  - DeepSeek API
- **架构**：MVC 分层架构

### 前端
- **框架**：原生 JavaScript (ES6+)
- **图表库**：ECharts
- **样式**：自定义 CSS

## 项目结构

```
python项目/
├── backend/                    # 后端项目
│   ├── app/                   # 应用入口
│   │   └── main.py           # FastAPI 主应用
│   ├── api/                   # API 路由层
│   │   ├── agent.py          # AI 模块 API
│   │   ├── auth.py           # 认证路由 (fastapi-users)
│   │   ├── class_student.py  # 班级模块 API
│   │   ├── employment.py     # 就业模块 API
│   │   ├── score.py          # 成绩模块 API
│   │   ├── student.py        # 学生模块 API
│   │   ├── teacher.py        # 教师模块 API
│   │   └── users.py          # 用户管理 API (管理员)
│   ├── core/                 # 核心配置
│   │   ├── auth.py           # 认证配置 (JWT, fastapi-users)
│   │   ├── config.py         # 应用配置
│   │   └── database.py       # 数据库配置
│   ├── models/               # 数据模型层
│   │   ├── agent.py         # AI 相关模型
│   │   ├── class_.py        # 班级模型
│   │   ├── dashboard.py      # 仪表板模型
│   │   ├── employment.py     # 就业模型
│   │   ├── llm.py           # LLM 接口
│   │   ├── score.py         # 成绩模型
│   │   ├── student.py       # 学生模型
│   │   ├── teacher.py       # 教师模型
│   │   └── user.py          # 用户模型 (fastapi-users)
│   ├── repositories/         # 数据访问层
│   ├── schemas/             # 数据传输对象
│   ├── services/            # 业务逻辑层
│   ├── static/             # 静态文件
│   │   ├── index.html      # 主页面
│   │   ├── login.html      # 登录页面
│   │   ├── register.html   # 注册页面
│   │   ├── style.css       # 样式文件
│   │   └── js/            # JavaScript 文件
│   │       ├── api.js      # API 调用 (含 Token 认证)
│   │       ├── app.js      # 应用主逻辑
│   │       ├── config.js   # 配置
│   │       ├── login.js    # 登录逻辑
│   │       ├── register.js # 注册逻辑
│   │       ├── utils.js    # 工具函数
│   │       └── modules/    # 功能模块
│   │           ├── ai.js
│   │           ├── class.js
│   │           ├── employment.js
│   │           ├── score.js
│   │           ├── student.js
│   │           ├── teacher.js
│   │           └── userAdmin.js  # 用户管理模块
│   ├── tests/              # 测试
│   │   └── test_users.py   # 用户模块测试
│   └── middlewares/        # 中间件
│       └── logging_middleware.py
├── frontend/              # 前端项目（预留）
├── .env                 # 环境变量
├── init.sql             # 数据库初始化脚本
└── README.md            # 项目说明
```

## 快速开始

### 环境要求
- Python 3.8+
- MySQL 5.7+
- npm (可选，用于前端开发)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd python项目
```

2. **安装依赖**
```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

3. **配置数据库**
- 创建 MySQL 数据库：`student_management_system`
- 创建 users 表（参考上方 users 表结构）
- 修改 `.env` 文件中的数据库连接信息

4. **创建管理员账户**
- 先通过注册页面创建账户
- 然后在数据库中将用户设为管理员：
```sql
UPDATE users SET is_superuser = 1 WHERE id = 1;
```

4. **配置 AI API**
- 在 `backend/core/config.py` 中配置通义千问和 DeepSeek 的 API 密钥
- 获取 API 密钥：
  - 通义千问：https://dashscope.aliyun.com/
  - DeepSeek：https://platform.deepseek.com/

5. **启动服务器**
```bash
# 开发环境
python backend/app/main.py

# 或使用 uvicorn
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **访问应用**
- 打开浏览器访问：http://localhost:8000 （登录页面）
- 主页面：http://localhost:8000/static/index.html
- API 文档：http://localhost:8000/docs

## 数据库设计

### 核心表结构
- **users**：用户信息表（邮箱、密码、角色、扩展字段等）
- **sequence**：序号生成辅助表
- **class**：班级信息表
- **teacher**：教师信息表
- **teacher_class**：教师带班历史表
- **student**：学生基本信息表
- **student_class**：学生班级归属历史表
- **score**：学生考核成绩表
- **employment**：学生就业信息表

详细的表结构请参考 `backend/models/` 目录下的模型文件。

### users 表结构
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| email | VARCHAR(320) | 邮箱，唯一 |
| hashed_password | VARCHAR(1024) | 哈希密码 |
| is_active | BOOLEAN | 是否启用 |
| is_superuser | BOOLEAN | 是否管理员 |
| is_verified | BOOLEAN | 是否已验证 |
| username | VARCHAR(50) | 用户名 |
| full_name | VARCHAR(100) | 姓名 |
| phone | VARCHAR(20) | 手机号 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| deleted_at | DATETIME | 删除时间 |

## API 文档

### 核心接口

#### 认证模块
- `POST /auth/jwt/login` - 用户登录
- `POST /auth/jwt/logout` - 用户登出
- `POST /auth/register` - 用户注册
- `POST /auth/forgot-password` - 忘记密码
- `POST /auth/reset-password` - 重置密码

#### 用户模块
- `GET /users/me` - 获取当前用户信息
- `PATCH /users/me` - 更新当前用户信息

#### 用户管理（管理员）
- `GET /admin/users` - 获取所有用户列表
- `POST /admin/users` - 创建新用户
- `GET /admin/users/{id}` - 获取指定用户
- `PUT /admin/users/{id}` - 更新用户信息
- `DELETE /admin/users/{id}` - 删除用户

#### 学生模块
- `GET /api/v1/student/` - 获取学生列表
- `POST /api/v1/student/` - 创建学生
- `GET /api/v1/student/{id}` - 获取学生详情
- `PUT /api/v1/student/{id}` - 更新学生
- `DELETE /api/v1/student/{id}` - 删除学生

#### 班级模块
- `GET /api/v1/class/` - 获取班级列表
- `POST /api/v1/class/` - 创建班级
- `GET /api/v1/class/{id}` - 获取班级详情
- `PUT /api/v1/class/{id}` - 更新班级
- `DELETE /api/v1/class/{id}` - 删除班级

#### 教师模块
- `GET /api/v1/teacher/` - 获取教师列表
- `POST /api/v1/teacher/` - 创建教师
- `GET /api/v1/teacher/{id}` - 获取教师详情
- `PUT /api/v1/teacher/{id}` - 更新教师
- `DELETE /api/v1/teacher/{id}` - 删除教师

#### 成绩模块
- `GET /api/v1/score/` - 获取成绩列表
- `POST /api/v1/score/` - 创建成绩
- `GET /api/v1/score/student/{student_no}` - 按学号查询成绩
- `GET /api/v1/score/class/{class_no}` - 按班级查询成绩

#### 就业模块
- `GET /api/v1/employment/` - 获取就业列表
- `POST /api/v1/employment/` - 创建就业记录
- `GET /api/v1/employment/{id}` - 获取就业详情
- `PUT /api/v1/employment/{id}` - 更新就业记录
- `DELETE /api/v1/employment/{id}` - 删除就业记录

#### AI 模块
- `POST /agent/sql` - AI SQL 查询
- `POST /agent/dashboard` - AI 数据分析（流式）

### 完整 API 文档
启动服务器后访问 http://localhost:8000/docs 查看完整的交互式 API 文档。

## 开发指南

### 架构说明

本项目采用 MVC 分层架构：

- **API 层** (`api/`)：处理 HTTP 请求和响应
- **Service 层** (`services/`)：业务逻辑处理
- **Repository 层** (`repositories/`)：数据访问
- **Model 层** (`models/`)：数据库模型
- **Schema 层** (`schemas/`)：数据传输对象

### 添加新功能

1. **定义 Model**：在 `models/` 目录创建数据模型
2. **定义 Schema**：在 `schemas/` 目录创建 DTO
3. **创建 Repository**：在 `repositories/` 目录创建数据访问层
4. **创建 Service**：在 `services/` 目录创建业务逻辑层
5. **创建 API**：在 `api/` 目录创建 API 路由
6. **注册路由**：在 `app/main.py` 中注册路由

详细开发指南请参考 `backend/MIGRATION_GUIDE.md` 和 `backend/REFACTORING.md`。

## 部署指南

### 生产环境部署

1. **使用 Gunicorn**
```bash
pip install gunicorn
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **使用 Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "backend.app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

3. **环境变量配置**
创建 `.env` 文件并配置以下变量：
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=student_management_system
```

## 常见问题

### 1. 数据库连接失败
- 检查 MySQL 服务是否启动
- 检查 `.env` 文件中的数据库配置
- 确保数据库已创建
- 确保 users 表已创建且字段与模型一致

### 2. AI API 调用失败
- 检查 API 密钥是否正确配置
- 检查网络连接
- 查看 API 配额是否充足

### 3. 前端页面无法访问
- 确保后端服务已启动
- 检查静态文件路径配置
- 查看浏览器控制台错误信息

### 4. 登录后看不到用户管理菜单
- 确认当前用户已设为管理员（`is_superuser = 1`）
- 重新登录以刷新 Token 和用户信息

### 5. 用户管理接口返回 403
- 确认请求头包含有效的 Authorization Token
- 确认当前用户 `is_superuser` 为 True

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请提交 Issue 或联系项目维护者。

## 更新日志

### v1.1.0 (2026-04-17)
- ✅ 集成 fastapi-users 用户认证系统
- ✅ 实现登录/注册页面
- ✅ JWT Token 认证机制
- ✅ 管理员用户管理功能（增删改查）
- ✅ 前端登录状态检测和权限控制
- ✅ 用户模块单元测试（9个测试全部通过）

### v1.0.0 (2026-04-16)
- ✅ 完成核心 CRUD 功能
- ✅ 集成 AI 智能助手
- ✅ 实现 MVC 分层架构
- ✅ 添加成绩管理模块
- ✅ 优化前端 UI/UX
