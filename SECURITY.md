# 安全配置指南

本文档说明如何安全地配置项目中的敏感信息。

## 概述

本项目已经移除所有硬编码的敏感信息（API密钥、数据库密码等），改用环境变量进行配置。

## 配置文件

### 1. `.env` 文件

`.env` 文件用于存储项目所有的环境变量配置。**该文件已被添加到 `.gitignore`，不会被提交到版本控制系统。**

### 2. `.env.example` 文件

`.env.example` 文件是环境变量的模板，包含了所有需要配置的变量及其说明。新用户可以复制该文件并重命名为 `.env`，然后填写实际的配置值。

```bash
cp .env.example .env
```

## 配置项说明

### 数据库配置

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_database_password_here
DB_NAME=student_management_system
```

### JWT 配置

生成强密钥（推荐使用 openssl）：

```bash
openssl rand -hex 32
```

配置到环境变量：

```env
SECRET_KEY=12060e1c8d65abda107a41ac545d075dd124825395065bc96cc7404dcd0861b9
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 大模型 API 配置

项目支持以下大模型API：

1. **通义千问 (Qwen)**
   ```env
   QWEN_API_KEY=your_qwen_api_key_here
   ```

2. **DeepSeek**
   ```env
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   ```

### 前端配置

```env
FRONTEND_API_BASE=http://localhost:8000
```

该配置会在应用启动时自动生成前端配置文件 `backend/static/js/config.js`。

## Docker 部署

使用 Docker Compose 部署时，确保 `.env` 文件配置正确。Docker Compose 会自动读取 `.env` 文件中的环境变量。

```bash
docker-compose up -d
```

## 安全建议

1. **永远不要将 `.env` 文件提交到版本控制系统**
   - `.env` 文件已被添加到 `.gitignore`

2. **使用强密码**
   - 数据库密码至少 12 位，包含大小写字母、数字和特殊字符
   - JWT 密钥使用 `openssl rand -hex 32` 生成

3. **定期更换密钥**
   - 定期更换数据库密码和 API 密钥
   - 定期更换 JWT 密钥

4. **生产环境配置**
   - 生产环境不要使用 `.env.example` 中的示例值
   - 生产环境的 `SECRET_KEY` 必须是强随机值
   - 生产环境的 `DB_PASSWORD` 必须是强随机值

5. **API 密钥管理**
   - 不要在代码中硬编码 API 密钥
   - 定期轮换 API 密钥
   - 监控 API 使用情况，防止滥用

## 常见问题

### Q: 为什么启动后前端无法连接后端？

A: 检查 `FRONTEND_API_BASE` 配置是否正确。确保该配置与后端的实际地址匹配。

### Q: 如何生成安全的密钥？

A: 使用以下命令生成安全的随机密钥：
```bash
# 生成 JWT 密钥
openssl rand -hex 32

# 生成数据库密码（16位）
openssl rand -base64 16
```

### Q: 如何在不同环境（开发/测试/生产）使用不同的配置？

A: 可以为不同环境创建不同的 `.env` 文件，例如：
- `.env.development` - 开发环境
- `.env.test` - 测试环境
- `.env.production` - 生产环境

然后在启动时指定使用哪个环境文件。

## 配置检查清单

在部署前，请检查以下配置项：

- [ ] `.env` 文件存在且不在版本控制中
- [ ] `DB_PASSWORD` 已设置为强密码
- [ ] `SECRET_KEY` 已使用 `openssl rand -hex 32` 生成
- [ ] `QWEN_API_KEY` 和 `DEEPSEEK_API_KEY` 已正确配置（如果需要使用AI功能）
- [ ] `FRONTEND_API_BASE` 配置正确
- [ ] 生产环境已移除所有示例/测试配置

## 更多信息

如需更多信息，请参考：
- [项目主文档](README.md)
- [部署文档](deploy.md)
