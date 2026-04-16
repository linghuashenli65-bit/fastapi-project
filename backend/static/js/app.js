import { showToast } from './utils.js';

// 模块映射
const modules = {
  student: () => import('./modules/student.js'),
  teacher: () => import('./modules/teacher.js'),
  class: () => import('./modules/class.js'),
  employment: () => import('./modules/employment.js'),
  score: () => import('./modules/score.js'),
  ai: () => import('./modules/ai.js'),
};

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

// 初始加载学生模块
document.addEventListener('DOMContentLoaded', () => {
  bindNavigation();
  loadModule('student');
});