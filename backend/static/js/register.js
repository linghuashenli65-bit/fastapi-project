/**
 * 注册页面 JavaScript
 */

const API_BASE = 'http://localhost:8000';

// 检查是否已登录
function checkAuth() {
  const token = localStorage.getItem('access_token');
  if (token) {
    // 已登录，跳转到主页
    window.location.href = '/static/index.html';
  }
}

// 页面加载时检查登录状态
checkAuth();

// 获取表单元素
const registerForm = document.getElementById('register-form');
const registerBtn = document.getElementById('register-btn');
const errorMsg = document.getElementById('error-msg');
const successMsg = document.getElementById('success-msg');

// 显示错误信息
function showError(message) {
  errorMsg.textContent = message;
  errorMsg.classList.add('show');
  successMsg.classList.remove('show');
}

// 显示成功信息
function showSuccess(message) {
  successMsg.textContent = message;
  successMsg.classList.add('show');
  errorMsg.classList.remove('show');
}

// 隐藏信息
function hideMessages() {
  errorMsg.classList.remove('show');
  successMsg.classList.remove('show');
}

// 设置按钮加载状态
function setLoading(loading) {
  if (loading) {
    registerBtn.disabled = true;
    registerBtn.classList.add('loading');
    registerBtn.textContent = '注册中...';
  } else {
    registerBtn.disabled = false;
    registerBtn.classList.remove('loading');
    registerBtn.textContent = '注册';
  }
}

// 注册请求
async function register(userData) {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || '注册失败，请检查输入信息');
  }

  return await response.json();
}

// 处理表单提交
registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideMessages();

  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const username = document.getElementById('username').value.trim();
  const full_name = document.getElementById('full_name').value.trim();
  const phone = document.getElementById('phone').value.trim();

  // 验证
  if (!email || !password) {
    showError('请填写邮箱和密码');
    return;
  }

  if (password.length < 6) {
    showError('密码至少需要6位');
    return;
  }

  setLoading(true);

  try {
    // 构建请求数据
    const userData = {
      email,
      password,
    };
    
    // 添加可选字段
    if (username) userData.username = username;
    if (full_name) userData.full_name = full_name;
    if (phone) userData.phone = phone;

    // 发送注册请求
    const result = await register(userData);
    
    showSuccess('注册成功！即将跳转到登录页面...');
    
    // 2秒后跳转到登录页
    setTimeout(() => {
      window.location.href = '/static/login.html';
    }, 2000);

  } catch (error) {
    console.error('注册错误:', error);
    showError(error.message || '注册失败，请稍后重试');
    setLoading(false);
  }
});

// 输入框聚焦时隐藏错误信息
document.querySelectorAll('input').forEach(input => {
  input.addEventListener('focus', hideMessages);
});
