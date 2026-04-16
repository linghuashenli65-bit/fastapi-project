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
export function createModal(title, contentHtml, onConfirm) {
  const modalDiv = document.createElement('div');
  modalDiv.className = 'modal';
  modalDiv.innerHTML = `
        <div class="modal-content">
            <h3>${title}</h3>
            <div>${contentHtml}</div>
            <div style="margin-top: 20px; display: flex; justify-content: flex-end; gap: 12px;">
                <button class="btn btn-secondary" id="modal-cancel">取消</button>
                <button class="btn btn-primary" id="modal-confirm">确认</button>
            </div>
        </div>
    `;
  document.body.appendChild(modalDiv);
  const confirmBtn = modalDiv.querySelector('#modal-confirm');
  const cancelBtn = modalDiv.querySelector('#modal-cancel');
  const closeModal = () => modalDiv.remove();
  confirmBtn.onclick = () => {
    onConfirm();
    closeModal();
  };
  cancelBtn.onclick = closeModal;
  return modalDiv;
}