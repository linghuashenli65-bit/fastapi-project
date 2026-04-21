// 消息提示
export function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerText = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 3000);
}

// 序列化表单数据为对象
export function serializeForm(formElement) {
  const formData = new FormData(formElement);
  const obj = {};
  formData.forEach((value, key) => {
    obj[key] = value;
  });
  return obj;
}

// 简单日期格式化 YYYY-MM-DD
export function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toISOString().slice(0, 10);
}

// 动态创建模态框
// 用法1: createModal(title, contentHtml, onConfirm)
// 用法2: createModal(fullHtmlContent, width) - 传入完整HTML和可选宽度
export function createModal(...args) {
  const modalDiv = document.createElement('div');
  modalDiv.className = 'modal-overlay';
  modalDiv.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:1000;';

  if (args.length === 1 && typeof args[0] === 'string') {
    // 完整 HTML 模式（无宽度）
    modalDiv.innerHTML = `<div class="modal-content" style="background:white;border-radius:16px;padding:24px;max-width:500px;width:90%;max-height:80vh;overflow-y:auto;">${args[0]}</div>`;
  } else if (args.length === 2 && typeof args[0] === 'string' && typeof args[1] === 'string') {
    // 完整 HTML + 宽度模式
    modalDiv.innerHTML = `<div class="modal-content" style="background:white;border-radius:16px;padding:24px;max-width:${args[1]};width:90%;max-height:80vh;overflow-y:auto;">${args[0]}</div>`;
  } else {
    // 传统模式: title, contentHtml, onConfirm
    const [title, contentHtml, onConfirm] = args;
    modalDiv.innerHTML = `
      <div class="modal-content" style="background:white;border-radius:16px;padding:24px;max-width:500px;width:90%;">
        <h3>${title}</h3>
        <div>${contentHtml}</div>
        <div style="margin-top:20px;display:flex;justify-content:flex-end;gap:12px;">
          <button class="btn btn-secondary" id="modal-cancel">取消</button>
          <button class="btn btn-primary" id="modal-confirm">确认</button>
        </div>
      </div>`;

    if (onConfirm) {
      modalDiv.querySelector('#modal-confirm').onclick = () => {
        onConfirm();
        modalDiv.remove();
      };
    }
  }

  document.body.appendChild(modalDiv);

  // 点击遮罩关闭
  modalDiv.onclick = (e) => {
    if (e.target === modalDiv) modalDiv.remove();
  };

  // 取消按钮关闭（传统模式）
  const cancelBtn = modalDiv.querySelector('#modal-cancel');
  if (cancelBtn) cancelBtn.onclick = () => modalDiv.remove();

  return modalDiv;
}

/**
 * 统一分页渲染函数（左侧信息，右侧按钮）
 * @param {string|HTMLElement} container - 分页容器元素或ID
 * @param {object} options - 配置项
 * @param {number} options.currentPage - 当前页码
 * @param {number} options.totalPages - 总页数
 * @param {number} options.total - 总条数
 * @param {number} options.pageSize - 每页条数
 * @param {function} options.onPageChange - 页码变化回调 (page) => void
 * @param {function} [options.onSizeChange] - 每页条数变化回调 (size) => void
 */
export function renderPagination(container, options) {
  const { currentPage, totalPages, total, pageSize = 10, onPageChange, onSizeChange } = options;
  const el = typeof container === 'string' ? document.getElementById(container) : container;
  if (!el) return;
  if (totalPages <= 0) {
    el.innerHTML = '';
    return;
  }

  // 左侧信息，右侧按钮组
  let html = `<div class="pagination-controls">`;
  html += `<span>共 ${total} 条，第 ${currentPage} / ${totalPages} 页</span>`;
  html += `<div class="pagination-buttons" style="margin-left: auto;">`;  // 添加内联样式
  html += `<button class="page-btn" data-action="first" ${currentPage === 1 ? 'disabled' : ''}>首页</button>`;
  html += `<button class="page-btn" data-action="prev" ${currentPage === 1 ? 'disabled' : ''}>上一页</button>`;
  html += `<span>跳至 <input type="number" class="page-jump" value="${currentPage}" min="1" max="${totalPages}"> 页</span>`;
  html += `<button class="page-btn" data-action="next" ${currentPage === totalPages ? 'disabled' : ''}>下一页</button>`;
  html += `<button class="page-btn" data-action="last" ${currentPage === totalPages ? 'disabled' : ''}>末页</button>`;
  html += `<select class="page-size-select">`;
  [10, 20, 50, 100].forEach(s => {
    html += `<option value="${s}" ${pageSize === s ? 'selected' : ''}>${s}条/页</option>`;
  });
  html += `</select></div></div>`;

  el.innerHTML = html;

  // 绑定按钮事件
  el.querySelectorAll('.page-btn:not([disabled])').forEach(btn => {
    btn.onclick = () => {
      const action = btn.dataset.action;
      let targetPage = currentPage;
      if (action === 'first') targetPage = 1;
      else if (action === 'prev') targetPage = currentPage - 1;
      else if (action === 'next') targetPage = currentPage + 1;
      else if (action === 'last') targetPage = totalPages;
      if (targetPage >= 1 && targetPage <= totalPages && targetPage !== currentPage) onPageChange(targetPage);
    };
  });

  // 绑定跳转输入框事件
  const jumpInput = el.querySelector('.page-jump');
  if (jumpInput) {
    jumpInput.onchange = () => {
      let p = parseInt(jumpInput.value);
      if (isNaN(p)) p = 1;
      p = Math.min(Math.max(p, 1), totalPages);
      if (p !== currentPage) onPageChange(p);
    };
  }

  // 绑定每页条数选择事件
  const sizeSelect = el.querySelector('.page-size-select');
  if (sizeSelect && onSizeChange) {
    sizeSelect.onchange = () => {
      onSizeChange(parseInt(sizeSelect.value));
    };
  }
}