# FastAPI-Users 集成文档

## 概述

项目已集成 `fastapi-users` 库，提供完整的用户认证和授权功能，包括：
- ✅ 用户注册
- ✅ 用户登录（JWT 认证）
- ✅ 密码重置
- ✅ 邮箱验证
- ✅ 用户信息管理
- ✅ 权限控制（普通用户/超级管理员）

---

## 安装依赖

```bash
pip install fastapi-users[sqlalchemy]==13.0.0
pip install fastapi-users[jwt]==13.0.0
```

或者使用 requirements.txt:

```bash
pip install -r requirements.txt
```

---

## 数据库配置

### 1. 创建用户表

在 `init.sql` 中已经添加了用户表定义。如果数据库已存在，需要执行以下 SQL：

```sql
CREATE TABLE IF NOT EXISTS user (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    email VARCHAR(320) UNIQUE NOT NULL COMMENT '邮箱',
    hashed_password VARCHAR(1024) NOT NULL COMMENT '加密密码',
    is_active BOOLEAN DEFAULT TRUE NOT NULL COMMENT '是否激活',
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL COMMENT '是否超级管理员',
    is_verified BOOLEAN DEFAULT FALSE NOT NULL COMMENT '是否已验证',
    username VARCHAR(50) UNIQUE COMMENT '用户名',
    full_name VARCHAR(100) COMMENT '全名',
    phone VARCHAR(20) COMMENT '电话',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted_at DATETIME DEFAULT '1900-01-01 00:00:00' COMMENT '软删除时间',
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

### 2. 配置 SECRET_KEY

在 `.env` 文件中添加或修改：

```env
# JWT 密钥（生产环境必须修改）
SECRET_KEY=your-very-secure-secret-key-here-change-in-production

# 或使用以下命令生成随机密钥：
# python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## API 接口说明

### 1. 用户注册

**接口地址**: `POST /auth/register`

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "username": "testuser",
  "full_name": "测试用户",
  "phone": "13800138000"
}
```

**响应**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "username": "testuser",
  "full_name": "测试用户",
  "phone": "13800138000"
}
```

---

### 2. 用户登录

**接口地址**: `POST /auth/jwt/login`

**请求体** (form-data):
```
username: user@example.com
password: secure_password
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 3. 获取当前用户信息

**接口地址**: `GET /users/me`

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "username": "testuser",
  "full_name": "测试用户",
  "phone": "13800138000"
}
```

---

### 4. 更新用户信息

**接口地址**: `PATCH /users/me`

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "full_name": "新姓名",
  "phone": "13900139000"
}
```

---

### 5. 修改密码

**接口地址**: `POST /auth/jwt/forgot-password`

**请求体**:
```json
{
  "email": "user@example.com"
}
```

**响应**:
```json
{
  "token": "reset_token_here"
}
```

---

### 6. 重置密码

**接口地址**: `POST /auth/jwt/reset-password`

**请求体**:
```json
{
  "token": "reset_token_here",
  "password": "new_secure_password"
}
```

---

## 在其他接口中使用认证

### 1. 依赖注入

```python
from fastapi import Depends
from fastapi_users import BaseUser
from backend.api.auth import fastapi_users

# 获取当前用户（需要登录）
current_active_user = fastapi_users.current_user(active=True)

# 获取当前超级用户（需要超级管理员权限）
current_superuser = fastapi_users.current_superuser()
```

### 2. 示例：创建需要认证的路由

```python
from fastapi import APIRouter, Depends, HTTPException
from backend.api.auth import fastapi_users

router = APIRouter()

# 需要登录的接口
@router.get("/protected")
async def protected_route(user=Depends(fastapi_users.current_user(active=True))):
    return {"message": f"Hello, {user.email}!"}

# 需要超级管理员权限的接口
@router.get("/admin")
async def admin_route(user=Depends(fastapi_users.current_superuser())):
    return {"message": f"Admin access granted for {user.email}"}
```

### 3. 示例：修改现有模块添加认证

```python
from fastapi import Depends
from backend.api.auth import fastapi_users

# 修改学生模块接口，添加认证
@router.get("/", response_model=dict)
async def get_students(
    page: int = 1, 
    size: int = 10, 
    name: str = None, 
    db: AsyncSession = Depends(get_async_db),
    user=Depends(fastapi_users.current_user(active=True))  # 添加认证
):
    """获取学生分页列表"""
    result = await student_service.get_paginated_students(db, page=page, size=size, name=name)
    return result
```

---

## 前端集成

### 1. 登录示例

```javascript
async function login(email, password) {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await fetch('/auth/jwt/login', {
    method: 'POST',
    body: formData
  });
  
  if (response.ok) {
    const data = await response.json();
    // 保存 token 到 localStorage
    localStorage.setItem('access_token', data.access_token);
    return data;
  } else {
    throw new Error('登录失败');
  }
}
```

### 2. 认证请求示例

```javascript
async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem('access_token');
  
  const headers = {
    'Authorization': `Bearer ${token}`,
    ...options.headers
  };
  
  const response = await fetch(url, {
    ...options,
    headers
  });
  
  if (response.status === 401) {
    // token 过期，跳转到登录页
    localStorage.removeItem('access_token');
    window.location.href = '/login.html';
  }
  
  return response;
}

// 使用示例
const data = await fetchWithAuth('/users/me').then(r => r.json());
```

---

## 常见问题

### Q: 如何创建超级管理员？

A: 有两种方式：

1. **直接在数据库中插入**:
```sql
INSERT INTO user (email, hashed_password, is_superuser, is_active, is_verified)
VALUES ('admin@example.com', 'hashed_password_here', TRUE, TRUE, TRUE);
```

2. **通过 API 创建后手动更新**:
```sql
UPDATE user SET is_superuser = TRUE WHERE email = 'admin@example.com';
```

### Q: 如何修改 JWT 过期时间？

A: 修改 `backend/core/auth.py` 中的 `get_jwt_strategy` 函数:

```python
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret_key=secret_key, 
        lifetime_seconds=3600 * 24 * 30  # 改为 30 天
    )
```

### Q: 如何禁用邮箱验证？

A: 注册时自动将 `is_verified` 设为 TRUE，在 `UserManager` 中重写 `on_after_register` 方法：

```python
async def on_after_register(self, user: User, request: Request | None = None):
    # 自动验证用户
    user.is_verified = True
    await self.user_db.update(user)
    print(f"User {user.id} has registered and verified.")
```

### Q: 如何添加自定义字段到用户模型？

A: 修改 `backend/models/user.py`，在 `User` 类中添加新字段，然后：

1. 修改数据库表结构（添加列）
2. 更新 `UserRead`, `UserCreate`, `UserUpdate` schemas

---

## 安全建议

1. **生产环境必须修改 SECRET_KEY**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **启用 HTTPS**
   - 生产环境使用 HTTPS 传输 JWT token
   - 防止中间人攻击

3. **定期更换密钥**
   - 建议每 3-6 个月更换一次 SECRET_KEY
   - 更换后需要用户重新登录

4. **限制 JWT 有效期**
   - 开发环境：7天
   - 生产环境：建议 1-7 天

5. **添加速率限制**
   - 防止暴力破解密码
   - 使用 `slowapi` 或 `fastapi-limiter`

---

## 参考文档

- [FastAPI-Users 官方文档](https://fastapi-users.github.io/fastapi-users/)
- [FastAPI-Users GitHub](https://github.com/fastapi-users/fastapi-users)
- [Pydantic 文档](https://docs.pydantic.dev/)
