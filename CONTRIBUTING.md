# 贡献指南

感谢你对本项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议，请：

1. 在 [Issues](https://github.com/your-username/student-management-system/issues) 中搜索是否已有类似问题
2. 如果没有，创建新的 Issue，并提供：
   - 清晰的标题
   - 详细的问题描述
   - 重现步骤
   - 预期行为
   - 实际行为
   - 环境信息（操作系统、Python 版本等）
   - 相关的日志或截图

### 提交代码

如果你想提交代码，请遵循以下步骤：

#### 1. Fork 项目

点击项目页面右上角的 "Fork" 按钮，将项目 Fork 到你的 GitHub 账户。

#### 2. 克隆项目

```bash
git clone https://github.com/your-username/student-management-system.git
cd student-management-system
```

#### 3. 创建分支

```bash
# 创建新分支进行开发
git checkout -b feature/your-feature-name

# 或修复 bug
git checkout -b fix/your-bug-fix
```

分支命名规范：
- `feature/xxx` - 新功能
- `fix/xxx` - bug 修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 代码重构
- `test/xxx` - 测试相关
- `style/xxx` - 代码格式调整

#### 4. 进行开发

遵循项目的代码风格和架构设计。

##### 代码风格

- Python 代码遵循 [PEP 8](https://pep8.org/)
- 使用 4 空格缩进（不要使用 Tab）
- 行长度不超过 120 字符
- 使用有意义的变量和函数名
- 添加适当的注释

##### 分层架构

遵循项目的 MVC 分层架构：
- **API 层**：只处理 HTTP 请求和响应
- **Service 层**：处理业务逻辑
- **Repository 层**：处理数据访问
- **Model 层**：定义数据库模型
- **Schema 层**：定义数据传输对象

不要跨层调用：
- ❌ API 层不能直接调用 Repository 层
- ❌ Repository 层不能调用 Service 层
- ✅ 正确流程：API → Service → Repository

##### 提交规范

提交信息使用清晰的描述：

```
<type>(<scope>): <subject>

<body>

<footer>
```

Type 类型：
- `feat`: 新功能
- `fix`: bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构（既不是新功能也不是修复）
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(student): 添加按专业查询学生功能

- 在 StudentRepo 中添加 get_by_major 方法
- 在 StudentService 中添加按专业查询逻辑
- 在 API 中添加 GET /student/major/{major} 端点
- 添加对应的测试用例

Closes #123
```

#### 5. 测试

确保你的代码：
- 通过所有现有测试
- 添加新的测试用例（如果适用）
- 在本地测试通过

运行测试：
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_student.py

# 运行特定测试
pytest tests/test_student.py::test_create_student
```

#### 6. 代码检查

在提交前运行代码检查：
```bash
# 代码格式化
black backend/

# 排序导入
isort backend/

# 代码检查
flake8 backend/

# 类型检查（可选）
mypy backend/
```

#### 7. 提交更改

```bash
git add .
git commit -m "feat(student): 添加按专业查询学生功能"
```

#### 8. 推送到 GitHub

```bash
git push origin feature/your-feature-name
```

#### 9. 创建 Pull Request

1. 访问你的 GitHub 仓库页面
2. 点击 "Pull requests" → "New pull request"
3. 选择你的分支
4. 填写 PR 模板：
   - 标题：清晰描述更改
   - 描述：详细说明更改内容、原因、测试情况
   - 关联相关的 Issue
5. 提交 PR

## Pull Request 审查

### 审查流程

1. **自动检查**：CI/CD 会自动运行测试和代码检查
2. **人工审查**：维护者会审查你的代码
3. **反馈**：如果需要修改，维护者会提供反馈
4. **合并**：通过审查后，代码会被合并到主分支

### 审查标准

- 代码质量
- 测试覆盖率
- 文档完整性
- 遵循项目规范
- 向后兼容性（如果有破坏性更改需要说明）

## 开发规范

### 添加新功能

请参考 `backend/README.md` 中的"添加新功能"章节，遵循以下步骤：

1. 定义 Model（在 `models/` 目录）
2. 定义 Schema（在 `schemas/` 目录）
3. 创建 Repository（在 `repositories/` 目录）
4. 创建 Service（在 `services/` 目录）
5. 创建 API（在 `api/` 目录）
6. 注册路由（在 `app/main.py` 中）

### 编写测试

为所有新功能添加测试：

```python
# tests/test_student.py
import pytest
from httpx import AsyncClient
from backend.app.main import app

@pytest.mark.asyncio
async def test_create_student():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/student/",
            json={
                "student_no": "250000001",
                "name": "张三",
                "gender": "M"
            }
        )
        assert response.status_code == 200
        assert response.json()["name"] == "张三"
```

### 更新文档

如果你的更改影响：
- API 接口：更新 API 文档
- 数据库结构：更新 `backend/README.md` 中的数据库设计部分
- 架构设计：更新 `backend/REFACTORING.md`
- 使用方式：更新 `README.md`

## 社区准则

### 行为准则

- 尊重所有贡献者
- 接受建设性批评
- 专注于对社区最有利的事情
- 对不同观点保持开放态度

### 沟通方式

- 使用友好、专业的语言
- 清晰地表达想法
- 耐心倾听他人意见
- 避免人身攻击

## 获取帮助

如果你在贡献过程中遇到问题：

1. 查看 [项目文档](../README.md)
2. 搜索现有的 [Issues](https://github.com/your-username/student-management-system/issues)
3. 创建新的 Issue 寻求帮助
4. 联系项目维护者

## 认可贡献者

所有贡献者都会在项目的贡献者列表中被认可。你的名字将出现在：
- README.md 的贡献者部分
- GitHub 的贡献者列表

## 许可证

通过向本项目贡献代码，你同意你的代码将根据项目的 [MIT 许可证](../LICENSE) 进行许可。

---

再次感谢你的贡献！🎉
