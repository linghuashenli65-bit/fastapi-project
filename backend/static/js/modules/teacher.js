import { get, post, put, del } from '../api.js';
import { showToast, serializeForm, createModal } from '../utils.js';
import { DEFAULT_PAGE, DEFAULT_SIZE } from '../config.js';

let currentPage = DEFAULT_PAGE;
let currentSize = DEFAULT_SIZE;
let currentName = '';
let teachersCache = [];

export async function render(container) {
  container.innerHTML = `
        <div class="card">
            <h3>👩‍🏫 教师管理</h3>
            <div class="search-bar">
                <input type="text" id="search-name" placeholder="按姓名搜索" value="${escapeHtml(currentName)}">
                <button id="search-btn" class="btn btn-primary">🔍 搜索</button>
                <button id="add-teacher-btn" class="btn btn-primary">➕ 添加教师</button>
            </div>
            <div style="overflow-x: auto;">
                <div id="teacher-list"></div>
            </div>
            <div id="pagination" class="pagination"></div>
        </div>
    `;

  await fetchTeachers();

  document.getElementById('search-btn').onclick = () => {
    currentName = document.getElementById('search-name').value;
    currentPage = DEFAULT_PAGE;
    fetchTeachers();
  };
  document.getElementById('add-teacher-btn').onclick = showAddModal;
}

async function fetchTeachers() {
  try {
    console.log('正在请求教师列表...');
    const params = new URLSearchParams({
      page: currentPage,
      size: currentSize,
      name: currentName
    });
    const url = `/teacher/?${params.toString()}`;
    console.log('请求URL:', url);
    const data = await get(url);
    console.log('返回数据:', data);
    teachersCache = data.data || [];
    renderTeacherTable(teachersCache);
    renderPagination(data.count);
  } catch (err) {
    console.error('获取教师列表失败:', err);
    showToast('获取教师列表失败', 'error');
  }
}

function renderTeacherTable(teachers) {
  const container = document.getElementById('teacher-list');
  if (!teachers.length) {
    container.innerHTML = '<p>暂无数据</p>';
    return;
  }
  let html = `
        <table class="data-table">
            <thead>
                <tr><th>ID</th><th>教师编号</th><th>姓名</th><th>性别</th><th>电话</th><th>职称</th><th>操作</th></tr>
            </thead>
            <tbody>
    `;
  teachers.forEach(t => {
    html += `
            <tr>
                <td>${t.id}</td>
                <td>${escapeHtml(t.teacher_no || '')}</td>
                <td>${escapeHtml(t.name || '')}</td>
                <td>${t.gender === 'M' ? '男' : (t.gender === 'F' ? '女' : '')}</td>
                <td>${escapeHtml(t.phone || '')}</td>
                <td>${escapeHtml(t.title || '')}</td>
                <td>
                    <button class="btn btn-sm btn-primary edit-teacher" data-id="${t.id}">编辑</button>
                    <button class="btn btn-sm btn-danger delete-teacher" data-id="${t.id}">删除</button>
                </td>
            </tr>
        `;
  });
  html += `</tbody></table>`;
  container.innerHTML = html;

  document.querySelectorAll('.edit-teacher').forEach(btn => {
    btn.onclick = () => {
      const id = parseInt(btn.dataset.id);
      const teacher = teachersCache.find(t => t.id === id);
      if (teacher) showEditModal(teacher);
      else showToast('未找到教师数据', 'error');
    };
  });
  document.querySelectorAll('.delete-teacher').forEach(btn => {
    btn.onclick = () => deleteTeacher(btn.dataset.id);
  });
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
      fetchTeachers();
    };
  });
}

function showAddModal() {
  const formHtml = `
        <form id="teacher-form">
            <div class="form-group"><label>教师编号*</label><input name="teacher_no" required></div>
            <div class="form-group"><label>姓名*</label><input name="name" required></div>
            <div class="form-group"><label>性别</label>
                <select name="gender">
                    <option value="">请选择</option>
                    <option value="M">男</option>
                    <option value="F">女</option>
                </select>
            </div>
            <div class="form-group"><label>电话</label><input name="phone"></div>
            <div class="form-group"><label>职称</label><input name="title"></div>
        </form>
    `;
  createModal('添加教师', formHtml, async () => {
    const form = document.querySelector('#teacher-form');
    const data = serializeForm(form);
    if (!data.teacher_no || !data.name) {
      showToast('教师编号和姓名不能为空', 'error');
      return;
    }
    try {
      await post('/teacher/', data);
      showToast('添加成功', 'success');
      currentName = '';
      document.getElementById('search-name').value = '';
      currentPage = 1;
      fetchTeachers();
    } catch (err) {
      showToast('添加失败', 'error');
    }
  });
}

function showEditModal(teacher) {
  const formHtml = `
        <form id="edit-teacher-form">
            <div class="form-group"><label>教师编号</label><input name="teacher_no" value="${escapeHtml(teacher.teacher_no || '')}" readonly></div>
            <div class="form-group"><label>姓名*</label><input name="name" value="${escapeHtml(teacher.name || '')}" required></div>
            <div class="form-group"><label>性别</label>
                <select name="gender">
                    <option value="">请选择</option>
                    <option value="M" ${teacher.gender === 'M' ? 'selected' : ''}>男</option>
                    <option value="F" ${teacher.gender === 'F' ? 'selected' : ''}>女</option>
                </select>
            </div>
            <div class="form-group"><label>电话</label><input name="phone" value="${escapeHtml(teacher.phone || '')}"></div>
            <div class="form-group"><label>职称</label><input name="title" value="${escapeHtml(teacher.title || '')}"></div>
        </form>
    `;
  createModal('编辑教师', formHtml, async () => {
    const form = document.querySelector('#edit-teacher-form');
    const data = serializeForm(form);
    delete data.teacher_no; // 编号不可修改
    Object.keys(data).forEach(k => { if (data[k] === '') delete data[k]; });
    try {
      await put(`/teacher/${teacher.id}/`, data);
      showToast('更新成功', 'success');
      fetchTeachers();
    } catch (err) {
      showToast('更新失败', 'error');
    }
  });
}

async function deleteTeacher(id) {
  if (confirm('确定删除该教师吗？')) {
    try {
      await del(`/teacher/${id}/`);
      showToast('删除成功', 'success');
      await fetchTeachers();
      // 如果当前页无数据且不是第一页，回退
      const container = document.getElementById('teacher-list');
      if (container.innerHTML.includes('暂无数据') && currentPage > 1) {
        currentPage--;
        await fetchTeachers();
      }
    } catch (err) {
      showToast('删除失败', 'error');
    }
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