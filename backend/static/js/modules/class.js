import { get, post, put, del } from '../api.js';
import { showToast, serializeForm, createModal, renderPagination } from '../utils.js';
import { DEFAULT_PAGE, DEFAULT_SIZE } from '../config.js';

let currentPage = DEFAULT_PAGE;
let currentSize = DEFAULT_SIZE;
let currentName = '';
let classesCache = [];

export async function render(container) {
  container.innerHTML = `
        <div class="card">
            <h3>🏫 班级管理</h3>
            <div class="search-bar">
                <input type="text" id="search-name" placeholder="按班级名称搜索" value="${escapeHtml(currentName)}">
                <button id="search-btn" class="btn btn-primary">🔍 搜索</button>
                <button id="add-class-btn" class="btn btn-primary">➕ 新建班级</button>
            </div>
            <div style="overflow-x: auto;">
                <div id="class-list">加载中...</div>
            </div>
            <div id="pagination" class="pagination"></div>
        </div>
    `;
  await fetchClasses();

  document.getElementById('search-btn').onclick = () => {
    currentName = document.getElementById('search-name').value;
    currentPage = DEFAULT_PAGE;
    fetchClasses();
  };
  document.getElementById('add-class-btn').onclick = showAddModal;
}

async function fetchClasses() {
  const listDiv = document.getElementById('class-list');
  if (!listDiv) return;
  listDiv.innerHTML = '加载中...';
  try {
    const params = new URLSearchParams({
      page: currentPage,
      size: currentSize,
      name: currentName
    });
    const data = await get(`/class/?${params.toString()}`);
    // 统一响应格式 { datas, pagination }
    let classes = data.datas || [];
    let total = data.pagination ? data.pagination.count : classes.length;
    classesCache = classes;
    renderClassList(classes);
    renderPagination('pagination', {
      currentPage,
      totalPages: Math.ceil(total / currentSize),
      total,
      pageSize: currentSize,
      onPageChange: (page) => { currentPage = page; fetchClasses(); },
      onSizeChange: (size) => { currentSize = size; currentPage = DEFAULT_PAGE; fetchClasses(); }
    });
  } catch (err) {
    console.error(err);
    listDiv.innerHTML = '<p style="color:red">加载失败，请检查网络</p>';
    showToast('获取班级列表失败', 'error');
  }
}

function renderClassList(classes) {
  const container = document.getElementById('class-list');
  if (!classes.length) {
    container.innerHTML = '<p>暂无班级数据</p>';
    return;
  }
  let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>班级编号</th>
                    <th>班级名称</th>
                    <th>开课日期</th>
                    <th>学生人数</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
    `;
  classes.forEach(c => {
    html += `
            <tr>
                <td>${escapeHtml(c.class_no || '')}</td>
                <td>${escapeHtml(c.class_name || '')}</td>
                <td>${escapeHtml(c.start_date || '')}</td>
                <td>${c.student_count !== undefined ? c.student_count : '-'}</td>
                <td>
                    <button class="btn btn-sm btn-primary view-members" data-no="${escapeHtml(c.class_no)}">👥 成员</button>
                    <button class="btn btn-sm btn-primary edit-class" data-no="${escapeHtml(c.class_no)}">编辑</button>
                    <button class="btn btn-sm btn-danger delete-class" data-no="${escapeHtml(c.class_no)}">删除</button>
                </td>
            </tr>
        `;
  });
  html += `</tbody></table>`;
  container.innerHTML = html;

  // 绑定成员按钮事件
  document.querySelectorAll('.view-members').forEach(btn => {
    btn.onclick = () => showClassMembers(btn.dataset.no);
  });
  // 绑定编辑按钮事件
  document.querySelectorAll('.edit-class').forEach(btn => {
    btn.onclick = () => {
      const classNo = btn.dataset.no;
      const classData = classesCache.find(c => c.class_no === classNo);
      if (classData) showEditModal(classData);
      else showToast('未找到班级数据', 'error');
    };
  });
  // 绑定删除按钮事件
  document.querySelectorAll('.delete-class').forEach(btn => {
    btn.onclick = () => deleteClass(btn.dataset.no);
  });
}

async function showClassMembers(classNo) {
  try {
    const result = await get(`/class/${classNo}/`);
    const members = result.datas || result || [];
    if (!members || !members.length) {
      showToast('该班级暂无成员信息', 'info');
      return;
    }
    const students = members.filter(m => m.role === '学生');
    const teachers = members.filter(m => m.role === '教师');
    let content = `<div style="max-height: 60vh; overflow-y: auto;">`;
    if (students.length) {
      content += `<h4>👨‍🎓 学生 (${students.length})</h4>
                        <table class="data-table">
                            <thead><tr><th>姓名</th><th>学号</th><th>专业</th></tr></thead>
                            <tbody>
                                ${students.map(s => `<tr><td>${escapeHtml(s.name)}</td><td>${escapeHtml(s.code)}</td><td>${escapeHtml(s.major || '')}</td></tr>`).join('')}
                            </tbody>
                        </table>`;
    }
    if (teachers.length) {
      content += `<h4>👩‍🏫 教师 (${teachers.length})</h4>
                        <table class="data-table">
                            <thead><tr><th>姓名</th><th>教师编号</th><th>职称</th></tr></thead>
                            <tbody>
                                ${teachers.map(t => `<tr><td>${escapeHtml(t.name)}</td><td>${escapeHtml(t.code)}</td><td>${escapeHtml(t.title || '')}</td></tr>`).join('')}
                            </tbody>
                        </table>`;
    }
    content += `</div>`;
    createModal(`班级成员 - ${classNo}`, content, null, { closeButton: true });
  } catch (err) {
    console.error(err);
    showToast('获取成员信息失败', 'error');
  }
}

function showAddModal() {
  const modal = createModal(`
        <h3>新建班级</h3>
        <form id="class-form">
            <div class="form-group"><label>班级编号*</label><input name="class_no" required></div>
            <div class="form-group"><label>班级名称*</label><input name="class_name" required></div>
            <div class="form-group"><label>开课日期</label><input type="date" name="start_date"></div>
            <button type="submit" class="btn btn-primary">保存</button>
            <button type="button" class="btn btn-danger" onclick="this.closest('.modal-overlay').remove()">取消</button>
        </form>
    `);

  modal.querySelector('form').onsubmit = async (e) => {
    e.preventDefault();
    const data = serializeForm(e.target);
    if (!data.class_no || !data.class_name) {
      showToast('班级编号和名称不能为空', 'error');
      return;
    }
    try {
      await post('/class/', data);
      showToast('创建成功', 'success');
      currentName = '';
      document.getElementById('search-name').value = '';
      currentPage = DEFAULT_PAGE;
      modal.remove();
      fetchClasses();
    } catch (err) {
      showToast('创建失败: ' + err.message, 'error');
    }
  };
}

function showEditModal(classData) {
  const modal = createModal(`
        <h3>编辑班级</h3>
        <form id="edit-class-form">
            <div class="form-group"><label>班级编号</label><input name="class_no" value="${escapeHtml(classData.class_no)}" readonly></div>
            <div class="form-group"><label>班级名称*</label><input name="class_name" value="${escapeHtml(classData.class_name)}" required></div>
            <div class="form-group"><label>开课日期</label><input type="date" name="start_date" value="${classData.start_date || ''}"></div>
            <button type="submit" class="btn btn-primary">保存</button>
            <button type="button" class="btn btn-danger" onclick="this.closest('.modal-overlay').remove()">取消</button>
        </form>
    `);

  modal.querySelector('form').onsubmit = async (e) => {
    e.preventDefault();
    const data = serializeForm(e.target);
    delete data.class_no;
    Object.keys(data).forEach(k => { if (data[k] === '') delete data[k]; });
    try {
      await put(`/class/${classData.class_no}`, data);
      showToast('更新成功', 'success');
      modal.remove();
      fetchClasses();
    } catch (err) {
      showToast('更新失败: ' + err.message, 'error');
    }
  };
}

async function deleteClass(classNo) {
  if (!confirm(`确定删除班级 ${classNo} 吗？`)) {
    return;
  }
  try {
    await del(`/class/${classNo}`);
    showToast('删除成功', 'success');
    await fetchClasses();
    // 如果当前页无数据且不是第一页，则回退
    const container = document.getElementById('class-list');
    if (container.innerHTML.includes('暂无数据') && currentPage > 1) {
      currentPage--;
      await fetchClasses();
    }
  } catch (err) {
    showToast('删除失败: ' + err.message, 'error');
  }
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