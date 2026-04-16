import { get, post, put, del } from '../api.js';
import { showToast, serializeForm, createModal } from '../utils.js';
import { DEFAULT_PAGE, DEFAULT_SIZE } from '../config.js';

let currentPage = DEFAULT_PAGE;
let currentSize = DEFAULT_SIZE;
let currentStudentNo = '';
let currentCompany = '';
let employmentsCache = [];

export async function render(container) {
  container.innerHTML = `
        <div class="card">
            <h3>💼 就业信息管理</h3>
            <div class="search-bar">
                <input type="text" id="search-student-no" placeholder="按学号搜索" value="${escapeHtml(currentStudentNo)}">
                <input type="text" id="search-company" placeholder="按公司名称搜索" value="${escapeHtml(currentCompany)}">
                <button id="search-btn" class="btn btn-primary">🔍 搜索</button>
                <button id="add-emp-btn" class="btn btn-primary">➕ 新增就业记录</button>
            </div>
            <div style="overflow-x: auto;">
                <div id="employment-list">加载中...</div>
            </div>
            <div id="pagination" class="pagination"></div>
        </div>
    `;
  await fetchEmployments();

  document.getElementById('search-btn').onclick = () => {
    currentStudentNo = document.getElementById('search-student-no').value;
    currentCompany = document.getElementById('search-company').value;
    currentPage = DEFAULT_PAGE;
    fetchEmployments();
  };
  document.getElementById('add-emp-btn').onclick = showAddModal;
}

async function fetchEmployments() {
  const listDiv = document.getElementById('employment-list');
  if (!listDiv) return;
  listDiv.innerHTML = '加载中...';
  try {
    const params = new URLSearchParams({
      page: currentPage,
      size: currentSize,
      student_no: currentStudentNo,
      company_name: currentCompany
    });
    const data = await get(`/employment/?${params.toString()}`);
    // 兼容后端返回格式 { count, data }
    let employments = [];
    let total = 0;
    if (Array.isArray(data)) {
      employments = data;
      total = data.length;
    } else if (data.data && Array.isArray(data.data)) {
      employments = data.data;
      total = data.count || data.total || employments.length;
    } else {
      throw new Error('后端返回格式错误');
    }
    employmentsCache = employments;
    renderEmploymentList(employments);
    renderPagination(total);
  } catch (err) {
    console.error(err);
    listDiv.innerHTML = '<p style="color:red">加载失败，请检查网络</p>';
    showToast('获取就业列表失败', 'error');
  }
}

function renderEmploymentList(list) {
  const container = document.getElementById('employment-list');
  if (!list.length) {
    container.innerHTML = '<p>暂无就业记录</p>';
    return;
  }
  let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>学号</th>
                    <th>学生姓名</th>
                    <th>公司名称</th>
                    <th>职位</th>
                    <th>薪资</th>
                    <th>录用日期</th>
                    <th>入职日期</th>
                    <th>记录类型</th>
                    <th>当前状态</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
    `;
  list.forEach(e => {
    const isCurrentClass = e.is_current === 1 ? 'status-current' : 'status-previous';
    const isCurrentText = e.is_current === 1 ? '当前' : '历史';
    html += `
            <tr>
                <td>${e.id}</td>
                <td>${escapeHtml(e.student_no || '')}</td>
                <td>${escapeHtml(e.student_name || '')}</td>
                <td>${escapeHtml(e.company_name || '')}</td>
                <td>${escapeHtml(e.job_title || '')}</td>
                <td>${formatSalary(e.salary)}</td>
                <td>${escapeHtml(e.offer_date || '')}</td>
                <td>${escapeHtml(e.employment_start_date || '')}</td>
                <td>${escapeHtml(e.record_type || '')}</td>
                <td class="${isCurrentClass}">${isCurrentText}</td>
                <td>
                    <button class="btn btn-sm btn-primary edit-emp" data-id="${e.id}">编辑</button>
                    <button class="btn btn-sm btn-danger delete-emp" data-id="${e.id}">删除</button>
                </td>
            </tr>
        `;
  });
  html += `</tbody></table>`;
  container.innerHTML = html;

  document.querySelectorAll('.edit-emp').forEach(btn => {
    btn.onclick = () => {
      const empData = employmentsCache.find(e => e.id === parseInt(btn.dataset.id));
      if (empData) showEditModal(empData);
      else showToast('未找到就业数据', 'error');
    };
  });
  document.querySelectorAll('.delete-emp').forEach(btn => {
    btn.onclick = () => deleteEmployment(btn.dataset.id);
  });
}

function renderPagination(total) {
  const totalPages = Math.ceil(total / currentSize);
  const pageDiv = document.getElementById('pagination');
  if (totalPages <= 1) {
    pageDiv.innerHTML = '';
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
  pageDiv.innerHTML = html;
}

// 全局函数供HTML中的onclick调用
window.changePage = (page) => {
  currentPage = page;
  fetchEmployments();
};

function showAddModal() {
  const modal = createModal(`
        <h3>新增就业记录</h3>
        <form id="emp-form">
            <div class="form-group"><label>学号*</label><input name="student_no" required></div>
            <div class="form-group"><label>公司名称*</label><input name="company_name" required></div>
            <div class="form-group"><label>职位*</label><input name="job_title" required></div>
            <div class="form-group"><label>薪资</label><input name="salary" type="number" min="0"></div>
            <div class="form-group"><label>录用日期</label><input type="date" name="offer_date"></div>
            <div class="form-group"><label>入职日期</label><input type="date" name="employment_start_date"></div>
            <div class="form-group"><label>记录类型</label>
                <select name="record_type">
                    <option value="正式">正式</option>
                    <option value="实习">实习</option>
                    <option value="兼职">兼职</option>
                    <option value="其他">其他</option>
                </select>
            </div>
            <div class="form-group"><label>当前状态</label>
                <select name="is_current">
                    <option value="1">当前</option>
                    <option value="0">历史</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary">保存</button>
            <button type="button" class="btn btn-danger" onclick="this.closest('.modal').remove()">取消</button>
        </form>
    `);

  modal.querySelector('form').onsubmit = async (e) => {
    e.preventDefault();
    const data = serializeForm(e.target);
    if (!data.student_no || !data.company_name || !data.job_title) {
      showToast('学号、公司名称和职位不能为空', 'error');
      return;
    }
    try {
      await post('/employment/', data);
      showToast('创建成功', 'success');
      currentStudentNo = '';
      currentCompany = '';
      document.getElementById('search-student-no').value = '';
      document.getElementById('search-company').value = '';
      currentPage = DEFAULT_PAGE;
      modal.remove();
      fetchEmployments();
    } catch (err) {
      showToast('创建失败: ' + err.message, 'error');
    }
  };
}

async function showEditModal(empData) {
  const modal = createModal(`
        <h3>编辑就业记录</h3>
        <form id="edit-emp-form">
            <div class="form-group"><label>ID</label><input name="id" value="${empData.id}" readonly></div>
            <div class="form-group"><label>学号</label><input name="student_no" value="${escapeHtml(empData.student_no)}" readonly></div>
            <div class="form-group"><label>公司名称*</label><input name="company_name" value="${escapeHtml(empData.company_name)}" required></div>
            <div class="form-group"><label>职位*</label><input name="job_title" value="${escapeHtml(empData.job_title || '')}" required></div>
            <div class="form-group"><label>薪资</label><input name="salary" type="number" min="0" value="${empData.salary || ''}"></div>
            <div class="form-group"><label>录用日期</label><input type="date" name="offer_date" value="${empData.offer_date || ''}"></div>
            <div class="form-group"><label>入职日期</label><input type="date" name="employment_start_date" value="${empData.employment_start_date || ''}"></div>
            <div class="form-group"><label>记录类型</label>
                <select name="record_type">
                    <option value="正式" ${empData.record_type === '正式' ? 'selected' : ''}>正式</option>
                    <option value="实习" ${empData.record_type === '实习' ? 'selected' : ''}>实习</option>
                    <option value="兼职" ${empData.record_type === '兼职' ? 'selected' : ''}>兼职</option>
                    <option value="其他" ${empData.record_type === '其他' ? 'selected' : ''}>其他</option>
                </select>
            </div>
            <div class="form-group"><label>当前状态</label>
                <select name="is_current">
                    <option value="1" ${empData.is_current === 1 ? 'selected' : ''}>当前</option>
                    <option value="0" ${empData.is_current === 0 ? 'selected' : ''}>历史</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary">保存</button>
            <button type="button" class="btn btn-danger" onclick="this.closest('.modal').remove()">取消</button>
        </form>
    `);

  modal.querySelector('form').onsubmit = async (e) => {
    e.preventDefault();
    const data = serializeForm(e.target);
    const id = data.id;
    delete data.id;
    Object.keys(data).forEach(k => { if (data[k] === '') delete data[k]; });
    try {
      await put(`/employment/${id}`, data);
      showToast('更新成功', 'success');
      modal.remove();
      fetchEmployments();
    } catch (err) {
      showToast('更新失败: ' + err.message, 'error');
    }
  };
}

async function deleteEmployment(id) {
  if (!confirm('确定删除这条就业记录吗？')) {
    return;
  }
  try {
    await del(`/employment/${id}`);
    showToast('删除成功', 'success');
    await fetchEmployments();
    // 如果当前页无数据且不是第一页，则回退
    const container = document.getElementById('employment-list');
    if (container.innerHTML.includes('暂无就业记录') && currentPage > 1) {
      currentPage--;
      await fetchEmployments();
    }
  } catch (err) {
    showToast('删除失败: ' + err.message, 'error');
  }
}

function formatSalary(salary) {
  if (salary === null || salary === undefined || salary === '') {
    return '-';
  }
  return `¥${Number(salary).toLocaleString()}`;
}

function escapeHtml(str) {
  if (str === undefined || str === null) return '';
  return String(str).replace(/[&<>]/g, function (m) {
    if (m === '&') return '&amp;';
    if (m === '<') return '&lt;';
    if (m === '>') return '&gt;';
    return m;
  });
}