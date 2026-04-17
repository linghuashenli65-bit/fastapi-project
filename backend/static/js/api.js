import { API_BASE } from './config.js';
import { showToast } from './utils.js';

// 获取存储的 token
function getToken() {
  return localStorage.getItem('access_token');
}

async function request(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
  
  // 构建请求头
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  // 添加认证 token
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const config = {
    headers,
    ...options,
  };
  
  if (config.body && typeof config.body !== 'string') {
    config.body = JSON.stringify(config.body);
  }

  try {
    const response = await fetch(url, config);
    
    // 处理 401 未授权
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('token_type');
      localStorage.removeItem('user_info');
      window.location.href = '/static/login.html';
      throw new Error('登录已过期，请重新登录');
    }
    
    // 处理 403 禁止访问
    if (response.status === 403) {
      throw new Error('无权限访问，仅管理员可操作');
    }
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail?.[0]?.msg || errorData.detail || `HTTP ${response.status}`;
      throw new Error(message);
    }
    // 对于 204 或空响应
    if (response.status === 204) return null;
    return await response.json();
  } catch (err) {
    throw err;
  }
}

export function get(endpoint) {
  return request(endpoint, { method: 'GET' });
}

export function post(endpoint, data) {
  return request(endpoint, { method: 'POST', body: data });
}

export function put(endpoint, data) {
  return request(endpoint, { method: 'PUT', body: data });
}

export function del(endpoint) {
  return request(endpoint, { method: 'DELETE' });
}