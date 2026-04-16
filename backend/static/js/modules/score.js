import { get, post, put, del } from '../api.js';
import { showToast, serializeForm, createModal } from '../utils.js';
import { DEFAULT_PAGE, DEFAULT_SIZE } from '../config.js';

let currentPage = DEFAULT_PAGE;
let currentSize = DEFAULT_SIZE;
let currentStudentNo = '';
let currentClassNo = '';

export async function render(container) {
    container.innerHTML = `
        <div class="card">
            <h3>📊 成绩管理</h3>
            <div class="search-bar">
                <input type="text" id="search-student-no" placeholder="按学号搜索" value="${escapeHtml(currentStudentNo)}">
                <input type="text" id="search-class-no" placeholder="按班级编号搜索" value="${escapeHtml(currentClassNo)}">
                <button id="search-btn" class="btn btn-primary">🔍 搜索</button>
                <button id="add-score-btn" class="btn btn-primary">➕ 新增成绩</button>
            </div>
            <div style="overflow-x: auto;">
                <div id="score-list"></div>
            </div>
            <div id="pagination" class="pagination"></div>
        </div>
        <div class="card">
            <h3>📈 成绩统计</h3>
            <div class="form-group">
                <label>选择班级编号</label>
                <input type="text" id="stat-class-no" placeholder="例如 202401">
                <button id="stat-class-btn" class="btn btn-primary">班级统计</button>
            </div>
            <div class="form-group">
                <label>选择学号</label>
                <input type="text" id="stat-student-no" placeholder="例如 230900001">
                <button id="stat-student-btn" class="btn btn-primary">学生统计</button>
            </div>
            <div id="statistics-result"></div>
        </div>
    `;

    await fetchScores();

    document.getElementById('search-btn').onclick = () => {
        currentStudentNo = document.getElementById('search-student-no').value;
        currentClassNo = document.getElementById('search-class-no').value;
        currentPage = DEFAULT_PAGE;
        fetchScores();
    };
    document.getElementById('add-score-btn').onclick = showAddModal;
    document.getElementById('stat-class-btn').onclick = showClassStatistics;
    document.getElementById('stat-student-btn').onclick = showStudentStatistics;
}

async function fetchScores() {
    try {
        const params = new URLSearchParams({
            page: currentPage,
            size: currentSize
        });
        if (currentStudentNo) {
            const data = await get(`/score/student/${currentStudentNo}?${params.toString()}`);
            renderScoreTable(data.data || []);
            renderPagination(data.count);
        } else if (currentClassNo) {
            const data = await get(`/score/class/${currentClassNo}?${params.toString()}`);
            renderScoreTable(data.data || []);
            renderPagination(data.count);
        } else {
            const data = await get(`/score/?${params.toString()}`);
            renderScoreTable(data.data || []);
            renderPagination(data.count);
        }
    } catch (err) {
        showToast('获取成绩列表失败', 'error');
    }
}

function renderScoreTable(scores) {
    const container = document.getElementById('score-list');
    if (!scores.length) {
        container.innerHTML = '<p>暂无数据</p>';
        return;
    }
    let html = `
        <table class="data-table" style="min-width: 1000px;">
            <thead>
                <tr>
                    <th>ID</th><th>学号</th><th>学生姓名</th><th>班级编号</th>
                    <th>班级名称</th><th>进入日期</th><th>考核序次</th>
                    <th>考试日期</th><th>成绩</th><th>操作</th>
                </tr>
            </thead>
            <tbody>
    `;
    scores.forEach(s => {
        const scoreClass = s.score >= 60 ? 'score-pass' : 'score-fail';
        html += `
            <tr>
                <td>${s.id}</td>
                <td>${escapeHtml(s.student_no || '')}</td>
                <td>${escapeHtml(s.student_name || '')}</td>
                <td>${escapeHtml(s.class_no || '')}</td>
                <td>${escapeHtml(s.class_name || '')}</td>
                <td>${escapeHtml(s.start_date || '')}</td>
                <td>${s.exam_sequence}</td>
                <td>${escapeHtml(s.exam_date || '')}</td>
                <td class="${scoreClass}">${s.score}</td>
                <td>
                    <button class="btn btn-sm btn-primary edit-score" data-id="${s.id}">编辑</button>
                    <button class="btn btn-sm btn-danger delete-score" data-id="${s.id}">删除</button>
                </td>
            </tr>
        `;
    });
    html += `</tbody></table>`;
    container.innerHTML = html;

    // 绑定编辑和删除按钮事件
    container.querySelectorAll('.edit-score').forEach(btn => {
        btn.onclick = () => showEditModal(btn.dataset.id);
    });
    container.querySelectorAll('.delete-score').forEach(btn => {
        btn.onclick = () => deleteScore(btn.dataset.id);
    });
}

function renderPagination(total) {
    const container = document.getElementById('pagination');
    const totalPages = Math.ceil(total / currentSize);
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = `<span>共 ${total} 条</span> `;
    html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="changePage(${currentPage - 1})">上一页</button> `;

    // 显示页码
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    for (let i = startPage; i <= endPage; i++) {
        if (i === currentPage) {
            html += `<button class="active">${i}</button> `;
        } else {
            html += `<button onclick="changePage(${i})">${i}</button> `;
        }
    }

    html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="changePage(${currentPage + 1})">下一页</button>`;
    container.innerHTML = html;
}

// 全局函数供HTML中的onclick调用
window.changePage = (page) => {
    currentPage = page;
    fetchScores();
};

function showAddModal() {
    const modal = createModal(`
        <h3>新增成绩</h3>
        <form id="add-score-form">
            <div class="form-group">
                <label>学号 *</label>
                <input type="text" name="student_no" required>
            </div>
            <div class="form-group">
                <label>班级编号 *</label>
                <input type="text" name="class_no" required>
            </div>
            <div class="form-group">
                <label>进入日期</label>
                <input type="date" name="start_date">
            </div>
            <div class="form-group">
                <label>考核序次 *</label>
                <input type="number" name="exam_sequence" required min="1">
            </div>
            <div class="form-group">
                <label>考试日期 *</label>
                <input type="date" name="exam_date" required>
            </div>
            <div class="form-group">
                <label>成绩 *</label>
                <input type="number" name="score" required min="0" max="100" step="0.01">
            </div>
            <button type="submit" class="btn btn-primary">保存</button>
            <button type="button" class="btn btn-danger" onclick="this.closest('.modal').remove()">取消</button>
        </form>
    `);

    modal.querySelector('form').onsubmit = async (e) => {
        e.preventDefault();
        try {
            const formData = serializeForm(e.target);
            await post('/score/', formData);
            showToast('添加成功', 'success');
            modal.remove();
            fetchScores();
        } catch (err) {
            showToast('添加失败: ' + err.message, 'error');
        }
    };
}

async function showEditModal(id) {
    try {
        const data = await get(`/score/${id}`);
        const modal = createModal(`
            <h3>编辑成绩</h3>
            <form id="edit-score-form">
                <div class="form-group">
                    <label>学号 *</label>
                    <input type="text" name="student_no" value="${escapeHtml(data.student_no)}" required>
                </div>
                <div class="form-group">
                    <label>班级编号 *</label>
                    <input type="text" name="class_no" value="${escapeHtml(data.class_no)}" required>
                </div>
                <div class="form-group">
                    <label>进入日期</label>
                    <input type="date" name="start_date" value="${data.start_date || ''}">
                </div>
                <div class="form-group">
                    <label>考核序次 *</label>
                    <input type="number" name="exam_sequence" value="${data.exam_sequence}" required min="1">
                </div>
                <div class="form-group">
                    <label>考试日期 *</label>
                    <input type="date" name="exam_date" value="${data.exam_date || ''}" required>
                </div>
                <div class="form-group">
                    <label>成绩 *</label>
                    <input type="number" name="score" value="${data.score}" required min="0" max="100" step="0.01">
                </div>
                <button type="submit" class="btn btn-primary">保存</button>
                <button type="button" class="btn btn-danger" onclick="this.closest('.modal').remove()">取消</button>
            </form>
        `);

        modal.querySelector('form').onsubmit = async (e) => {
            e.preventDefault();
            try {
                const formData = serializeForm(e.target);
                await put(`/score/${id}`, formData);
                showToast('更新成功', 'success');
                modal.remove();
                fetchScores();
            } catch (err) {
                showToast('更新失败: ' + err.message, 'error');
            }
        };
    } catch (err) {
        showToast('获取成绩详情失败', 'error');
    }
}

async function deleteScore(id) {
    if (!confirm('确定要删除这条成绩记录吗？')) {
        return;
    }
    try {
        await del(`/score/${id}`);
        showToast('删除成功', 'success');
        fetchScores();
    } catch (err) {
        showToast('删除失败: ' + err.message, 'error');
    }
}

async function showClassStatistics() {
    const classNo = document.getElementById('stat-class-no').value;
    if (!classNo) {
        showToast('请输入班级编号', 'error');
        return;
    }

    try {
        const data = await get(`/score/statistics/class/${classNo}`);
        renderStatistics(data, '班级');
    } catch (err) {
        showToast('获取统计数据失败', 'error');
    }
}

async function showStudentStatistics() {
    const studentNo = document.getElementById('stat-student-no').value;
    if (!studentNo) {
        showToast('请输入学号', 'error');
        return;
    }

    try {
        const data = await get(`/score/statistics/student/${studentNo}`);
        renderStatistics(data, '学生');
    } catch (err) {
        showToast('获取统计数据失败', 'error');
    }
}

function renderStatistics(data, type) {
    const container = document.getElementById('statistics-result');
    const html = `
        <div class="stat-cards">
            <div class="stat-card">
                <div class="stat-value">${data.total_count}</div>
                <div class="stat-label">总考试次数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.average_score}</div>
                <div class="stat-label">平均分</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.highest_score}</div>
                <div class="stat-label">最高分</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.lowest_score}</div>
                <div class="stat-label">最低分</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.pass_count}</div>
                <div class="stat-label">及格次数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.pass_rate}%</div>
                <div class="stat-label">及格率</div>
            </div>
        </div>
    `;
    container.innerHTML = html;
}

// HTML转义函数
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
