import { get, post, put, del } from '../api.js';
import { showToast, serializeForm, createModal } from '../utils.js';
import { DEFAULT_PAGE, DEFAULT_SIZE } from '../config.js';

let currentPage = DEFAULT_PAGE;
let currentSize = DEFAULT_SIZE;

export async function render(container) {
    container.innerHTML = `
        <div class="card">
            <h3>👥 用户管理</h3>
            <div class="search-bar">
                <button id="add-user-btn" class="btn btn-primary">➕ 新增用户</button>
                <span style="color: #666; margin-left: auto; font-size: 0.9rem;">
                    提示: 管理员可管理所有用户账户
                </span>
            </div>
            <div style="overflow-x: auto;">
                <div id="user-list"></div>
            </div>
            <div id="pagination" class="pagination"></div>
        </div>
    `;

    await fetchUsers();

    document.getElementById('add-user-btn').onclick = showAddModal;
}

async function fetchUsers() {
    try {
        const params = new URLSearchParams({
            skip: (currentPage - 1) * currentSize,
            limit: currentSize * 5
        });
        const data = await get(`/admin/users?${params.toString()}`);
        
        // 处理返回数据（可能是数组或对象）
        const users = Array.isArray(data) ? data : (data.data || data.items || []);
        const count = data.count || users.length;
        
        renderUserTable(users);
        renderPagination(count);
    } catch (err) {
        console.error('获取用户列表失败:', err);
        showToast('获取用户列表失败', 'error');
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    try {
        const date = new Date(dateStr);
        return date.toLocaleString('zh-CN');
    } catch {
        return dateStr;
    }
}

function renderUserTable(users) {
    const container = document.getElementById('user-list');
    if (!users || users.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#999;padding:2rem;">暂无用户数据</p>';
        return;
    }

    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>邮箱</th>
                    <th>用户名</th>
                    <th>姓名</th>
                    <th>手机号</th>
                    <th>状态</th>
                    <th>角色</th>
                    <th>注册时间</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    for (const u of users) {
        html += `
            <tr>
                <td>${u.id}</td>
                <td>${escapeHtml(u.email)}</td>
                <td>${escapeHtml(u.username) || '-'}</td>
                <td>${escapeHtml(u.full_name) || '-'}</td>
                <td>${escapeHtml(u.phone) || '-'}</td>
                <td>
                    <span class="status-badge ${u.is_active ? 'active' : 'inactive'}">
                        ${u.is_active ? '启用' : '禁用'}
                    </span>
                </td>
                <td>
                    <span class="role-badge ${u.is_superuser ? 'superuser' : 'user'}">
                        ${u.is_superuser ? '管理员' : '普通用户'}
                    </span>
                </td>
                <td>${formatDate(u.created_at)}</td>
                <td>
                    <button class="btn btn-small btn-edit" data-id="${u.id}">编辑</button>
                    ${!u.is_superuser ? `<button class="btn btn-small btn-delete" data-id="${u.id}">删除</button>` : ''}
                </td>
            </tr>
        `;
    }
    
    html += '</tbody></table>';
    container.innerHTML = html;

    // 绑定事件
    container.querySelectorAll('.btn-edit').forEach(btn => {
        btn.onclick = () => showEditModal(parseInt(btn.dataset.id));
    });
    container.querySelectorAll('.btn-delete').forEach(btn => {
        btn.onclick = () => deleteUser(parseInt(btn.dataset.id));
    });
}

function renderPagination(totalCount) {
    const totalPages = Math.ceil(totalCount / currentSize);
    const container = document.getElementById('pagination');
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';
    html += `<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} data-page="${currentPage - 1}">上一页</button>`;
    
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
    }
    
    html += `<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} data-page="${currentPage + 1}">下一页</button>`;
    container.innerHTML = html;

    container.querySelectorAll('.page-btn:not([disabled])').forEach(btn => {
        btn.onclick = () => {
            currentPage = parseInt(btn.dataset.page);
            fetchUsers();
        };
    });
}

// 新增用户弹窗
async function showAddModal() {
    const modal = await createModal(`
        <h3>新增用户</h3>
        <form id="add-user-form">
            <div class="form-group">
                <label>邮箱 *</label>
                <input type="email" name="email" required placeholder="请输入邮箱">
            </div>
            <div class="form-group">
                <label>密码 *</label>
                <input type="password" name="password" required placeholder="请输入密码（至少8位）" minlength="8">
            </div>
            <div class="form-group">
                <label>用户名</label>
                <input type="text" name="username" placeholder="请输入用户名">
            </div>
            <div class="form-group">
                <label>姓名</label>
                <input type="text" name="full_name" placeholder="请输入姓名">
            </div>
            <div class="form-group">
                <label>手机号</label>
                <input type="text" name="phone" placeholder="请输入手机号">
            </div>
            <div class="form-group checkbox-group">
                <label><input type="checkbox" name="is_superuser"> 设为管理员</label>
            </div>
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">创建</button>
                <button type="button" class="btn btn-cancel" onclick="this.closest('.modal-overlay').remove()">取消</button>
            </div>
        </form>
    `, '600px');

    modal.querySelector('#add-user-form').onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const userData = {
            email: formData.get('email'),
            password: formData.get('password'),
            username: formData.get('username') || null,
            full_name: formData.get('full_name') || null,
            phone: formData.get('phone') || null,
            is_superuser: formData.has('is_superuser')
        };

        try {
            await post('/admin/users', userData);
            showToast('用户创建成功', 'success');
            modal.remove();
            currentPage = 1;
            fetchUsers();
        } catch (err) {
            showToast(err.message || '创建失败', 'error');
        }
    };
}

// 编辑用户弹窗
async function showEditModal(userId) {
    try {
        const user = await get(`/admin/users/${userId}`);
        
        const modal = await createModal(`
            <h3>编辑用户 - ${escapeHtml(user.email)}</h3>
            <form id="edit-user-form">
                <div class="form-group">
                    <label>邮箱</label>
                    <input type="email" name="email" value="${escapeHtml(user.email)}" required>
                </div>
                <div class="form-group">
                    <label>用户名</label>
                    <input type="text" name="username" value="${escapeHtml(user.username || '')}">
                </div>
                <div class="form-group">
                    <label>姓名</label>
                    <input type="text" name="full_name" value="${escapeHtml(user.full_name || '')}">
                </div>
                <div class="form-group">
                    <label>手机号</label>
                    <input type="text" name="phone" value="${escapeHtml(user.phone || '')}">
                </div>
                <div class="form-group">
                    <label>启用状态</label>
                    <select name="is_active">
                        <option value="true" ${user.is_active ? 'selected' : ''}>启用</option>
                        <option value="false" ${!user.is_active ? 'selected' : ''}>禁用</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>管理员</label>
                    <select name="is_superuser">
                        <option value="true" ${user.is_superuser ? 'selected' : ''}>是</option>
                        <option value="false" ${!user.is_superuser ? 'selected' : ''}>否</option>
                    </select>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">保存修改</button>
                    <button type="button" class="btn btn-cancel" onclick="this.closest('.modal-overlay').remove()">取消</button>
                </div>
            </form>
        `, '600px');

        modal.querySelector('#edit-user-form').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            // 将字符串转换为布尔值
            const userData = {
                email: formData.get('email'),
                username: formData.get('username') || null,
                full_name: formData.get('full_name') || null,
                phone: formData.get('phone') || null,
                is_active: formData.get('is_active') === 'true',
                is_superuser: formData.get('is_superuser') === 'true'
            };

            try {
                await put(`/admin/users/${userId}`, userData);
                showToast('用户信息更新成功', 'success');
                modal.remove();
                fetchUsers();
            } catch (err) {
                showToast(err.message || '更新失败', 'error');
            }
        };
    } catch (err) {
        showToast('获取用户信息失败', 'error');
    }
}

// 删除用户
async function deleteUser(userId) {
    const confirmDel = confirm('确定要删除该用户吗？此操作不可恢复！');
    if (!confirmDel) return;

    try {
        await del(`/admin/users/${userId}`);
        showToast('用户已删除', 'success');
        fetchUsers();
    } catch (err) {
        showToast(err.message || '删除失败', 'error');
    }
}
