# FastAPI-Users 集成完成总结

## ✅ 已完成的工作

### 1. 删除了自定义用户模块
- ✅ `backend/models/users.py`
- ✅ `backend/repositories/user.py`
- ✅ `backend/schemas/user.py`
- ✅ `backend/core/utils/security.py`

### 2. 更新了依赖包
- ✅ 在 `requirements.txt` 中添加了 `fastapi-users[sqlalchemy]==13.0.0`
- ✅ 在 `requirements.txt` 中添加了 `fastapi-users[jwt]==13.0.0`

### 3. 创建了 FastAPI-Users 相关文件
- ✅ `backend/models/user.py` - 用户模型（继承 fastapi-users 基类）
- ✅ `backend/core/auth.py` - 认证配置和用户管理器
- ✅ `backend/api/auth.py` - 认证 API 路由

### 4. 更新了主应用
- ✅ 在 `backend/app/main.py` 中注册了认证路由
- ✅ 路由前缀：`/auth/*` 和 `/users/*`

### 5. 更新了数据库脚本
- ✅ 在 `init.sql` 中添加了 `user` 表定义

### 6. 创建了文档和测试脚本
- ✅ `FASTAPI_USERS.md` - 详细的使用文档
- ✅ `test_auth.py` - API 测试脚本

---

## 📋 下一步操作

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 SECRET_KEY

在 `.env` 文件中添加或修改：

```env
# 生成随机密钥（可选）
# python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-very-secure-secret-key-here
```

### 3. 创建用户表

如果数据库已存在，执行以下 SQL：

```bash
mysql -u root -p < init.sql
```

或者直接在 MySQL 中执行：

```sql
USE student_management_system;

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

### 4. 启动后端服务

```bash
python backend/app/main.py
```

### 5. 测试认证功能

运行测试脚本：

```bash
python test_auth.py
```

或者访问 API 文档：http://localhost:8000/docs

---

## 📚 API 接口列表

### 认证相关

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 用户注册 | POST | `/auth/register` | 注册新用户 |
| 用户登录 | POST | `/auth/jwt/login` | 登录获取 JWT token |
| 退出登录 | POST | `/auth/jwt/logout` | 退出登录 |
| 忘记密码 | POST | `/auth/jwt/forgot-password` | 请求密码重置 token |
| 重置密码 | POST | `/auth/jwt/reset-password` | 使用 token 重置密码 |

### 用户管理

| 接口 | 方法 | 路径 | 说明 | 需要认证 |
|------|------|------|------|----------|
| 获取当前用户 | GET | `/users/me` | 获取当前登录用户信息 | ✅ |
| 更新当前用户 | PATCH | `/users/me` | 更新当前用户信息 | ✅ |
| 获取用户列表 | GET | `/users` | 获取所有用户列表 | ✅ (超级管理员) |
| 获取指定用户 | GET | `/users/{id}` | 获取指定用户信息 | ✅ (超级管理员) |
| 更新指定用户 | PATCH | `/users/{id}` | 更新指定用户信息 | ✅ (超级管理员) |
| 删除指定用户 | DELETE | `/users/{id}` | 删除指定用户 | ✅ (超级管理员) |

---

## 🔐 如何在其他模块中使用认证

### 示例 1: 添加认证到学生模块

```python
from fastapi import Depends, HTTPException, status
from backend.api.auth import fastapi_users

# 需要登录的接口
@router.get("/", response_model=dict)
async def get_students(
    page: int = 1, 
    size: int = 10, 
    name: str = None, 
    db: AsyncSession = Depends(get_async_db),
    user=Depends(fastapi_users.current_user(active=True))  # 添加认证
):
    """获取学生分页列表（需要登录）"""
    result = await student_service.get_paginated_students(db, page=page, size=size, name=name)
    return result

# 需要超级管理员权限的接口
@router.delete("/{student_id}")
async def delete_student(
    student_id: int, 
    db: AsyncSession = Depends(get_async_db),
    user=Depends(fastapi_users.current_superuser())  # 需要超级管理员
):
    """删除学生（需要超级管理员权限）"""
    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    await student_service.delete_student(db, str(student_id))
    return {"message": "删除成功"}
```

### 示例 2: 在服务层访问当前用户

```python
from backend.api.auth import fastapi_users

@router.get("/protected")
async def protected_route(
    user=Depends(fastapi_users.current_user(active=True))
):
    """受保护的路由"""
    return {
        "message": f"Hello, {user.email}!",
        "user_id": user.id,
        "is_superuser": user.is_superuser
    }
```

---

## 📱 前端集成示例

### 登录

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
    localStorage.setItem('access_token', data.access_token);
    return data;
  } else {
    throw new Error('登录失败');
  }
}
```

### 发送认证请求

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
    localStorage.removeItem('access_token');
    window.location.href = '/login.html';
  }
  
  return response;
}

// 使用示例
const students = await fetchWithAuth('/student/?page=1&size=10')
  .then(r => r.json());
```

---

## ⚠️ 重要提示

1. **生产环境必须修改 SECRET_KEY**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **启用 HTTPS**
   - 生产环境必须使用 HTTPS
   - JWT token 在传输过程中必须加密

3. **JWT 过期时间**
   - 默认：7天
   - 修改位置：`backend/core/auth.py` 中的 `get_jwt_strategy()` 函数

4. **软删除支持**
   - 用户表支持软删除
   - `deleted_at` 默认值：`1900-01-01 00:00:00`
   - 快速API-Users 的查询会自动过滤已删除用户

---

## 📖 文档

- [FastAPI-Users 集成文档](FASTAPI_USERS.md) - 详细的使用指南
- [API 文档](http://localhost:8000/docs) - 交互式 API 文档
- [ReDoc](http://localhost:8000/redoc) - API 文档（另一种格式）

---

## 🐛 故障排除

### 问题 1: 导入错误 `ModuleNotFoundError: No module named 'fastapi_users'`

**解决方案**:
```bash
pip install fastapi-users[sqlalchemy]==13.0.0
pip install fastapi-users[jwt]==13.0.0
```

### 问题 2: 数据库表不存在

**解决方案**: 执行 `init.sql` 中的用户表定义

### 问题 3: SECRET_KEY 未设置

**解决方案**: 在 `.env` 文件中添加 `SECRET_KEY`

### 问题 4: 登录返回 401

**可能原因**:
- 用户名或密码错误
- 账户未激活（`is_active = False`）

---

## 🎉 集成完成！

现在你的项目已经成功集成了 FastAPI-Users，可以开始使用完整的用户认证功能了！

需要帮助？查看 [FastAPI-Users 集成文档](FASTAPI_USERS.md) 获取更多信息。
