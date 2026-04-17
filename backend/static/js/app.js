import { showToast } from './utils.js';

// 检查登录状态
function checkAuth() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    // 未登录，跳转到登录页
    window.location.href = '/static/login.html';
    return false;
  }
  return true;
}

// 显示用户信息
function displayUserInfo() {
  const userInfo = localStorage.getItem('user_info');
  const userNameEl = document.getElementById('user-name');
  
  if (userInfo && userNameEl) {
    const user = JSON.parse(userInfo);
    userNameEl.textContent = user.full_name || user.username || user.email;
  }
}

// 退出登录
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('token_type');
  localStorage.removeItem('user_info');
  window.location.href = '/static/login.html';
}

// 模块映射
const modules = {
  student: () => import('./modules/student.js'),
  teacher: () => import('./modules/teacher.js'),
  class: () => import('./modules/class.js'),
  employment: () => import('./modules/employment.js'),
  score: () => import('./modules/score.js'),
  ai: () => import('./modules/ai.js'),
  userAdmin: () => import('./modules/userAdmin.js'),
};

// 显示管理员菜单（如果是超级用户）
function showAdminMenu() {
  const userInfo = localStorage.getItem('user_info');
  if (userInfo) {
    const user = JSON.parse(userInfo);
    const adminBtns = document.querySelectorAll('.nav-admin');
    if (user.is_superuser) {
      adminBtns.forEach(btn => btn.style.display = '');
    }
  }
}

let currentModule = null;

// 渲染指定模块
async function loadModule(moduleName) {
  const contentDiv = document.getElementById('app-content');
  if (!contentDiv) return;
  try {
    const moduleExports = await modules[moduleName]();
    const renderFn = moduleExports.default || moduleExports.render;
    if (typeof renderFn === 'function') {
      // 清空容器
      contentDiv.innerHTML = '';
      await renderFn(contentDiv);
      currentModule = moduleName;
      // 高亮导航按钮
      document.querySelectorAll('.nav-btn').forEach(btn => {
        if (btn.dataset.module === moduleName) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    } else {
      throw new Error('模块没有导出 render 函数');
    }
  } catch (err) {
    console.error(err);
    contentDiv.innerHTML = `<div class="card"><p style="color:red">加载模块失败: ${err.message}</p></div>`;
    showToast('模块加载错误', 'error');
  }
}

// 绑定导航事件
function bindNavigation() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const module = btn.dataset.module;
      if (module && modules[module]) {
        loadModule(module);
      }
    });
  });
}

// 初始加载
document.addEventListener('DOMContentLoaded', () => {
  // 检查登录状态
  if (!checkAuth()) {
    return;
  }
  
  // 显示用户信息
  displayUserInfo();
  
  // 显示管理员菜单
  showAdminMenu();
  
  // 绑定退出按钮
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
  
  // 绑定导航
  bindNavigation();
  
  // 默认加载学生模块
  loadModule('student');
});