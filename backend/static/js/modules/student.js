import { get, post, put, del } from '../api.js';
import { showToast, serializeForm, createModal } from '../utils.js';
import { DEFAULT_PAGE, DEFAULT_SIZE } from '../config.js';

let currentPage = DEFAULT_PAGE;
let currentSize = DEFAULT_SIZE;
let currentName = '';

export async function render(container) {
    container.innerHTML = `
        <div class="card">
            <h3>👨‍🎓 学生管理</h3>
            <div class="search-bar">
                <input type="text" id="search-name" placeholder="按姓名模糊搜索" value="${escapeHtml(currentName)}">
                <button id="search-btn" class="btn btn-primary">🔍 搜索</button>
                <button id="add-student-btn" class="btn btn-primary">➕ 新增学生</button>
            </div>
            <div style="overflow-x: auto;">
                <div id="student-list"></div>
            </div>
            <div id="pagination" class="pagination"></div>
        </div>
        <div class="card">
            <h3>🔍 按学号查询详情</h3>
            <div class="form-group">
                <label>学号</label>
                <input type="text" id="query-student-no" placeholder="例如 230900001">
                <button id="query-by-no-btn" class="btn btn-primary">查询</button>
            </div>
            <div id="student-detail"></div>
        </div>
    `;

    await fetchStudents();

    document.getElementById('search-btn').onclick = () => {
        currentName = document.getElementById('search-name').value;
        currentPage = DEFAULT_PAGE;
        fetchStudents();
    };
    document.getElementById('add-student-btn').onclick = showAddModal;
    document.getElementById('query-by-no-btn').onclick = queryStudentByNo;
}

async function fetchStudents() {
    try {
        const params = new URLSearchParams({
            page: currentPage,
            size: currentSize,
            name: currentName
        });
        const data = await get(`/student/?${params.toString()}`);
        renderStudentTable(data.data || []);
        renderPagination(data.count);
    } catch (err) {
        showToast('获取学生列表失败', 'error');
    }
}

function renderStudentTable(students) {
    const container = document.getElementById('student-list');
    if (!students.length) {
        container.innerHTML = '<p>暂无数据</p>';
        return;
    }
    let html = `
        <table class="data-table" style="min-width: 1200px;">
            <thead>
                <tr>
                    <th>学号</th><th>姓名</th><th>性别</th><th>出生日期</th><th>籍贯</th>
                    <th>毕业学校</th><th>专业</th><th>入学日期</th><th>毕业日期</th>
                    <th>学历</th><th>咨询师编号</th><th>操作</th>
                </tr>
            </thead>
            <tbody>
    `;
    students.forEach(s => {
        html += `
            <tr>
                <td>${escapeHtml(s.student_no || '')}</td>
                <td>${escapeHtml(s.name || '')}</td>
                <td>${escapeHtml(s.gender || '')}</td>
                <td>${escapeHtml(s.birth_date || '')}</td>
                <td>${escapeHtml(s.birthplace || '')}</td>
                <td>${escapeHtml(s.graduated_school || '')}</td>
                <td>${escapeHtml(s.major || '')}</td>
                <td>${escapeHtml(s.enrollment_date || '')}</td>
                <td>${escapeHtml(s.graduation_date || '')}</td>
                <td>${formatEducation(s.education)}</td>
                <td>${escapeHtml(s.consultant_no || '')}</td>
                <td>
                    <button class="btn btn-sm btn-primary edit-student" data-id="${s.id}">编辑</button>
                    <button class="btn btn-sm btn-danger delete-student" data-id="${s.id}">删除</button>
                </td>
            </tr>
        `;
    });
    html += `</tbody></table>`;
    container.innerHTML = html;

    document.querySelectorAll('.edit-student').forEach(btn => {
        btn.onclick = () => showEditModal(btn.dataset.id);
    });
    document.querySelectorAll('.delete-student').forEach(btn => {
        btn.onclick = () => deleteStudent(btn.dataset.id);
    });
}

function formatEducation(edu) {
    const map = { 1: '高中', 2: '大专', 3: '本科', 4: '硕士', 5: '博士' };
    return map[edu] || edu || '';
}

function renderPagination(total) {
    const totalPages = Math.ceil(total / currentSize);
    const pageDiv = document.getElementById('pagination');
    if (totalPages <= 1) {
        pageDiv.innerHTML = '';
        return;
    }
    let btns = '';
    for (let i = 1; i <= totalPages; i++) {
        const activeClass = i === currentPage ? 'active' : '';
        btns += `<button class="btn btn-secondary page-btn ${activeClass}" data-page="${i}">${i}</button>`;
    }
    pageDiv.innerHTML = btns;
    document.querySelectorAll('.page-btn').forEach(btn => {
        btn.onclick = () => {
            currentPage = parseInt(btn.dataset.page);
            fetchStudents();
        };
    });
}

// 新增学生
function showAddModal() {
    const formHtml = `
        <form id="student-form">
            <div class="form-group"><label>学号*</label><input name="student_no" required></div>
            <div class="form-group"><label>姓名*</label><input name="name" required></div>
            <div class="form-group"><label>性别</label>
                <select name="gender"><option value="">请选择</option><option value="M">男</option><option value="F">女</option></select>
            </div>
            <div class="form-group"><label>出生日期</label><input type="date" name="birth_date"></div>
            <div class="form-group"><label>籍贯</label><input name="birthplace"></div>
            <div class="form-group"><label>毕业学校</label><input name="graduated_school"></div>
            <div class="form-group"><label>专业</label><input name="major"></div>
            <div class="form-group"><label>入学日期</label><input type="date" name="enrollment_date" required></div>
            <div class="form-group"><label>毕业日期</label><input type="date" name="graduation_date"></div>
            <div class="form-group"><label>学历</label>
                <select name="education">
                    <option value="">请选择</option>
                    <option value="1">高中</option><option value="2">大专</option>
                    <option value="3">本科</option><option value="4">硕士</option><option value="5">博士</option>
                </select>
            </div>
            <div class="form-group"><label>咨询师编号</label><input name="consultant_no"></div>
        </form>
    `;
    createModal('新增学生', formHtml, async () => {
        const form = document.querySelector('#student-form');
        const data = serializeForm(form);
        // 删除空值字段
        Object.keys(data).forEach(k => { if (data[k] === '') delete data[k]; });
        if (!data.student_no) {
            showToast('学号不能为空', 'error');
            return;
        }
        try {
            await post('/student/', data);
            showToast('添加成功', 'success');
            // 重置搜索条件并刷新第一页
            currentName = '';
            document.getElementById('search-name').value = '';
            currentPage = 1;
            fetchStudents();
        } catch (err) {
            showToast('添加失败', 'error');
        }
    });
}

// 编辑学生：使用后端 GET /student/{id} 接口
async function showEditModal(id) {
    try {
        // 调用后端接口获取学生详情
        const student = await get(`/student/${id}`);
        // 构建表单
        const formHtml = `
            <form id="edit-student-form">
                <div class="form-group"><label>学号</label><input name="student_no" value="${escapeHtml(student.student_no || '')}" readonly></div>
                <div class="form-group"><label>姓名*</label><input name="name" value="${escapeHtml(student.name || '')}" required></div>
                <div class="form-group"><label>性别</label>
                    <select name="gender">
                        <option value="">请选择</option>
                        <option value="M" ${student.gender === 'M' ? 'selected' : ''}>男</option>
                        <option value="F" ${student.gender === 'F' ? 'selected' : ''}>女</option>
                    </select>
                </div>
                <div class="form-group"><label>出生日期</label><input type="date" nam   e="birth_date" value="${student.birth_date || ''}"></div>
                <div class="form-group"><label>籍贯</label><input name="birthplace" value="${escapeHtml(student.birthplace || '')}"></div>
                <div class="form-group"><label>毕业学校</label><input name="graduated_school" value="${escapeHtml(student.graduated_school || '')}"></div>
                <div class="form-group"><label>专业</label><input name="major" value="${escapeHtml(student.major || '')}"></div>
                <div class="form-group"><label>入学日期</label><input type="date" name="enrollment_date" value="${student.enrollment_date || ''}" required></div>
                <div class="form-group"><label>毕业日期</label><input type="date" name="graduation_date" value="${student.graduation_date || ''}"></div>
                <div class="form-group"><label>学历</label>
                    <select name="education">
                        <option value="">请选择</option>
                        <option value="1" ${student.education == 1 ? 'selected' : ''}>高中</option>
                        <option value="2" ${student.education == 2 ? 'selected' : ''}>专科</option>
                        <option value="3" ${student.education == 3 ? 'selected' : ''}>本科</option>
                        <option value="4" ${student.education == 4 ? 'selected' : ''}>硕士</option>
                        <option value="5" ${student.education == 5 ? 'selected' : ''}>博士</option>
                    </select>
                </div>
                <div class="form-group"><label>咨询师编号</label><input name="consultant_no" value="${escapeHtml(student.consultant_no || '')}"></div>
            </form>
        `;
        createModal('编辑学生', formHtml, async () => {
            const form = document.querySelector('#edit-student-form');
            const data = serializeForm(form);
            delete data.student_no; // 学号不可修改
            Object.keys(data).forEach(k => { if (data[k] === '') delete data[k]; });
            try {
                await put(`/student/${student.id}`, data);
                showToast('更新成功', 'success');
                fetchStudents();
            } catch (err) {
                showToast('更新失败', 'error');
            }
        });
    } catch (err) {
        console.error(err);
        showToast('获取学生详情失败，请检查网络或联系管理员', 'error');
    }
}

async function deleteStudent(id) {
    if (confirm('确定删除该学生吗？')) {
        try {
            await del(`/student/${id}`);
            showToast('删除成功', 'success');
            // 删除后如果当前页没有数据且不是第一页，则回退一页
            const total = await getTotalCount(); // 需要实现一个获取总数的接口，或者从列表响应中获取
            // 简单方法：重新获取当前页，如果当前页数据为空且当前页>1，则跳转到上一页
            await fetchStudents(); // 先刷新当前页
            // 如果刷新后列表为空且 currentPage > 1，则跳转到上一页
            const container = document.getElementById('student-list');
            if (container.innerHTML.includes('暂无数据') && currentPage > 1) {
                currentPage--;
                await fetchStudents();
            }
        } catch (err) {
            showToast('删除失败', 'error');
        }
    }
}

// 辅助函数：获取学生总数（用于删除后判断，可选）
async function getTotalCount() {
    try {
        const params = new URLSearchParams({ page: 1, size: 1, name: currentName });
        const data = await get(`/student/?${params.toString()}`);
        return data.count || 0;
    } catch {
        return 0;
    }
}

async function queryStudentByNo() {
    const studentNo = document.getElementById('query-student-no').value.trim();
    if (!studentNo) return showToast('请输入学号');
    try {
        const data = await get(`/student/${studentNo}`);
        const detailDiv = document.getElementById('student-detail');
        detailDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    } catch (err) {
        document.getElementById('student-detail').innerHTML = '<p style="color:red">未找到学生</p>';
    }
}

// 简单的转义函数（如果全局没有，可以自己定义）
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function (m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}