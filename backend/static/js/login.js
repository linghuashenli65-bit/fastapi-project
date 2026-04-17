/**
 * 登录页面 JavaScript
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
const loginForm = document.getElementById('login-form');
const loginBtn = document.getElementById('login-btn');
const errorMsg = document.getElementById('error-msg');

// 显示错误信息
function showError(message) {
  errorMsg.textContent = message;
  errorMsg.classList.add('show');
}

// 隐藏错误信息
function hideError() {
  errorMsg.textContent = '';
  errorMsg.classList.remove('show');
}

// 设置按钮加载状态
function setLoading(loading) {
  if (loading) {
    loginBtn.disabled = true;
    loginBtn.classList.add('loading');
    loginBtn.textContent = '登录中...';
  } else {
    loginBtn.disabled = false;
    loginBtn.classList.remove('loading');
    loginBtn.textContent = '登录';
  }
}

// 登录请求
async function login(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await fetch(`${API_BASE}/auth/jwt/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || '登录失败，请检查邮箱和密码');
  }

  return await response.json();
}

// 获取用户信息
async function getUserInfo(token) {
  const response = await fetch(`${API_BASE}/users/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('获取用户信息失败');
  }

  return await response.json();
}

// 处理表单提交
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideError();

  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;

  if (!email || !password) {
    showError('请输入邮箱和密码');
    return;
  }

  setLoading(true);

  try {
    // 1. 登录获取 token
    const authData = await login(email, password);
    
    // 2. 保存 token
    localStorage.setItem('access_token', authData.access_token);
    localStorage.setItem('token_type', authData.token_type);

    // 3. 获取用户信息
    const userInfo = await getUserInfo(authData.access_token);
    localStorage.setItem('user_info', JSON.stringify(userInfo));

    // 4. 登录成功，跳转到主页
    window.location.href = '/static/index.html';

  } catch (error) {
    console.error('登录错误:', error);
    showError(error.message || '登录失败，请稍后重试');
    setLoading(false);
  }
});

// 输入框聚焦时隐藏错误信息
document.getElementById('email').addEventListener('focus', hideError);
document.getElementById('password').addEventListener('focus', hideError);
