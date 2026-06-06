const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const ADMIN_TOKEN_KEY = 'admin_access_token';

class AdminApiError extends Error {
  constructor(message, status, errorCode) {
    super(message);
    this.name = 'AdminApiError';
    this.status = status;
    this.errorCode = errorCode;
  }
}

function getToken() {
  return localStorage.getItem(ADMIN_TOKEN_KEY) || localStorage.getItem('access_token') || localStorage.getItem('token') || '';
}

function toQuery(params = {}) {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      query.set(key, value);
    }
  });

  const queryString = query.toString();
  return queryString ? `?${queryString}` : '';
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const response = await fetch(`${API_BASE_URL}${path}${toQuery(options.query)}`, {
    method: options.method || 'GET',
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json') ? await response.json() : null;

  if (!response.ok) {
    const detail = typeof payload?.detail === 'object' ? payload.detail.detail : payload?.detail;
    const errorCode = payload?.error_code || payload?.detail?.error_code;
    const message = detail || '관리자 요청에 실패했습니다.';
    throw new AdminApiError(message, response.status, errorCode);
  }

  return payload;
}

export function setAccessToken(token) {
  localStorage.setItem(ADMIN_TOKEN_KEY, token);
  localStorage.setItem('access_token', token);
}

export function clearAccessToken() {
  localStorage.removeItem(ADMIN_TOKEN_KEY);
  localStorage.removeItem('access_token');
  localStorage.removeItem('token');
}

export async function loginAdmin(email, password) {
  const payload = await request('/api/auth/login', {
    method: 'POST',
    body: { email, password },
  });

  if (payload?.access_token) {
    setAccessToken(payload.access_token);
  }

  return payload;
}

function listPayload(payload, fallbackKey) {
  if (Array.isArray(payload)) {
    return { items: payload, total: payload.length, page: 1, limit: payload.length };
  }

  if (Array.isArray(payload?.items)) {
    return payload;
  }

  if (Array.isArray(payload?.[fallbackKey])) {
    return {
      items: payload[fallbackKey],
      total: payload.total ?? payload[fallbackKey].length,
      page: payload.page ?? 1,
      limit: payload.limit ?? payload[fallbackKey].length,
    };
  }

  return { items: [], total: 0, page: 1, limit: 0 };
}

function withFilteredItems(listLike, predicate) {
  const items = (listLike.items || []).filter(predicate);
  return {
    ...listLike,
    items,
    total: items.length,
    page: 1,
  };
}

export async function loadAdminSnapshot(filters = {}) {
  const [
    me,
    stats,
    systemStatus,
    recentParties,
    users,
    parties,
    recentMessages,
    actions,
    supportSummary,
    supportThreads,
  ] = await Promise.all([
    request('/api/auth/me'),
    request('/api/admin/stats'),
    request('/api/admin/system/status'),
    request('/api/admin/parties/recent', { query: { limit: 5 } }),
    request('/api/admin/users', {
      query: {
        page: 1,
        limit: 100,
        keyword: filters.userKeyword,
        include_deleted: filters.includeDeleted ? 'true' : '',
        role: filters.userRole === 'all' ? '' : filters.userRole,
        is_active: filters.userActive === 'all' ? '' : filters.userActive,
      },
    }),
    request('/api/admin/parties', {
      query: {
        page: 1,
        limit: 100,
        status: filters.partyStatus === 'all' ? '' : filters.partyStatus,
        keyword: filters.partyKeyword,
        include_deleted: filters.includeDeleted ? 'true' : '',
        creator_user_id: filters.creatorUserId,
        member_user_id: filters.memberUserId,
      },
    }),
    request('/api/admin/messages/recent', { query: { limit: 8 } }),
    request('/api/admin/actions', { query: { page: 1, limit: 10 } }),
    request('/api/admin/support/summary'),
    request('/api/admin/support/threads'),
  ]);

  let normalizedParties = listPayload(parties, 'parties');

  if (filters.creatorUserId) {
    normalizedParties = withFilteredItems(
      normalizedParties,
      (party) => String(party.creator_id) === String(filters.creatorUserId),
    );
  }

  if (filters.memberUserId) {
    try {
      const history = await request(`/api/admin/users/${filters.memberUserId}/parties`, {
        query: { role: 'all', page: 1, limit: 100 },
      });
      const partyIds = new Set((history.items || []).map((item) => item.party_id));
      normalizedParties = withFilteredItems(normalizedParties, (party) => partyIds.has(party.id));
    } catch (error) {
      if (error.status !== 404) throw error;
      normalizedParties = withFilteredItems(normalizedParties, () => false);
    }
  }

  return {
    currentUser: me?.user || me,
    stats,
    systemStatus,
    recentParties: Array.isArray(recentParties) ? recentParties : recentParties.items || recentParties.recent_parties || [],
    users: listPayload(users, 'users'),
    parties: normalizedParties,
    recentMessages: Array.isArray(recentMessages) ? recentMessages : recentMessages.items || recentMessages.recent_messages || [],
    actions: listPayload(actions, 'admin_actions'),
    supportSummary,
    supportThreads: listPayload(supportThreads, 'threads'),
  };
}

export function updateUserRole(userId, role, adminNote) {
  return request(`/api/admin/users/${userId}/role`, {
    method: 'PATCH',
    body: { role, admin_note: adminNote },
  });
}

export function updateUserStatus(userId, isActive, adminNote) {
  return request(`/api/admin/users/${userId}/status`, {
    method: 'PATCH',
    body: { is_active: isActive, admin_note: adminNote },
  });
}

export function updatePartyStatus(partyId, status, adminNote) {
  return request(`/api/admin/parties/${partyId}/status`, {
    method: 'PATCH',
    body: { status, admin_note: adminNote },
  });
}

export function getUserDetail(userId) {
  return request(`/api/admin/users/${userId}`);
}

export function getPartyDetail(partyId) {
  return request(`/api/admin/parties/${partyId}`);
}

export function createAdminUser(payload) {
  return request('/api/admin/users', {
    method: 'POST',
    body: payload,
  });
}

export function updateAdminUser(userId, payload) {
  return request(`/api/admin/users/${userId}`, {
    method: 'PATCH',
    body: payload,
  });
}

export function resetAdminUserPassword(userId, payload) {
  return request(`/api/admin/users/${userId}/password-reset`, {
    method: 'POST',
    body: payload,
  });
}

export function deleteAdminUser(userId, payload) {
  return request(`/api/admin/users/${userId}`, {
    method: 'DELETE',
    body: payload,
  });
}

export function loadAdminUserParties(userId, query = {}) {
  return request(`/api/admin/users/${userId}/parties`, { query });
}

export function createAdminParty(payload) {
  return request('/api/admin/parties', {
    method: 'POST',
    body: payload,
  });
}

export function updateAdminParty(partyId, payload) {
  return request(`/api/admin/parties/${partyId}`, {
    method: 'PATCH',
    body: payload,
  });
}

export function deleteAdminParty(partyId, payload) {
  return request(`/api/admin/parties/${partyId}`, {
    method: 'DELETE',
    body: payload,
  });
}

export function updateAdminPartyStatus(partyId, payload) {
  return request(`/api/admin/parties/${partyId}/status`, {
    method: 'PATCH',
    body: payload,
  });
}

export function addPartyMember(partyId, payload) {
  return request(`/api/admin/parties/${partyId}/members`, {
    method: 'POST',
    body: payload,
  });
}

export function removePartyMember(partyId, userId, payload) {
  return request(`/api/admin/parties/${partyId}/members/${userId}`, {
    method: 'DELETE',
    body: payload,
  });
}

export function recalculatePartyFare(partyId, payload) {
  return request(`/api/admin/parties/${partyId}/fare/recalculate`, {
    method: 'POST',
    body: payload,
  });
}

export function overridePartyFare(partyId, payload) {
  return request(`/api/admin/parties/${partyId}/fare`, {
    method: 'PATCH',
    body: payload,
  });
}

export function hideAdminMessage(messageId, payload) {
  return request(`/api/admin/messages/${messageId}`, {
    method: 'DELETE',
    body: payload,
  });
}

export function createPartyNotice(partyId, payload) {
  return request(`/api/admin/parties/${partyId}/messages/notice`, {
    method: 'POST',
    body: payload,
  });
}

export function loadSupportThread(threadId) {
  return request(`/api/admin/support/threads/${threadId}`);
}

export function sendSupportReply(threadId, payload) {
  return request(`/api/admin/support/threads/${threadId}/messages`, {
    method: 'POST',
    body: payload,
  });
}

export function updateSupportThreadStatus(threadId, payload) {
  return request(`/api/admin/support/threads/${threadId}/status`, {
    method: 'PATCH',
    body: payload,
  });
}

export { API_BASE_URL, AdminApiError };
