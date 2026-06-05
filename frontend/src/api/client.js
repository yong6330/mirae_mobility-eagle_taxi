const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');
const TOKEN_KEY = 'access_token';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(formatErrorDetail(body.detail) || `API 요청 실패: ${response.status}`);
  }

  if (response.status === 204) return null;
  return response.json();
}

export function getPartyChatWebSocketUrl(partyId) {
  const token = getToken();
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const query = token ? `?token=${encodeURIComponent(token)}` : '';

  return `${protocol}//${window.location.host}/ws/parties/${partyId}${query}`;
}

export const api = {
  register: (payload) => request('/api/auth/register', { method: 'POST', body: JSON.stringify(payload) }),
  login: (payload) => request('/api/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  me: () => request('/api/auth/me'),
  parties: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/parties${query ? `?${query}` : ''}`);
  },
  searchParties: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/parties/search${query ? `?${query}` : ''}`);
  },
  recommendParties: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/parties/recommend${query ? `?${query}` : ''}`);
  },
  createParty: (payload) => request('/api/parties', { method: 'POST', body: JSON.stringify(payload) }),
  partyDetail: (partyId) => request(`/api/parties/${partyId}`),
  joinParty: (partyId) => request(`/api/parties/${partyId}/join`, { method: 'POST' }),
  leaveParty: (partyId) => request(`/api/parties/${partyId}/leave`, { method: 'DELETE' }),
  cancelParty: (partyId, payload = {}) =>
    request(`/api/parties/${partyId}/cancel`, { method: 'PATCH', body: JSON.stringify(payload) }),
  myParties: () => request('/api/my/parties'),
  messages: (partyId) => request(`/api/parties/${partyId}/messages`),
  estimateFare: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/fares/estimate${query ? `?${query}` : ''}`);
  },
  adminStats: () => request('/api/admin/stats'),
};

function formatErrorDetail(detail) {
  if (!detail) return '';
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg || item?.message || JSON.stringify(item)).join('\n');
  }
  return detail.message || JSON.stringify(detail);
}
