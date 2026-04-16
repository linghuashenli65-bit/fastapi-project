import { API_BASE } from './config.js';
import { showToast } from './utils.js';

async function request(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };
  if (config.body && typeof config.body !== 'string') {
    config.body = JSON.stringify(config.body);
  }

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail?.[0]?.msg || `HTTP ${response.status}`;
      throw new Error(message);
    }
    // 对于 204 或空响应
    if (response.status === 204) return null;
    return await response.json();
  } catch (err) {
    showToast(err.message || '请求失败', 'error');
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