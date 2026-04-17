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