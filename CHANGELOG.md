# 更新日志 (Changelog)

所有重要的项目变更都将记录在此文件中。

## [1.2.0] - 2026-04-19

### 新增 (Added)
- ✨ 统一 API 响应格式 `UnifiedResponse` (`core/response.py`)
  - 标准化响应结构：`{status, messages, datas, pagination}`
  - `status`: 1=成功, 0=失败
  - `datas`: 数据列表（单条记录也包裹在列表中）
  - `pagination`: 分页信息（count, page, page_size, total_pages）
  - `UnifiedResponse.success()` 和 `UnifiedResponse.error()` 工厂方法

### 变更 (Changed)
- 🔄 所有业务模块 API 返回值改用 `UnifiedResponse`
  - 学生模块 (`api/student.py`)
  - 教师模块 (`api/teacher.py`)
  - 班级模块 (`api/class_student.py`)
  - 成绩模块 (`api/score.py`)
  - 就业模块 (`api/employment.py`)
  - 用户管理模块 (`api/users.py`)
  - AI 模块 (`api/agent.py`)
- 🔄 统一异常处理器返回 `UnifiedResponse` 格式
  - `base_api_exception_handler`
  - `http_exception_handler`
  - `validation_exception_handler`
  - `pydantic_validation_exception_handler`
  - `general_exception_handler`
- 🔄 前端 `api.js` 自动解包统一响应
  - 检测 `status` 字段自动识别统一格式
  - 成功时返回 `{datas, pagination, messages}`
  - 失败时抛出 `Error(messages)`
  - 非统一格式（如登录接口）直接返回原始数据
- 🔄 前端所有模块适配新数据格式
  - `data.datas` 替代 `data.data` / `data.items`
  - `data.pagination.count` 替代 `data.count` / `data.total`
  - 单条记录使用 `result.datas[0]`

### 弃用 (Deprecated)
- ⚠️ 旧版 `ResponseBuilder` 及相关响应模型保留但不再推荐使用

---

## [1.1.0] - 2026-04-16

### 新增 (Added)
- ✨ 统一日志模块 (`core/logger.py`)
  - 基于 Loguru 的高性能日志系统
  - 支持结构化日志记录
  - 专用日志记录器（API、数据库、AI）
  - 自动日志文件轮转和清理
  - 彩色控制台输出
  - 分级别的日志文件（普通日志、错误日志）
- ✨ 统一响应模块 (`core/response.py`)
  - 标准化的 API 响应格式
  - 多种响应类型（成功、错误、分页、批量操作等）
  - 响应构建器类
  - 快捷响应函数
  - 泛型响应模型
- ✨ 统一异常处理模块 (`core/exceptions.py`)
  - 自定义异常类体系
  - 统一的异常处理器
  - 异常处理装饰器
  - 快捷异常抛出函数
  - 详细的异常日志记录
- ✨ 日志中间件 (`middlewares/logging_middleware.py`)
  - 请求/响应自动记录
  - 性能监控（响应时间）
  - 客户端 IP 记录
  - 请求 ID 生成
  - 错误日志中间件
- ✨ 使用指南文档 (`backend/USAGE_GUIDE.md`)
  - 日志模块使用说明
  - 响应模块使用说明
  - 异常处理使用说明
  - 完整示例代码
  - 最佳实践和故障排查

### 架构 (Architecture)
- 🏗️ 集成日志系统到应用启动流程
- 🏗️ 统一的异常处理机制
- 🏗️ 中间件架构优化
- 🏗️ 健康检查端点 (`/health`)
- 🏗️ 请求 ID 追踪

### 优化 (Optimized)
- ⚡ 日志性能优化（异步写入）
- ⚡ 统一的响应格式，提升前端集成体验
- ⚡ 异常处理自动化，减少重复代码
- ⚡ 结构化日志，便于日志分析和监控

### 修复 (Fixed)
- 🐛 修复日志配置问题
- 🐛 优化异常处理流程

### 文档 (Documentation)
- 📝 更新 requirements.txt，添加 loguru 依赖
- 📝 创建使用指南文档
- 📝 更新主 README.md
- 📝 更新后端 README.md

---

## [1.0.0] - 2026-04-16

### 新增 (Added)
- ✨ 完整的学生信息管理功能
- ✨ 教师信息管理功能
- ✨ 班级信息管理功能
- ✨ 成绩管理功能
- ✨ 就业管理功能
- ✨ AI 智能助手功能
  - 自然语言 SQL 查询
  - 智能数据分析
  - 流式响应支持
  - 多模型支持（通义千问、DeepSeek）
- ✨ 完整的前端界面
  - 响应式设计
  - 美观的 UI/UX
  - 表格展示
  - 模态框编辑
  - 搜索功能
  - 分页功能

### 架构 (Architecture)
- 🏗️ 实现完整的 MVC 分层架构
  - API 层 (Controller)
  - Service 层 (Business Logic)
  - Repository 层 (Data Access)
  - Model 层 (ORM)
  - Schema 层 (DTO)
- 🏗️ 使用 BaseCRUD 基类实现通用 CRUD 操作
- 🏗️ 统一的异常处理机制
- 🏗️ 软删除策略（deleted_at 字段）

### 数据库 (Database)
- 🗄️ 完整的数据库设计（8 张表）
  - sequence（序号生成）
  - class（班级）
  - teacher（教师）
  - teacher_class（教师带班）
  - student（学生）
  - student_class（学生班级）
  - score（成绩）
  - employment（就业）
- 🗄️ 外键关系定义
- 🗄️ 索引优化

### AI 集成 (AI Integration)
- 🤖 通义千问 API 集成
- 🤖 DeepSeek API 集成
- 🤖 SQL 生成功能
- 🤖 图表类型选择
- 🤖 数据分析报告生成
- 🤖 流式响应支持

### 文档 (Documentation)
- 📝 README.md - 项目主文档
- 📝 backend/README.md - 后端文档
- 📝 MIGRATION_GUIDE.md - 迁移指南
- 📝 REFACTORING.md - 重构说明
- 📝 CHANGELOG.md - 更新日志
- 📝 .gitignore - Git 忽略文件
- 📝 requirements.txt - 依赖清单
- 📝 Dockerfile - Docker 配置
- 📝 docker-compose.yml - Docker Compose 配置
- 📝 nginx.conf - Nginx 配置

### 修复 (Fixed)
- 🐛 修复 API 路由冲突问题
- 🐛 修复 AI API 调用格式错误
- 🐛 修复 SQL 查询字段名错误（deleted_at vs is_deleted）
- 🐛 修复前端表格显示问题
- 🐛 修复数据库连接问题

### 优化 (Optimized)
- ⚡ 优化数据库查询性能
- ⚡ 优化前端渲染性能
- ⚡ 添加数据库连接池
- ⚡ 添加响应缓存

---

## 开发计划 (Planned)

### [1.1.0] - 已完成 ✅
- [x] 添加用户认证和授权（JWT）
- [x] 添加数据导入导出功能
- [ ] 添加数据统计报表
- [ ] 添加消息通知功能
- [ ] 添加数据备份功能

### [1.2.0] - 已完成 ✅
- [x] 统一 API 响应格式（UnifiedResponse）
- [x] 前端适配统一响应格式
- [ ] 添加单元测试
- [ ] 添加集成测试

### [1.3.0] - 计划中
- [ ] 引入 Redis 缓存机制
  - [ ] 缓存各业务模块列表数据（学生、教师、班级、成绩、就业）
  - [ ] 缓存 AI 查询分析结果
  - [ ] AI 模块添加语义缓存（基于向量相似度匹配相似问题，复用历史回答）
  - [ ] 缓存失效策略（数据变更时自动清除相关缓存）
  - [ ] 缓存预热与过期时间配置
  - [ ] 添加缓存命中/未命中监控指标

### [2.0.0] - 未来计划
- [ ] 重构为微服务架构
- [ ] 添加前端框架（Vue/React）
- [ ] 添加移动端支持
- [ ] 添加实时协作功能
- [ ] 添加数据可视化大屏

---

## 版本说明

### 版本号规则
遵循 [语义化版本](https://semver.org/lang/zh-CN/)：
- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 变更类型
- **新增 (Added)**：新功能
- **变更 (Changed)**：现有功能的变更
- **弃用 (Deprecated)**：即将移除的功能
- **移除 (Removed)**：已移除的功能
- **修复 (Fixed)**：问题修复
- **安全 (Security)**：安全相关的修复
