# CORS 配置说明

## 什么是 CORS？

CORS（Cross-Origin Resource Sharing，跨域资源共享）是一种基于 HTTP 头的机制，允许服务器标示除了它自己以外的其他源（域、协议或端口）浏览器应该允许从其加载资源。

## 问题现象

当浏览器向不同域名、端口或协议发送请求时，会触发CORS检查：

```
WARNING  | Response: OPTIONS /student/ - Status: 405 - Duration: 0.001s
```

`OPTIONS` 请求是浏览器的**预检请求**（preflight request），用于检查服务器是否允许跨域请求。

## 解决方案

本项目已添加 `CORSMiddleware` 来处理跨域请求。

### 配置位置

配置文件：`backend/core/config.py`

```python
# CORS配置
CORS_ORIGINS: list = Field(default_factory=lambda: ["*"])
CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
CORS_ALLOW_METHODS: list = Field(default_factory=lambda: ["*"])
CORS_ALLOW_HEADERS: list = Field(default_factory=lambda: ["*"])
```

### 环境变量配置

在 `.env` 文件中可以覆盖默认配置：

```env
# 开发环境：允许所有来源
CORS_ORIGINS=["*"]

# 生产环境：只允许特定域名
CORS_ORIGINS=["http://example.com", "https://www.example.com"]

# 允许携带凭证（如Cookies）
CORS_ALLOW_CREDENTIALS=true

# 允许的HTTP方法
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]

# 允许的请求头
CORS_ALLOW_HEADERS=["*"]
```

### CORS 中间件实现

位置：`backend/app/main.py`

```python
# 注册CORS中间件（必须在其他中间件之前）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)
```

## 配置说明

### `allow_origins`

允许哪些域名可以访问API：

- `["*"]`：允许所有域名（开发环境）
- `["http://localhost:3000", "https://example.com"]`：只允许指定域名（生产环境推荐）

### `allow_credentials`

是否允许携带凭证（如Cookies）：

- `True`：允许
- `False`：不允许

### `allow_methods`

允许哪些HTTP方法：

- `["*"]`：允许所有方法
- `["GET", "POST", "PUT", "DELETE"]`：只允许指定方法

### `allow_headers`

允许哪些请求头：

- `["*"]`：允许所有请求头
- `["Content-Type", "Authorization"]`：只允许指定请求头

## 开发环境 vs 生产环境

### 开发环境

```env
# 允许所有来源，方便开发调试
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
```

### 生产环境

```env
# 只允许指定的前端域名，提高安全性
CORS_ORIGINS=["https://yourdomain.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "PATCH"]
CORS_ALLOW_HEADERS=["Content-Type", "Authorization"]
```

## 常见问题

### Q: 为什么需要CORS？

A: 浏览器的同源策略（Same-Origin Policy）限制网页只能从相同域名加载资源。CORS允许服务器明确指定哪些域名可以访问其资源。

### Q: OPTIONS 请求是什么？

A: OPTIONS 是预检请求，浏览器在发送复杂请求（如 PUT、DELETE）之前，会先发送 OPTIONS 请求检查服务器是否允许该跨域请求。

### Q: 如何测试CORS是否配置正确？

A: 使用浏览器的开发者工具（F12）：
1. 打开 Network 标签
2. 查看OPTIONS请求
3. 检查响应头：
   - `Access-Control-Allow-Origin`
   - `Access-Control-Allow-Methods`
   - `Access-Control-Allow-Headers`

### Q: 生产环境如何配置CORS？

A: 
1. 不要使用 `["*"]`，明确指定允许的域名
2. 限制允许的HTTP方法和请求头
3. 考虑使用Nginx/Apache等反向代理统一处理CORS

## 安全建议

1. **生产环境不要使用 `["*"]`**
   - 明确指定允许的域名
   - 避免任意域名访问API

2. **限制HTTP方法**
   - 只允许必要的HTTP方法
   - 避免不必要的操作

3. **限制请求头**
   - 只允许必要的请求头
   - 避免敏感信息泄露

4. **定期审查CORS配置**
   - 及时移除不再需要的域名
   - 确保配置符合实际需求

## 相关资源

- [MDN - CORS](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CORS)
- [FastAPI - CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [CORS 错误说明](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CORS/Errors)
