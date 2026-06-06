import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bell,
  Calculator,
  Car,
  CheckCircle2,
  CircleDot,
  Clock,
  Crown,
  Database,
  Eye,
  History,
  Inbox,
  KeyRound,
  ListChecks,
  MessageSquare,
  PencilLine,
  Power,
  RefreshCw,
  Search,
  Server,
  Send,
  ShieldCheck,
  Trash2,
  UserCog,
  UserPlus,
  Users,
  X,
} from 'lucide-react';
import {
  API_BASE_URL,
  addPartyMember,
  clearAccessToken,
  createAdminParty,
  createAdminUser,
  createPartyNotice,
  deleteAdminParty,
  deleteAdminUser,
  hideAdminMessage,
  getPartyDetail,
  getUserDetail,
  loginAdmin,
  loadAdminSnapshot,
  loadAdminUserParties,
  overridePartyFare,
  recalculatePartyFare,
  removePartyMember,
  resetAdminUserPassword,
  sendSupportReply,
  updateAdminParty,
  updateAdminPartyStatus,
  updateAdminUser,
  updateSupportThreadStatus,
  updateUserRole,
  updateUserStatus,
  loadSupportThread,
} from './api/adminApi.js';

const views = [
  { id: 'overview', label: '대시보드', icon: BarChart3 },
  { id: 'users', label: '사용자', icon: Users },
  { id: 'parties', label: '파티', icon: Car },
  { id: 'messages', label: '메시지', icon: MessageSquare },
  { id: 'support', label: '문의/신고', icon: Inbox },
  { id: 'actions', label: '조작 기록', icon: History },
];

const statusLabels = {
  recruiting: '모집 중',
  matched: '매칭 완료',
  canceled: '취소',
  expired: '만료',
  completed: '이용 완료',
};

const statusTone = {
  recruiting: 'teal',
  matched: 'olive',
  canceled: 'red',
  expired: 'amber',
  completed: 'blue',
};

const genderLabels = {
  male: '남성',
  female: '여성',
  none: '미표시',
};

const roleLabels = {
  admin: 'admin',
  user: 'user',
};

const actionTypeLabels = {
  user_create: 'user create',
  user_update: 'user update',
  user_role_update: 'user role',
  user_status_update: 'user status',
  user_password_reset: 'password reset',
  user_delete: 'user delete',
  party_create: 'party create',
  party_update: 'party update',
  party_delete: 'party delete',
  party_status_update: 'party status',
  party_member_add: 'member add',
  party_member_remove: 'member remove',
  party_fare_recalculate: 'fare recalculate',
  party_fare_override: 'fare override',
  message_hide: 'message hide',
  admin_notice_create: 'admin notice',
  support_status_update: 'support status',
  admin_login: 'admin login',
};

const targetTypeLabels = {
  user: 'user',
  party: 'party',
  party_member: 'party member',
  fare: 'fare',
  message: 'message',
  support_thread: 'support',
};

const emptyFilters = {
  userKeyword: '',
  userRole: 'all',
  userActive: 'all',
  partyKeyword: '',
  partyStatus: 'all',
  creatorUserId: '',
  memberUserId: '',
  includeDeleted: false,
};

const userCreateGenderOptions = [
  { value: '', label: 'select' },
  { value: 'male', label: 'male' },
  { value: 'female', label: 'female' },
];

const userEditGenderOptions = [
  { value: '', label: 'unchanged' },
  { value: 'male', label: 'male' },
  { value: 'female', label: 'female' },
];

const roleOptions = [
  { value: 'user', label: 'user' },
  { value: 'admin', label: 'admin' },
];

const partyStatusOptions = [
  { value: 'recruiting', label: 'recruiting' },
  { value: 'matched', label: 'matched' },
  { value: 'canceled', label: 'canceled' },
  { value: 'expired', label: 'expired' },
  { value: 'completed', label: 'completed' },
];

const genderRuleOptions = [
  { value: 'any', label: 'any' },
  { value: 'same_gender', label: 'same_gender' },
];

const noteField = { name: 'admin_note', label: 'Admin note', type: 'textarea', required: true };

function createEmptySnapshot() {
  return {
    currentUser: null,
    stats: {},
    systemStatus: {},
    recentParties: [],
    users: { items: [], total: 0, page: 1, limit: 20 },
    parties: { items: [], total: 0, page: 1, limit: 20 },
    recentMessages: [],
    actions: { items: [], total: 0, page: 1, limit: 20 },
    supportSummary: { total: 0, resolved: 0, in_progress: 0, open: 0 },
    supportThreads: { items: [], total: 0, page: 1, limit: 20 },
  };
}

function formatDate(value) {
  if (!value) return '-';

  try {
    return new Intl.DateTimeFormat('ko-KR', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function formatLongDate(value) {
  if (!value) return '-';

  try {
    return new Intl.DateTimeFormat('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function toDateTimeLocalValue(value) {
  if (!value) return '';

  try {
    const date = new Date(value);
    const pad = (number) => String(number).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
  } catch {
    return '';
  }
}

function toKstIso(value) {
  if (!value) return '';
  return value.includes('+') || value.endsWith('Z') ? value : `${value}:00+09:00`;
}

function formatWon(value) {
  if (value === undefined || value === null) return '-';
  const amount = Number(value || 0);
  return amount > 0 ? `${amount.toLocaleString('ko-KR')}원` : '요금 확인 중';
}

function formatSupportKind(value) {
  return value === 'report' ? '신고' : '문의';
}

function formatSupportStatus(value) {
  const labels = {
    open: '접수',
    in_progress: '진행 중',
    resolved: '완료',
  };
  return labels[value] || value || '접수';
}

function formatSystemStatus(value, isLoading) {
  if (isLoading) return 'checking';
  if (!value || value === 'unknown') return 'unknown';
  return value;
}

function getItems(listLike) {
  if (Array.isArray(listLike)) return listLike;
  return listLike?.items || [];
}

function normalizeText(value) {
  return String(value || '').toLowerCase().trim();
}

const avatarPalette = [
  { bg: '#eff6ff', fg: '#1d4ed8', border: '#bfdbfe' },
  { bg: '#ecfdf5', fg: '#047857', border: '#bbf7d0' },
  { bg: '#f8fafc', fg: '#334155', border: '#cbd5e1' },
  { bg: '#fffbeb', fg: '#b45309', border: '#fde68a' },
  { bg: '#f5f3ff', fg: '#6d28d9', border: '#ddd6fe' },
];

function getAdminInitial(user = {}) {
  const source = user.name || user.email || '관리자';
  return source.trim().slice(0, 1).toUpperCase();
}

function getAvatarStyle(user = {}) {
  const source = `${user.email || ''}${user.name || ''}`;
  const hash = [...source].reduce((total, character) => total + character.charCodeAt(0), 0);
  const color = avatarPalette[hash % avatarPalette.length];
  return {
    '--avatar-bg': color.bg,
    '--avatar-fg': color.fg,
    '--avatar-border': color.border,
  };
}

function App() {
  const [activeView, setActiveView] = useState('overview');
  const [snapshot, setSnapshot] = useState(() => createEmptySnapshot());
  const [mode, setMode] = useState('loading');
  const [filters, setFilters] = useState(emptyFilters);
  const [loadError, setLoadError] = useState('');
  const [toast, setToast] = useState('');
  const [actionDialog, setActionDialog] = useState(null);
  const [maintenanceDialog, setMaintenanceDialog] = useState(null);
  const [detailDrawer, setDetailDrawer] = useState(null);
  const [pendingAction, setPendingAction] = useState(false);
  const [pendingMaintenance, setPendingMaintenance] = useState(false);
  const [selectedSupportThread, setSelectedSupportThread] = useState(null);
  const [supportDraft, setSupportDraft] = useState('');

  const users = getItems(snapshot.users);
  const parties = getItems(snapshot.parties);
  const recentMessages = getItems(snapshot.recentMessages);
  const actions = getItems(snapshot.actions);
  const supportThreads = getItems(snapshot.supportThreads);
  const currentUser = snapshot.currentUser || {};

  const activeAdminCount = users.filter((user) => user.role === 'admin' && user.is_active).length;

  const visibleUsers = useMemo(() => {
    const keyword = normalizeText(filters.userKeyword);

    return users.filter((user) => {
      const target = `${user.name} ${user.email} ${user.role}`.toLowerCase();
      const matchesKeyword = !keyword || target.includes(keyword);
      const matchesRole = filters.userRole === 'all' || user.role === filters.userRole;
      const matchesActive = filters.userActive === 'all' || String(Boolean(user.is_active)) === filters.userActive;
      const matchesDeleted = filters.includeDeleted || !user.is_deleted;
      return matchesKeyword && matchesRole && matchesActive && matchesDeleted;
    });
  }, [filters.includeDeleted, filters.userActive, filters.userKeyword, filters.userRole, users]);

  const visibleParties = useMemo(() => {
    const keyword = normalizeText(filters.partyKeyword);

    return parties.filter((party) => {
      const matchesStatus = filters.partyStatus === 'all' || party.status === filters.partyStatus;
      const matchesCreator = !filters.creatorUserId || String(party.creator_id) === String(filters.creatorUserId);
      const target = `${party.start_place} ${party.end_place} ${party.creator_name} ${party.status}`.toLowerCase();
      const matchesKeyword = !keyword || target.includes(keyword);
      return matchesStatus && matchesCreator && matchesKeyword;
    });
  }, [filters.creatorUserId, filters.partyKeyword, filters.partyStatus, parties]);

  useEffect(() => {
    loadDashboard();
  }, []);

  useEffect(() => {
    if (mode !== 'live') return undefined;

    const timer = window.setTimeout(() => {
      loadDashboard();
    }, 250);

    return () => window.clearTimeout(timer);
  }, [
    filters.userKeyword,
    filters.userRole,
    filters.userActive,
    filters.partyKeyword,
    filters.partyStatus,
    filters.creatorUserId,
    filters.memberUserId,
    filters.includeDeleted,
  ]);

  async function loadDashboard() {
    setMode('loading');
    setLoadError('');

    try {
      const liveSnapshot = await loadAdminSnapshot(filters);

      if (liveSnapshot.currentUser?.role !== 'admin') {
        setLoadError('관리자 권한이 필요합니다.');
        clearAccessToken();
        setSnapshot(createEmptySnapshot());
        setMode('forbidden');
        if (window.location.pathname !== '/login') {
          window.history.replaceState({}, '', '/login');
        }
        return false;
      }

      setSnapshot(liveSnapshot);
      setMode('live');
      if (window.location.pathname !== '/admin') {
        window.history.replaceState({}, '', '/admin');
      }
      return true;
    } catch (error) {
      if (error?.status === 401) {
        clearAccessToken();
      }

      if (error?.status === 403) {
        clearAccessToken();
      }

      setSnapshot(createEmptySnapshot());
      setMode(error?.status === 401 ? 'auth' : error?.status === 403 ? 'forbidden' : 'error');
      setLoadError(error?.status === 401 ? '' : error?.status ? `${error.status} ${error.message}` : '운영 서버에 연결할 수 없습니다.');
      if ((error?.status === 401 || error?.status === 403) && window.location.pathname !== '/login') {
        window.history.replaceState({}, '', '/login');
      }
      return false;
    }
  }

  async function openSupportThread(thread) {
    setSelectedSupportThread({ ...thread, loading: true });
    setSupportDraft('');
    try {
      const detail = await loadSupportThread(thread.id);
      setSelectedSupportThread(detail);
    } catch (error) {
      showToast(error.message || '문의 상세를 불러오지 못했습니다.');
      setSelectedSupportThread(thread);
    }
  }

  async function handleSupportReply(event) {
    event.preventDefault();
    if (!selectedSupportThread || !supportDraft.trim()) return;

    try {
      const detail = await sendSupportReply(selectedSupportThread.id, { content: supportDraft.trim() });
      setSelectedSupportThread(detail);
      setSupportDraft('');
      await loadDashboard();
      showToast('답변을 전송했습니다.');
    } catch (error) {
      showToast(error.message || '답변 전송에 실패했습니다.');
    }
  }

  async function handleSupportStatus(statusValue) {
    if (!selectedSupportThread) return;

    try {
      const detail = await updateSupportThreadStatus(selectedSupportThread.id, { status: statusValue });
      setSelectedSupportThread(detail);
      await loadDashboard();
      showToast('상태가 변경되었습니다.');
    } catch (error) {
      showToast(error.message || '상태 변경에 실패했습니다.');
    }
  }

  async function handleLogin(email, password) {
    setLoadError('');
    try {
      await loginAdmin(email, password);
      const allowed = await loadDashboard();
      if (allowed) {
        showToast('관리자 로그인이 완료되었습니다.');
      }
    } catch (error) {
      if (error?.status === 403) {
        clearAccessToken();
      }

      setMode(error?.status === 403 ? 'forbidden' : 'auth');
      setLoadError(error?.status ? `${error.status} ${error.message}` : '로그인 요청에 실패했습니다.');
    }
  }

  function handleLogout() {
    clearAccessToken();
    setSnapshot(createEmptySnapshot());
    setDetailDrawer(null);
    setMode('auth');
    setLoadError('로그아웃했습니다.');
    if (window.location.pathname !== '/login') {
      window.history.replaceState({}, '', '/login');
    }
  }

  function showToast(message) {
    setToast(message);
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => setToast(''), 3200);
  }

  function isProtectedMaster(user) {
    return Boolean(user?.master_admin);
  }

  function isLastActiveAdmin(user) {
    return user?.role === 'admin' && user?.is_active && activeAdminCount <= 1;
  }

  function openUserRoleDialog(user) {
    if (!currentUser.master_admin) {
      showToast('마스터 관리자만 권한을 변경할 수 있습니다.');
      return;
    }

    if (isProtectedMaster(user)) {
      showToast('마스터 관리자 계정은 변경할 수 없습니다.');
      return;
    }

    if (user.role === 'admin' && user.is_active && activeAdminCount <= 1) {
      showToast('마지막 관리자 계정은 강등하거나 비활성화할 수 없습니다.');
      return;
    }

    setDetailDrawer(null);
    setActionDialog({
      kind: 'user-role',
      title: '사용자 권한 변경',
      targetLabel: `${user.name} · ${user.email}`,
      value: user.role === 'admin' ? 'user' : 'admin',
      options: [
        { value: 'user', label: 'user' },
        { value: 'admin', label: 'admin' },
      ],
      target: user,
      note: user.role === 'admin' ? '관리자 권한 회수' : '관리자 권한 부여',
    });
  }

  function openUserStatusDialog(user) {
    if (isProtectedMaster(user)) {
      showToast('마스터 관리자 계정은 변경할 수 없습니다.');
      return;
    }

    if (isLastActiveAdmin(user)) {
      showToast('마지막 관리자 계정은 강등하거나 비활성화할 수 없습니다.');
      return;
    }

    setDetailDrawer(null);
    setActionDialog({
      kind: 'user-status',
      title: '사용자 활성 상태 변경',
      targetLabel: `${user.name} · ${user.email}`,
      value: user.is_active ? 'inactive' : 'active',
      options: [
        { value: 'active', label: '활성' },
        { value: 'inactive', label: '비활성' },
      ],
      target: user,
      note: user.is_active ? '운영 기준에 따른 비활성화' : '계정 활성화',
    });
  }

  function openPartyStatusDialog(party) {
    const statusOptions = currentUser.master_admin
      ? [
          { value: 'recruiting', label: '모집 중' },
          { value: 'matched', label: '매칭 완료' },
          { value: 'canceled', label: '취소' },
          { value: 'expired', label: '만료' },
          { value: 'completed', label: '이용 완료' },
        ]
      : [
          { value: 'canceled', label: '취소' },
          { value: 'expired', label: '만료' },
          { value: 'completed', label: '이용 완료' },
        ];

    setDetailDrawer(null);
    setActionDialog({
      kind: 'party-status',
      title: '파티 상태 변경',
      targetLabel: `#${party.id} ${party.start_place} → ${party.end_place}`,
      value: party.status,
      options: statusOptions,
      allowForce: currentUser.master_admin,
      target: party,
      note: '관리자 확인 후 상태 처리',
    });
  }

  async function openUserDetail(user) {
    setDetailDrawer({
      kind: 'user',
      title: `User #${user.id}`,
      loading: true,
      error: '',
      data: null,
      summary: user,
    });

    try {
      const data = await getUserDetail(user.id);
      let partyHistory = null;
      let partyHistoryError = '';

      try {
        partyHistory = await loadAdminUserParties(user.id, { role: 'all', page: 1, limit: 10 });
      } catch (historyError) {
        partyHistoryError = historyError?.errorCode || historyError?.message || '사용자 파티 이력 API 대기 중';
      }

      setDetailDrawer({
        kind: 'user',
        title: `User #${user.id}`,
        loading: false,
        error: '',
        data: { ...data, partyHistory, partyHistoryError },
        summary: user,
      });
    } catch (error) {
      setDetailDrawer({
        kind: 'user',
        title: `User #${user.id}`,
        loading: false,
        error: error.message || '사용자 상세를 불러오지 못했습니다.',
        data: null,
        summary: user,
      });
    }
  }

  async function openPartyDetail(party) {
    setDetailDrawer({
      kind: 'party',
      title: `Party #${party.id}`,
      loading: true,
      error: '',
      data: null,
      summary: party,
    });

    try {
      const data = await getPartyDetail(party.id);
      setDetailDrawer({
        kind: 'party',
        title: `Party #${party.id}`,
        loading: false,
        error: '',
        data,
        summary: party,
      });
    } catch (error) {
      setDetailDrawer({
        kind: 'party',
        title: `Party #${party.id}`,
        loading: false,
        error: error.message || '파티 상세를 불러오지 못했습니다.',
        data: null,
        summary: party,
      });
    }
  }

  function requireMasterAction() {
    if (!currentUser.master_admin) {
      showToast('마스터 관리자 권한이 필요한 작업입니다.');
      return false;
    }

    return true;
  }

  function openMaintenance(config) {
    if (config.masterOnly && !requireMasterAction()) return;
    setActionDialog(null);
    setDetailDrawer(null);
    setMaintenanceDialog(config);
  }

  async function submitMaintenance(values) {
    if (!maintenanceDialog) return;
    setPendingMaintenance(true);

    try {
      await maintenanceDialog.submit(values);
      await loadDashboard();
      showToast('관리 작업이 완료되었습니다.');
      setMaintenanceDialog(null);
      setDetailDrawer(null);
    } catch (error) {
      const message = error?.errorCode ? `${error.errorCode}: ${error.message}` : error.message;
      showToast(message || '관리 작업을 완료하지 못했습니다.');
    } finally {
      setPendingMaintenance(false);
    }
  }

  function openCreateUserDialog() {
    openMaintenance({
      title: '사용자 추가',
      masterOnly: true,
      fields: [
        { name: 'email', label: 'Email', type: 'email', required: true },
        { name: 'password', label: 'Temporary password', type: 'password', required: true },
        { name: 'name', label: 'Name', required: true },
        { name: 'gender', label: 'Gender', type: 'select', options: userCreateGenderOptions, required: true },
        { name: 'role', label: 'Role', type: 'select', options: roleOptions, defaultValue: 'user' },
        { name: 'is_active', label: 'Active', type: 'checkbox', defaultValue: true },
        noteField,
      ],
      submit: createAdminUser,
    });
  }

  function openEditUserDialog(user) {
    openMaintenance({
      title: `사용자 수정 #${user.id}`,
      masterOnly: true,
      fields: [
        { name: 'email', label: 'Email', type: 'email', defaultValue: user.email },
        { name: 'name', label: 'Name', defaultValue: user.name },
        { name: 'gender', label: 'Gender', type: 'select', options: userEditGenderOptions, defaultValue: ['male', 'female'].includes(user.gender) ? user.gender : '' },
        { name: 'role', label: 'Role', type: 'select', options: roleOptions, defaultValue: user.role || 'user' },
        { name: 'is_active', label: 'Active', type: 'checkbox', defaultValue: Boolean(user.is_active) },
        noteField,
      ],
      submit: (payload) => updateAdminUser(user.id, payload),
    });
  }

  function openResetPasswordDialog(user) {
    openMaintenance({
      title: `비밀번호 초기화 #${user.id}`,
      masterOnly: true,
      fields: [
        { name: 'new_password', label: 'New password', type: 'password', required: true },
        { name: 'force_logout', label: 'Force logout', type: 'checkbox', defaultValue: true },
        noteField,
      ],
      submit: (payload) => resetAdminUserPassword(user.id, payload),
    });
  }

  function openDeleteUserDialog(user) {
    openMaintenance({
      title: `사용자 삭제 처리 #${user.id}`,
      masterOnly: true,
      fields: [
        { name: 'delete_mode', label: 'Delete mode', type: 'select', options: [{ value: 'soft', label: 'soft' }], defaultValue: 'soft' },
        noteField,
      ],
      submit: (payload) => deleteAdminUser(user.id, payload),
    });
  }

  function openCreatePartyDialog() {
    openMaintenance({
      title: '파티 생성',
      masterOnly: true,
      fields: [
        { name: 'creator_user_id', label: 'Creator user ID', type: 'number', required: true },
        { name: 'start_place', label: 'Start place', required: true },
        { name: 'start_lat', label: 'Start lat', type: 'number', required: true },
        { name: 'start_lng', label: 'Start lng', type: 'number', required: true },
        { name: 'end_place', label: 'End place', required: true },
        { name: 'end_lat', label: 'End lat', type: 'number', required: true },
        { name: 'end_lng', label: 'End lng', type: 'number', required: true },
        { name: 'departure_time', label: 'Departure time', type: 'datetime-local', required: true },
        { name: 'meeting_point', label: 'Meeting point' },
        { name: 'meeting_note', label: 'Meeting note', type: 'textarea' },
        { name: 'max_members', label: 'Max members', type: 'number', defaultValue: 4 },
        { name: 'gender_rule', label: 'Gender rule', type: 'select', options: genderRuleOptions, defaultValue: 'any' },
        { name: 'initial_member_ids', label: 'Initial member IDs', type: 'csvNumbers' },
        { name: 'status', label: 'Status', type: 'select', options: partyStatusOptions.slice(0, 2), defaultValue: 'recruiting' },
        { name: 'force', label: 'Force', type: 'checkbox' },
        noteField,
      ],
      submit: createAdminParty,
    });
  }

  function openEditPartyDialog(party) {
    openMaintenance({
      title: `파티 수정 #${party.id}`,
      masterOnly: true,
      fields: [
        { name: 'creator_user_id', label: 'Creator user ID', type: 'number', defaultValue: party.creator_id || '' },
        { name: 'start_place', label: 'Start place', defaultValue: party.start_place },
        { name: 'start_lat', label: 'Start lat', type: 'number', defaultValue: party.start_lat || '' },
        { name: 'start_lng', label: 'Start lng', type: 'number', defaultValue: party.start_lng || '' },
        { name: 'end_place', label: 'End place', defaultValue: party.end_place },
        { name: 'end_lat', label: 'End lat', type: 'number', defaultValue: party.end_lat || '' },
        { name: 'end_lng', label: 'End lng', type: 'number', defaultValue: party.end_lng || '' },
        { name: 'departure_time', label: 'Departure time', type: 'datetime-local', defaultValue: toDateTimeLocalValue(party.departure_time) },
        { name: 'meeting_point', label: 'Meeting point', defaultValue: party.meeting_point || '' },
        { name: 'meeting_note', label: 'Meeting note', type: 'textarea', defaultValue: party.meeting_note || '' },
        { name: 'max_members', label: 'Max members', type: 'number', defaultValue: party.max_members || 4 },
        { name: 'gender_rule', label: 'Gender rule', type: 'select', options: genderRuleOptions, defaultValue: party.gender_rule || 'any' },
        { name: 'recalculate_fare', label: 'Recalculate fare', type: 'checkbox', defaultValue: false },
        { name: 'force', label: 'Force', type: 'checkbox', defaultValue: false },
        noteField,
      ],
      submit: (payload) => updateAdminParty(party.id, payload),
    });
  }

  function openDeletePartyDialog(party) {
    openMaintenance({
      title: `파티 삭제 처리 #${party.id}`,
      masterOnly: true,
      fields: [
        { name: 'delete_mode', label: 'Delete mode', type: 'select', options: [{ value: 'soft', label: 'soft' }], defaultValue: 'soft' },
        noteField,
      ],
      submit: (payload) => deleteAdminParty(party.id, payload),
    });
  }

  function openAddMemberDialog(party) {
    openMaintenance({
      title: `참여자 추가 #${party.id}`,
      masterOnly: true,
      fields: [
        { name: 'user_id', label: 'User ID', type: 'number', required: true },
        { name: 'force', label: 'Force', type: 'checkbox' },
        noteField,
      ],
      submit: (payload) => addPartyMember(party.id, payload),
    });
  }

  function openRemoveMemberDialog(party, member) {
    openMaintenance({
      title: `참여자 삭제 #${party.id} / user #${member.id}`,
      masterOnly: true,
      fields: [noteField],
      submit: (payload) => removePartyMember(party.id, member.id, payload),
    });
  }

  function openRecalculateFareDialog(party) {
    openMaintenance({
      title: `요금 재산정 #${party.id}`,
      masterOnly: true,
      fields: [noteField],
      submit: (payload) => recalculatePartyFare(party.id, payload),
    });
  }

  function openOverrideFareDialog(party) {
    openMaintenance({
      title: `요금 수동 보정 #${party.id}`,
      masterOnly: true,
      fields: [
        { name: 'estimated_fare', label: 'Estimated fare', type: 'number', required: true },
        { name: 'toll_fare', label: 'Toll fare', type: 'number', defaultValue: 0 },
        { name: 'distance_meters', label: 'Distance meters', type: 'number', required: true },
        { name: 'duration_seconds', label: 'Duration seconds', type: 'number', required: true },
        noteField,
      ],
      submit: (payload) => overridePartyFare(party.id, payload),
    });
  }

  function openCreateNoticeDialog(party) {
    openMaintenance({
      title: `파티 공지 생성 #${party.id}`,
      masterOnly: true,
      fields: [
        { name: 'content', label: 'Notice content', type: 'textarea', required: true },
        noteField,
      ],
      submit: (payload) => createPartyNotice(party.id, payload),
    });
  }

  function openHideMessageDialog(message) {
    openMaintenance({
      title: `메시지 숨김 #${message.id}`,
      masterOnly: true,
      fields: [noteField],
      submit: (payload) => hideAdminMessage(message.id, payload),
    });
  }

  async function confirmAction(value, note, force = false) {
    if (!actionDialog) return;
    setPendingAction(true);

    try {
      if (actionDialog.kind === 'user-role') {
        await updateUserRole(actionDialog.target.id, value, note);
      }

      if (actionDialog.kind === 'user-status') {
        await updateUserStatus(actionDialog.target.id, value === 'active', note);
      }

      if (actionDialog.kind === 'party-status') {
        await updateAdminPartyStatus(actionDialog.target.id, {
          status: value,
          force,
          admin_note: note,
        });
      }

      await loadDashboard();
      showToast('관리 작업이 반영되었습니다.');
      setActionDialog(null);
      setDetailDrawer(null);
    } catch (error) {
      const message = error?.errorCode ? `${error.errorCode}: ${error.message}` : error.message;
      showToast(message || '관리 작업을 완료하지 못했습니다.');
    } finally {
      setPendingAction(false);
    }
  }

  if (mode === 'auth' || mode === 'forbidden') {
    return (
      <AuthScreen
        mode={mode}
        message={loadError}
        onLogin={handleLogin}
      />
    );
  }

  if (mode === 'error') {
    return (
      <AuthScreen
        mode={mode}
        message={loadError}
        onLogin={handleLogin}
      />
    );
  }

  return (
    <div className="admin-shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark">
            <img src="/assets/eagle-taxi-logo.png" alt="" />
          </div>
          <div>
            <strong>독수리 택시</strong>
            <span>관리자 콘솔</span>
          </div>
        </div>

        <nav className="view-nav" aria-label="관리자 메뉴">
          {views.map((view) => {
            const Icon = view.icon;
            return (
              <button
                key={view.id}
                type="button"
                className={activeView === view.id ? 'active' : ''}
                onClick={() => setActiveView(view.id)}
              >
                <Icon size={18} aria-hidden="true" />
                {view.label}
              </button>
            );
          })}
        </nav>

        <div className="operator-card">
          <div className="operator-row">
            <span className="avatar logo-avatar" aria-hidden="true">
              <img src="/assets/eagle-taxi-logo.png" alt="" />
            </span>
            <div>
              <strong>{currentUser.name || '관리자'}</strong>
              <span>{currentUser.email || 'admin'}</span>
            </div>
          </div>
          <div className="operator-badges">
            <Badge tone="teal">{roleLabels[currentUser.role] || '관리자'}</Badge>
            {currentUser.master_admin && <Badge tone="amber">마스터 관리자</Badge>}
          </div>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Admin Console</p>
            <h1>{views.find((view) => view.id === activeView)?.label}</h1>
          </div>
          <div className="topbar-actions">
            <span className={`data-mode ${mode === 'live' ? 'live' : 'needs-api'}`}>
              <CircleDot size={14} aria-hidden="true" />
              {mode === 'loading' ? 'checking' : mode === 'live' ? 'API connected' : 'auth required'}
            </span>
            <button type="button" className="primary-action" onClick={loadDashboard}>
              <RefreshCw size={17} aria-hidden="true" />
              새로고침
            </button>
            {mode === 'live' && (
              <button type="button" className="ghost-button" onClick={handleLogout}>
                로그아웃
              </button>
            )}
          </div>
        </header>

        {loadError && (
          <div className="notice">
            <AlertTriangle size={18} aria-hidden="true" />
            <span>{loadError}</span>
            <small>{API_BASE_URL}</small>
          </div>
        )}

        {(mode === 'live' || mode === 'loading') && activeView === 'support' && (
          <SupportInboxView
            draft={supportDraft}
            selectedThread={selectedSupportThread}
            threads={supportThreads}
            onDraftChange={setSupportDraft}
            onRefresh={loadDashboard}
            onReply={handleSupportReply}
            onSelectThread={openSupportThread}
            onStatusChange={handleSupportStatus}
            onViewParty={openPartyDetail}
            onViewUser={openUserDetail}
          />
        )}

        {(mode === 'live' || mode === 'loading') && activeView === 'overview' && (
          <Overview
            snapshot={snapshot}
            mode={mode}
            onViewParty={openPartyDetail}
            onChangePartyStatus={openPartyStatusDialog}
            onRefresh={loadDashboard}
          />
        )}

        {(mode === 'live' || mode === 'loading') && activeView === 'users' && (
          <UsersView
            users={visibleUsers}
            filters={filters}
            setFilters={setFilters}
            currentUser={currentUser}
            activeAdminCount={activeAdminCount}
            onCreate={openCreateUserDialog}
            onDetail={openUserDetail}
            onRoleChange={openUserRoleDialog}
            onStatusChange={openUserStatusDialog}
          />
        )}

        {(mode === 'live' || mode === 'loading') && activeView === 'parties' && (
          <PartiesView
            parties={visibleParties}
            filters={filters}
            setFilters={setFilters}
            currentUser={currentUser}
            onCreate={openCreatePartyDialog}
            onDetail={openPartyDetail}
            onStatusChange={openPartyStatusDialog}
          />
        )}

        {(mode === 'live' || mode === 'loading') && activeView === 'messages' && (
          <MessagesView
            messages={recentMessages}
            currentUser={currentUser}
            onHideMessage={openHideMessageDialog}
          />
        )}

        {(mode === 'live' || mode === 'loading') && activeView === 'actions' && <ActionsView actions={actions} />}
      </main>

      {actionDialog && (
        <ActionDialog
          dialog={actionDialog}
          pending={pendingAction}
          onClose={() => setActionDialog(null)}
          onConfirm={confirmAction}
        />
      )}

      {maintenanceDialog && (
        <MaintenanceDialog
          dialog={maintenanceDialog}
          pending={pendingMaintenance}
          onClose={() => setMaintenanceDialog(null)}
          onConfirm={submitMaintenance}
        />
      )}

      {detailDrawer && (
        <DetailDrawer
          drawer={detailDrawer}
          currentUser={currentUser}
          activeAdminCount={activeAdminCount}
          onClose={() => setDetailDrawer(null)}
          onChangeUserRole={openUserRoleDialog}
          onChangeUserStatus={openUserStatusDialog}
          onEditUser={openEditUserDialog}
          onResetPassword={openResetPasswordDialog}
          onDeleteUser={openDeleteUserDialog}
          onChangePartyStatus={openPartyStatusDialog}
          onEditParty={openEditPartyDialog}
          onDeleteParty={openDeletePartyDialog}
          onAddMember={openAddMemberDialog}
          onRemoveMember={openRemoveMemberDialog}
          onRecalculateFare={openRecalculateFareDialog}
          onOverrideFare={openOverrideFareDialog}
          onCreateNotice={openCreateNoticeDialog}
        />
      )}

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}

function AuthScreen({ mode, message, onLogin }) {
  const title = mode === 'forbidden' ? '관리자 권한이 필요합니다.' : mode === 'error' ? '서버 연결을 확인하세요.' : '관리자 로그인';
  const description = mode === 'forbidden'
    ? 'role이 admin인 계정으로 다시 로그인하세요.'
    : mode === 'error'
      ? 'API 서버와 DB 연결 상태를 확인한 뒤 다시 시도하세요.'
      : '서비스 운영 권한이 있는 계정으로 접속하세요.';

  return (
    <main className="auth-screen">
      <section className="auth-panel">
        <div className="auth-brand">
          <img src="/assets/eagle-taxi-logo.png" alt="독수리 택시" />
          <strong>독수리 택시</strong>
          <span>Admin Console</span>
        </div>
        <div className="auth-heading">
          <h1>{title}</h1>
          <p>{description}</p>
        </div>
        {message && (
          <div className="auth-notice">
            <AlertTriangle size={17} aria-hidden="true" />
            <span>{message}</span>
          </div>
        )}
        <LoginPanel onLogin={onLogin} />
      </section>
    </main>
  );
}

function LoginPanel({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [pending, setPending] = useState(false);

  async function submitLogin(event) {
    event.preventDefault();
    setPending(true);
    try {
      await onLogin(email, password);
    } finally {
      setPending(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={submitLogin}>
        <label>
          <span>이메일</span>
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label>
          <span>비밀번호</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        <button type="submit" className="primary-action" disabled={pending}>
          <ShieldCheck size={17} aria-hidden="true" />
          로그인
        </button>
    </form>
  );
}

function BlockingPanel({ icon: Icon, title }) {
  return (
    <section className="auth-panel">
      <Icon size={28} aria-hidden="true" />
      <h2>{title}</h2>
      <p>관리자 권한과 운영 서버 상태를 확인한 뒤 다시 시도해 주세요.</p>
    </section>
  );
}

function Overview({ snapshot, mode, onViewParty, onChangePartyStatus, onRefresh }) {
  const stats = snapshot.stats || {};
  const system = snapshot.systemStatus || {};
  const supportSummary = snapshot.supportSummary || {};
  const recentParties = getItems(snapshot.recentParties);
  const parties = getItems(snapshot.parties);
  const partyTotal = Math.max(parties.length, 1);

  const primaryMetrics = [
    { label: '사용자', value: stats.total_users, sub: `활성 ${stats.active_users || 0}`, icon: Users, tone: 'teal' },
    { label: '전체 파티', value: stats.total_parties, sub: `모집 ${stats.recruiting_parties || 0}`, icon: Car, tone: 'olive' },
    { label: '매칭 완료', value: stats.matched_parties, sub: `완료 ${stats.completed_parties || 0}`, icon: CheckCircle2, tone: 'blue' },
    { label: '메시지', value: stats.total_messages, sub: '최근 채팅 점검', icon: MessageSquare, tone: 'amber' },
  ];
  const supportMetrics = [
    { label: '전체 문의', value: supportSummary.total, sub: `접수 ${supportSummary.open || 0}`, icon: Inbox, tone: 'teal' },
    { label: '문의 진행', value: supportSummary.in_progress, sub: '답변 진행', icon: MessageSquare, tone: 'amber' },
    { label: '완료 문의', value: supportSummary.resolved, sub: '처리 완료', icon: CheckCircle2, tone: 'blue' },
  ];

  const statusBars = ['recruiting', 'matched', 'canceled', 'expired', 'completed'].map((status) => {
    const count = parties.filter((party) => party.status === status).length;
    return {
      status,
      count,
      width: `${Math.max((count / partyTotal) * 100, count ? 10 : 0)}%`,
    };
  });

  return (
    <section className="view-stack">
      <div className="metric-grid metric-grid-primary">
        {primaryMetrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <article className={`metric-card ${metric.tone}`} key={metric.label}>
              <div>
                <span>{metric.label}</span>
                <strong>{Number(metric.value || 0).toLocaleString('ko-KR')}</strong>
                <small>{metric.sub}</small>
              </div>
              <Icon size={26} aria-hidden="true" />
            </article>
          );
        })}
      </div>
      <div className="metric-grid metric-grid-support">
        {supportMetrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <article className={`metric-card ${metric.tone}`} key={metric.label}>
              <div>
                <span>{metric.label}</span>
                <strong>{Number(metric.value || 0).toLocaleString('ko-KR')}</strong>
                <small>{metric.sub}</small>
              </div>
              <Icon size={26} aria-hidden="true" />
            </article>
          );
        })}
      </div>

      <div className="content-grid">
        <section className="panel">
          <PanelHeader
            icon={Server}
            title="시스템 상태"
            action={
              <button type="button" className="icon-text-button" onClick={onRefresh}>
                <RefreshCw size={16} aria-hidden="true" />
                갱신
              </button>
            }
          />
          <div className="system-list">
            <SystemRow icon={Activity} label="API" value={formatSystemStatus(system.api_status, mode === 'loading')} ok={system.api_status === 'ok'} />
            <SystemRow icon={Database} label="DB" value={formatSystemStatus(system.db_status, mode === 'loading')} ok={system.db_status === 'ok'} />
            <SystemRow icon={ShieldCheck} label="Fare key" value={system.mobility_provider_configured ? 'configured' : 'missing'} ok={system.mobility_provider_configured} />
            <SystemRow icon={Power} label="Fallback" value={system.fare_fallback_enabled ? 'enabled' : 'disabled'} ok={!system.fare_fallback_enabled} />
            <SystemRow icon={Clock} label="Server time" value={formatLongDate(system.server_time)} ok />
          </div>
        </section>

        <section className="panel">
          <PanelHeader icon={BarChart3} title="상태별 파티" />
          <div className="status-bars">
            {statusBars.map((item) => (
              <div className="status-row" key={item.status}>
                <span>{statusLabels[item.status]}</span>
                <div className="bar-track">
                  <div className={`bar-fill ${statusTone[item.status]}`} style={{ width: item.width }} />
                </div>
                <strong>{item.count}</strong>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="panel">
        <PanelHeader icon={ListChecks} title="최근 파티" />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>이동</th>
                <th>출발</th>
                <th>인원</th>
                <th>요금</th>
                <th>상태</th>
                <th>관리</th>
              </tr>
            </thead>
            <tbody>
              {recentParties.map((party) => (
                <tr key={party.id}>
                  <td>#{party.id}</td>
                  <td>{party.start_place} → {party.end_place}</td>
                  <td>{formatDate(party.departure_time)}</td>
                  <td>{party.current_members}/{party.max_members}</td>
                  <td>{formatWon(party.per_person_fare)}</td>
                  <td><StatusBadge status={party.status} /></td>
                  <td>
                    <div className="row-actions">
                      <button type="button" className="icon-button" onClick={() => onViewParty(party)} aria-label="파티 상세 보기" title="상세 보기">
                      <Eye size={16} aria-hidden="true" />
                      </button>
                      <button type="button" className="icon-button" onClick={() => onChangePartyStatus(party)} aria-label="파티 상태 변경" title="상태 변경">
                        <ListChecks size={16} aria-hidden="true" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}

function UsersView({ users, filters, setFilters, currentUser, activeAdminCount, onCreate, onDetail, onRoleChange, onStatusChange }) {
  return (
    <section className="panel">
      <PanelHeader
        icon={Users}
        title="사용자 관리"
        action={
          <div className="toolbar">
            <SearchBox value={filters.userKeyword} onChange={(userKeyword) => setFilters((previous) => ({ ...previous, userKeyword }))} placeholder="이름, 이메일, 권한 검색" />
            <select value={filters.userRole} onChange={(event) => setFilters((previous) => ({ ...previous, userRole: event.target.value }))} aria-label="사용자 role 필터">
              <option value="all">전체 role</option>
              <option value="user">user</option>
              <option value="admin">admin</option>
            </select>
            <select value={filters.userActive} onChange={(event) => setFilters((previous) => ({ ...previous, userActive: event.target.value }))} aria-label="활성 상태 필터">
              <option value="all">전체 active</option>
              <option value="true">active=true</option>
              <option value="false">active=false</option>
            </select>
            <label className="check-row compact">
              <input type="checkbox" checked={filters.includeDeleted} onChange={(event) => setFilters((previous) => ({ ...previous, includeDeleted: event.target.checked }))} />
              <span>deleted 포함</span>
            </label>
            {currentUser.master_admin && (
              <button type="button" className="primary-action" onClick={onCreate}>
                <UserCog size={17} aria-hidden="true" />
                사용자 추가
              </button>
            )}
          </div>
        }
      />
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>사용자</th>
              <th>성별</th>
              <th>권한</th>
              <th>상태</th>
              <th>가입일</th>
              <th>관리</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => {
              const roleDisabled = !currentUser.master_admin || user.master_admin || (user.role === 'admin' && user.is_active && activeAdminCount <= 1);
              const statusDisabled = user.master_admin || (user.role === 'admin' && user.is_active && activeAdminCount <= 1);

              return (
                <tr key={user.id}>
                  <td>#{user.id}</td>
                  <td>
                    <div className="stacked-cell">
                      <strong>{user.name}</strong>
                      <span>{user.email}</span>
                    </div>
                  </td>
                  <td>{genderLabels[user.gender] || user.gender || '-'}</td>
                  <td>
                    <div className="badge-row">
                      <Badge tone={user.role === 'admin' ? 'teal' : 'gray'}>{roleLabels[user.role] || user.role}</Badge>
                      {user.master_admin && <Badge tone="amber"><Crown size={13} aria-hidden="true" />마스터</Badge>}
                    </div>
                  </td>
                  <td>
                    <Badge tone={user.is_active ? 'olive' : 'red'}>{user.is_active ? '활성' : '비활성'}</Badge>
                  </td>
                  <td>{formatDate(user.created_at)}</td>
                  <td>
                    <div className="row-actions">
                      <button type="button" className="icon-button" onClick={() => onDetail(user)} aria-label="사용자 상세 보기" title="상세 보기">
                        <Eye size={16} aria-hidden="true" />
                      </button>
                      {currentUser.master_admin && (
                        <button type="button" className="icon-button" onClick={() => onRoleChange(user)} disabled={roleDisabled} aria-label="권한 변경" title="role 변경">
                          <UserCog size={16} aria-hidden="true" />
                        </button>
                      )}
                      <button type="button" className="icon-button" onClick={() => onStatusChange(user)} disabled={statusDisabled} aria-label="활성 상태 변경" title="active 변경">
                        <Power size={16} aria-hidden="true" />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
            {!users.length && <EmptyRow colSpan={7} label="사용자 데이터가 없습니다." />}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function PartiesView({ parties, filters, setFilters, currentUser, onCreate, onDetail, onStatusChange }) {
  return (
    <section className="panel">
      <PanelHeader
        icon={Car}
        title="파티 관리"
        action={
          <div className="toolbar">
            <select
              value={filters.partyStatus}
              onChange={(event) => setFilters((previous) => ({ ...previous, partyStatus: event.target.value }))}
              aria-label="파티 상태 필터"
            >
              <option value="all">전체 상태</option>
              <option value="recruiting">모집 중</option>
              <option value="matched">매칭 완료</option>
              <option value="canceled">취소</option>
              <option value="expired">만료</option>
              <option value="completed">이용 완료</option>
            </select>
            <SearchBox
              value={filters.partyKeyword}
              onChange={(partyKeyword) => setFilters((previous) => ({ ...previous, partyKeyword }))}
              placeholder="출발지, 도착지, 생성자 검색"
            />
            <input
              className="compact-input"
              type="number"
              value={filters.creatorUserId}
              onChange={(event) => setFilters((previous) => ({ ...previous, creatorUserId: event.target.value }))}
              placeholder="creator ID"
              aria-label="생성자 ID 필터"
            />
            <input
              className="compact-input"
              type="number"
              value={filters.memberUserId}
              onChange={(event) => setFilters((previous) => ({ ...previous, memberUserId: event.target.value }))}
              placeholder="member ID"
              aria-label="참여자 ID 필터"
            />
            <label className="check-row compact">
              <input type="checkbox" checked={filters.includeDeleted} onChange={(event) => setFilters((previous) => ({ ...previous, includeDeleted: event.target.checked }))} />
              <span>deleted 포함</span>
            </label>
            {currentUser.master_admin && (
              <button type="button" className="primary-action" onClick={onCreate}>
                <Car size={17} aria-hidden="true" />
                파티 생성
              </button>
            )}
          </div>
        }
      />
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>경로</th>
              <th>출발 시간</th>
              <th>만남 장소</th>
              <th>인원</th>
              <th>1인 요금</th>
              <th>상태</th>
              <th>관리</th>
            </tr>
          </thead>
          <tbody>
            {parties.map((party) => (
              <tr key={party.id}>
                <td>#{party.id}</td>
                <td>
                  <div className="stacked-cell">
                    <strong>{party.start_place} → {party.end_place}</strong>
                    <span>{party.creator_name || '생성자 미표시'}</span>
                  </div>
                </td>
                <td>{formatLongDate(party.departure_time)}</td>
                <td>{party.meeting_point || '-'}</td>
                <td>{party.current_members}/{party.max_members}</td>
                <td>{formatWon(party.per_person_fare)}</td>
                <td><StatusBadge status={party.status} /></td>
                <td>
                  <div className="row-actions">
                    <button type="button" className="icon-button" onClick={() => onDetail(party)} aria-label="파티 상세 보기" title="상세 보기">
                      <Eye size={16} aria-hidden="true" />
                    </button>
                    <button type="button" className="icon-button" onClick={() => onStatusChange(party)} aria-label="파티 상태 변경" title="status 변경">
                      <ListChecks size={16} aria-hidden="true" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {!parties.length && <EmptyRow colSpan={8} label="파티 데이터가 없습니다." />}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function MessagesView({ messages, currentUser, onHideMessage }) {
  return (
    <section className="panel">
      <PanelHeader icon={MessageSquare} title="최근 메시지" />
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>파티</th>
              <th>작성자</th>
              <th>내용</th>
              <th>작성 시간</th>
              {currentUser.master_admin && <th>관리</th>}
            </tr>
          </thead>
          <tbody>
            {messages.map((message) => (
              <tr key={message.id}>
                <td>#{message.id}</td>
                <td>#{message.party_id}</td>
                <td>{message.author_name || message.user_name || '-'}</td>
                <td>{message.content}</td>
                <td>{formatLongDate(message.created_at)}</td>
                {currentUser.master_admin && (
                  <td>
                    <button type="button" className="icon-button" onClick={() => onHideMessage(message)} aria-label="메시지 숨김">
                      <X size={15} aria-hidden="true" />
                    </button>
                  </td>
                )}
              </tr>
            ))}
            {!messages.length && <EmptyRow colSpan={currentUser.master_admin ? 6 : 5} label="최근 메시지가 없습니다." />}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function SupportInboxView({
  draft,
  onDraftChange,
  onRefresh,
  onReply,
  onSelectThread,
  onStatusChange,
  onViewParty,
  onViewUser,
  selectedThread,
  threads,
}) {
  return (
    <section className="panel support-admin-panel">
      <div className="support-admin-layout">
        <aside className="support-admin-list">
          {threads.map((thread) => (
            <button
              className={selectedThread?.id === thread.id ? 'support-admin-item active' : 'support-admin-item'}
              key={thread.id}
              type="button"
              onClick={() => onSelectThread(thread)}
            >
              <span>{thread.code || `Q${String(thread.id).padStart(5, '0')}`}</span>
              <strong>{thread.title}</strong>
              <small>{formatSupportKind(thread.kind)} · {thread.user?.name || '사용자'} · {formatSupportStatus(thread.status)}</small>
            </button>
          ))}
          {!threads.length && <div className="drawer-state compact">접수된 문의가 없습니다.</div>}
        </aside>

        <div className="support-admin-chat">
          {!selectedThread ? (
            <div className="support-admin-empty">
              <MessageSquare size={30} aria-hidden="true" />
              <p>신고/문의를 선택해주세요.</p>
            </div>
          ) : (
            <>
              <div className="support-admin-head">
                <div>
                  <p className="eyebrow">{selectedThread.code || `Q${String(selectedThread.id).padStart(5, '0')}`}</p>
                  <h2>{selectedThread.title}</h2>
                </div>
                <div className="support-admin-tools">
                  <select
                    value={selectedThread.status || 'open'}
                    onChange={(event) => onStatusChange(event.target.value)}
                    aria-label="문의 상태"
                  >
                    <option value="open">접수</option>
                    <option value="in_progress">진행 중</option>
                    <option value="resolved">완료</option>
                  </select>
                  <button type="button" className="icon-button" onClick={onRefresh} aria-label="새로고침">
                    <RefreshCw size={16} aria-hidden="true" />
                  </button>
                </div>
              </div>

              <article className="support-admin-summary">
                <SupportInfoCard
                  label="문의자"
                  title={selectedThread.user?.name || '사용자'}
                  text={selectedThread.user?.email || '-'}
                  actionLabel="USER DETAIL"
                  disabled={!selectedThread.user}
                  onClick={() => selectedThread.user && onViewUser(selectedThread.user)}
                />
                <SupportInfoCard
                  label="파티"
                  title={selectedThread.party ? `#${selectedThread.party.id}` : '미선택'}
                  text={selectedThread.party ? `${selectedThread.party.start_place} → ${selectedThread.party.end_place}` : '선택된 파티가 없습니다.'}
                  actionLabel="Party detail"
                  disabled={!selectedThread.party}
                  onClick={() => selectedThread.party && onViewParty(selectedThread.party)}
                />
              </article>

              <div className="support-admin-messages" aria-live="polite">
                <article className="support-admin-message support-intake-card">
                  <span>{formatSupportKind(selectedThread.kind)} 접수 내용</span>
                  <p>{selectedThread.content}</p>
                </article>
                {getSupportTimelineItems(selectedThread).map((item) => (
                  item.type === 'event' ? (
                    <div className="support-admin-system-note" key={item.key}>{item.content}</div>
                  ) : (
                    <article
                      className={item.sender_role === 'admin' ? 'support-admin-message mine' : 'support-admin-message'}
                      key={item.key}
                    >
                      <span>{item.sender_name || (item.sender_role === 'admin' ? '운영팀' : '사용자')}</span>
                      <p>{item.content}</p>
                      <time>{formatLongDate(item.created_at)}</time>
                    </article>
                  )
                ))}
              </div>

              <form className="support-admin-input" onSubmit={onReply}>
                <input
                  placeholder="답변을 입력하세요"
                  value={draft}
                  onChange={(event) => onDraftChange(event.target.value)}
                />
                <button type="submit" className="primary-action" disabled={!draft.trim()}>
                  <Send size={16} aria-hidden="true" />
                  전송
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </section>
  );
}

function SupportInfoCard({ actionLabel, disabled, label, onClick, text, title }) {
  return (
    <div className="support-info-card">
      <span>{label}</span>
      <strong>{title}</strong>
      <p>{text}</p>
      <button type="button" className="icon-text-button" disabled={disabled} onClick={onClick}>
        <Eye size={15} aria-hidden="true" />
        {actionLabel}
      </button>
    </div>
  );
}

function getVisibleSupportMessages(thread) {
  const messages = thread?.messages || [];
  return messages.filter((message, index) => {
    if (index !== 0) return true;
    return !(message.sender_role === 'user' && message.content === thread.content);
  });
}

function getSupportTimelineItems(thread) {
  const events = (thread?.events?.length ? thread.events : createFallbackSupportEvents(thread)).map((event) => ({
    ...event,
    type: 'event',
    key: `event-${event.id || event.event_type || event.created_at}`,
  }));
  const messages = getVisibleSupportMessages(thread).map((message) => ({
    ...message,
    type: 'message',
    key: `message-${message.id}`,
  }));

  return [...events, ...messages].sort((left, right) => new Date(left.created_at || 0) - new Date(right.created_at || 0));
}

function createFallbackSupportEvents(thread) {
  return [
    {
      id: 'created',
      event_type: 'created',
      content: '문의가 시작되었습니다. 개발자의 답변이 오기 전까지 다소 시간이 소요될 수 있습니다.',
      created_at: thread?.created_at,
    },
    {
      id: 'status',
      event_type: 'status',
      content: `현재 상태가 ${formatSupportStatus(thread?.status)}로 변경되었습니다.`,
      created_at: thread?.updated_at || thread?.created_at,
    },
  ];
}

function ActionsView({ actions }) {
  return (
    <section className="panel">
      <PanelHeader icon={History} title="관리자 조작 기록" />
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>관리자</th>
              <th>유형</th>
              <th>대상</th>
              <th>변경</th>
              <th>메모</th>
              <th>시간</th>
            </tr>
          </thead>
          <tbody>
            {actions.map((action) => (
              <tr key={action.id}>
                <td>#{action.id}</td>
                <td>{action.actor_admin_name || `#${action.actor_admin_id}`}</td>
                <td>{actionTypeLabels[action.action_type] || action.action_type}</td>
                <td>{targetTypeLabels[action.target_type] || action.target_type} #{action.target_id}</td>
                <td>{action.before_value} → {action.after_value}</td>
                <td>{action.note || '-'}</td>
                <td>{formatLongDate(action.created_at)}</td>
              </tr>
            ))}
            {!actions.length && <EmptyRow colSpan={7} label="조작 기록이 없습니다." />}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function DetailDrawer({
  drawer,
  currentUser,
  activeAdminCount,
  onClose,
  onChangeUserRole,
  onChangeUserStatus,
  onEditUser,
  onResetPassword,
  onDeleteUser,
  onChangePartyStatus,
  onEditParty,
  onDeleteParty,
  onAddMember,
  onRemoveMember,
  onRecalculateFare,
  onOverrideFare,
  onCreateNotice,
}) {
  const isUser = drawer.kind === 'user';
  const user = isUser ? drawer.data?.user || drawer.summary : null;
  const party = !isUser ? { ...drawer.summary, ...(drawer.data?.party || {}) } : null;
  const members = drawer.data?.members || [];
  const userStatusDisabled = user?.master_admin || (user?.role === 'admin' && user?.is_active && activeAdminCount <= 1);
  const userRoleDisabled = !currentUser.master_admin || userStatusDisabled;

  return (
    <div className="drawer-backdrop" role="presentation">
      <aside className="detail-drawer" aria-label={drawer.title}>
        <header className="drawer-header">
          <div>
            <p className="eyebrow">{isUser ? 'User detail' : 'Party detail'}</p>
            <h2>{drawer.title}</h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose} aria-label="닫기">
            <X size={18} aria-hidden="true" />
          </button>
        </header>

        {drawer.loading && <div className="drawer-state">loading...</div>}
        {drawer.error && <div className="drawer-state error">{drawer.error}</div>}

        {!drawer.loading && !drawer.error && isUser && user && (
          <div className="drawer-body">
            <section className="detail-section">
              <h3>Profile</h3>
              <div className="detail-grid">
                <DetailItem label="ID" value={`#${user.id}`} />
                <DetailItem label="Email" value={user.email} />
                <DetailItem label="Name" value={user.name} />
                <DetailItem label="Gender" value={genderLabels[user.gender] || user.gender || '-'} />
                <DetailItem label="Role" value={roleLabels[user.role] || user.role} />
                <DetailItem label="Active" value={user.is_active ? 'true' : 'false'} />
                <DetailItem label="Master admin" value={user.master_admin ? 'true' : 'false'} />
                <DetailItem label="Created" value={formatLongDate(user.created_at)} />
              </div>
            </section>

            <section className="detail-section">
              <h3>Usage</h3>
              <div className="mini-metric-grid">
                <MiniMetric label="Created parties" value={drawer.data?.created_parties_count || 0} />
                <MiniMetric label="Joined parties" value={drawer.data?.joined_parties_count || 0} />
                <MiniMetric label="Messages" value={drawer.data?.message_count || 0} />
              </div>
            </section>

            <section className="detail-section">
              <h3>Party history</h3>
              <div className="member-list">
                {(drawer.data?.partyHistory?.items || []).map((item) => (
                  <div className="member-row" key={`${item.relation}-${item.party_id}`}>
                    <div>
                      <strong>#{item.party_id} {item.start_place} → {item.end_place}</strong>
                      <span>{item.relation} · {statusLabels[item.status] || item.status} · {formatDate(item.departure_time)} · {item.current_members}/{item.max_members}</span>
                    </div>
                  </div>
                ))}
                {drawer.data?.partyHistoryError && <div className="drawer-state compact">{drawer.data.partyHistoryError}</div>}
                {!drawer.data?.partyHistoryError && !(drawer.data?.partyHistory?.items || []).length && (
                  <div className="drawer-state compact">파티 이력이 없습니다.</div>
                )}
              </div>
            </section>

            <footer className="drawer-actions">
              <div className="drawer-action-grid">
                {currentUser.master_admin && (
                  <>
                    <button type="button" className="primary-action" onClick={() => onEditUser(user)} disabled={user.master_admin}>
                      <PencilLine size={17} aria-hidden="true" />
                      Edit user
                    </button>
                    <button type="button" className="ghost-button" onClick={() => onResetPassword(user)} disabled={user.master_admin}>
                      <KeyRound size={17} aria-hidden="true" />
                      Reset password
                    </button>
                    <button type="button" className="ghost-button" onClick={() => onChangeUserRole(user)} disabled={userRoleDisabled}>
                      <UserCog size={17} aria-hidden="true" />
                      Change role
                    </button>
                  </>
                )}
                <button type="button" className="ghost-button" onClick={() => onChangeUserStatus(user)} disabled={userStatusDisabled}>
                  <Power size={17} aria-hidden="true" />
                  {user.is_active ? 'Deactivate' : 'Activate'}
                </button>
              </div>
              {currentUser.master_admin && (
                <button type="button" className="ghost-button danger drawer-danger-action" onClick={() => onDeleteUser(user)} disabled={userStatusDisabled}>
                  <Trash2 size={17} aria-hidden="true" />
                  Delete user
                </button>
              )}
            </footer>
          </div>
        )}

        {!drawer.loading && !drawer.error && !isUser && party && (
          <div className="drawer-body">
            <section className="detail-section">
              <h3>Route</h3>
              <div className="detail-grid">
                <DetailItem label="ID" value={`#${party.id}`} />
                <DetailItem label="Creator" value={party.creator_name || `#${party.creator_id}`} />
                <DetailItem label="Status" value={statusLabels[party.status] || party.status} />
                <DetailItem label="Departure" value={formatLongDate(party.departure_time)} />
                <DetailItem label="Start" value={party.start_place} />
                <DetailItem label="End" value={party.end_place} />
                <DetailItem label="Meeting point" value={party.meeting_point || '-'} />
                <DetailItem label="Meeting note" value={party.meeting_note || '-'} />
              </div>
            </section>

            <section className="detail-section">
              <h3>Fare and capacity</h3>
              <div className="detail-grid">
                <DetailItem label="Members" value={`${party.current_members}/${party.max_members}`} />
                <DetailItem label="Estimated fare" value={formatWon(party.estimated_fare)} />
                <DetailItem label="Per person" value={formatWon(party.per_person_fare)} />
                <DetailItem label="Toll" value={formatWon(party.toll_fare)} />
                <DetailItem label="Distance" value={party.distance_meters ? `${Number(party.distance_meters).toLocaleString('ko-KR')}m` : '-'} />
                <DetailItem label="Duration" value={party.duration_seconds ? `${Math.round(party.duration_seconds / 60)}분` : '-'} />
                <DetailItem label="Fare mode" value={party.fare_source || '-'} />
                <DetailItem label="Messages" value={drawer.data?.messages_count ?? 0} />
              </div>
            </section>

            <section className="detail-section">
              <h3>Members</h3>
              <div className="member-list">
                {members.map((member) => (
                  <div className="member-row" key={member.id}>
                    <div>
                      <strong>{member.name}</strong>
                      <span>#{member.id} · {genderLabels[member.gender] || member.gender || '-'} · {formatDate(member.joined_at)}</span>
                    </div>
                    {currentUser.master_admin && (
                      <button type="button" className="icon-button" onClick={() => onRemoveMember(party, member)} aria-label="참여자 삭제">
                        <X size={15} aria-hidden="true" />
                      </button>
                    )}
                  </div>
                ))}
                {!members.length && <div className="drawer-state compact">참여자 데이터가 없습니다.</div>}
              </div>
            </section>

            <footer className="drawer-actions">
              <div className="drawer-action-grid">
                <button type="button" className="primary-action" onClick={() => onChangePartyStatus(party)}>
                  <ListChecks size={17} aria-hidden="true" />
                  Change status
                </button>
                {currentUser.master_admin && (
                  <>
                    <button type="button" className="ghost-button" onClick={() => onEditParty(party)}>
                      <PencilLine size={17} aria-hidden="true" />
                      Edit party
                    </button>
                    <button type="button" className="ghost-button" onClick={() => onAddMember(party)}>
                      <UserPlus size={17} aria-hidden="true" />
                      Add member
                    </button>
                    <button type="button" className="ghost-button" onClick={() => onRecalculateFare(party)}>
                      <RefreshCw size={17} aria-hidden="true" />
                      Recalculate fare
                    </button>
                    <button type="button" className="ghost-button" onClick={() => onOverrideFare(party)}>
                      <Calculator size={17} aria-hidden="true" />
                      Override fare
                    </button>
                    <button type="button" className="ghost-button" onClick={() => onCreateNotice(party)}>
                      <Bell size={17} aria-hidden="true" />
                      Notice
                    </button>
                  </>
                )}
              </div>
              {currentUser.master_admin && (
                <button type="button" className="ghost-button danger drawer-danger-action" onClick={() => onDeleteParty(party)}>
                  <Trash2 size={17} aria-hidden="true" />
                  Delete party
                </button>
              )}
            </footer>
          </div>
        )}
      </aside>
    </div>
  );
}

function DetailItem({ label, value }) {
  return (
    <div className="detail-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function MiniMetric({ label, value }) {
  return (
    <div className="mini-metric">
      <span>{label}</span>
      <strong>{Number(value || 0).toLocaleString('ko-KR')}</strong>
    </div>
  );
}

function createInitialMaintenanceForm(fields) {
  return fields.reduce((accumulator, field) => {
    if (field.type === 'checkbox') {
      accumulator[field.name] = Boolean(field.defaultValue);
      return accumulator;
    }

    accumulator[field.name] = field.defaultValue ?? '';
    return accumulator;
  }, {});
}

function normalizeMaintenancePayload(fields, form) {
  return fields.reduce((payload, field) => {
    const rawValue = form[field.name];

    if (field.type === 'checkbox') {
      payload[field.name] = Boolean(rawValue);
      return payload;
    }

    if (rawValue === '' || rawValue === undefined || rawValue === null) {
      if (field.required) payload[field.name] = rawValue;
      return payload;
    }

    if (field.type === 'number') {
      payload[field.name] = Number(rawValue);
      return payload;
    }

    if (field.type === 'csvNumbers') {
      payload[field.name] = String(rawValue)
        .split(',')
        .map((item) => Number(item.trim()))
        .filter((item) => Number.isFinite(item));
      return payload;
    }

    if (field.type === 'datetime-local') {
      payload[field.name] = toKstIso(rawValue);
      return payload;
    }

    payload[field.name] = typeof rawValue === 'string' ? rawValue.trim() : rawValue;
    return payload;
  }, {});
}

function MaintenanceDialog({ dialog, pending, onClose, onConfirm }) {
  const [form, setForm] = useState(() => createInitialMaintenanceForm(dialog.fields));

  useEffect(() => {
    setForm(createInitialMaintenanceForm(dialog.fields));
  }, [dialog]);

  function updateField(name, value) {
    setForm((previous) => ({ ...previous, [name]: value }));
  }

  function submit(event) {
    event.preventDefault();
    onConfirm(normalizeMaintenancePayload(dialog.fields, form));
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section className="modal wide-modal" role="dialog" aria-modal="true" aria-labelledby="maintenance-dialog-title">
        <header className="modal-header">
          <div>
            <p className="eyebrow">Admin Operation</p>
            <h2 id="maintenance-dialog-title">{dialog.title}</h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose} aria-label="닫기">
            <X size={18} aria-hidden="true" />
          </button>
        </header>

        <form onSubmit={submit}>
          <div className="modal-body form-grid">
            {dialog.fields.map((field) => (
              <FieldControl field={field} value={form[field.name]} onChange={updateField} key={field.name} />
            ))}
          </div>

          <footer className="modal-actions">
            <button type="button" className="ghost-button" onClick={onClose}>취소</button>
            <button type="submit" className="primary-action" disabled={pending}>
              <CheckCircle2 size={17} aria-hidden="true" />
              적용
            </button>
          </footer>
        </form>
      </section>
    </div>
  );
}

function FieldControl({ field, value, onChange }) {
  if (field.type === 'checkbox') {
    return (
      <label className="check-row field-check">
        <input type="checkbox" checked={Boolean(value)} onChange={(event) => onChange(field.name, event.target.checked)} />
        <span>{field.label}</span>
      </label>
    );
  }

  if (field.type === 'select') {
    return (
      <label>
        <span>{field.label}{field.required ? ' *' : ''}</span>
        <select value={value} onChange={(event) => onChange(field.name, event.target.value)} required={field.required}>
          {(field.options || []).map((option) => (
            <option value={option.value} key={option.value}>{option.label}</option>
          ))}
        </select>
      </label>
    );
  }

  if (field.type === 'textarea') {
    return (
      <label className="full-field">
        <span>{field.label}{field.required ? ' *' : ''}</span>
        <textarea value={value} onChange={(event) => onChange(field.name, event.target.value)} rows={4} required={field.required} />
      </label>
    );
  }

  return (
    <label>
      <span>{field.label}{field.required ? ' *' : ''}</span>
      <input
        type={field.type === 'csvNumbers' ? 'text' : field.type || 'text'}
        value={value}
        onChange={(event) => onChange(field.name, event.target.value)}
        required={field.required}
      />
    </label>
  );
}

function ActionDialog({ dialog, pending, onClose, onConfirm }) {
  const [value, setValue] = useState(dialog.value);
  const [note, setNote] = useState(dialog.note || '');
  const [force, setForce] = useState(false);

  useEffect(() => {
    setValue(dialog.value);
    setNote(dialog.note || '');
    setForce(false);
  }, [dialog]);

  return (
    <div className="modal-backdrop" role="presentation">
      <section className="modal" role="dialog" aria-modal="true" aria-labelledby="action-dialog-title">
        <header className="modal-header">
          <div>
            <p className="eyebrow">관리 작업</p>
            <h2 id="action-dialog-title">{dialog.title}</h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose} aria-label="닫기">
            <X size={18} aria-hidden="true" />
          </button>
        </header>

        <div className="modal-body">
          <label>
            <span>대상</span>
            <input type="text" value={dialog.targetLabel} readOnly />
          </label>
          <label>
            <span>변경값</span>
            <select value={value} onChange={(event) => setValue(event.target.value)}>
              {dialog.options.map((option) => (
                <option value={option.value} key={option.value}>{option.label}</option>
              ))}
            </select>
          </label>
          <label>
            <span>관리 메모</span>
            <textarea value={note} onChange={(event) => setNote(event.target.value)} rows={4} />
          </label>
          {dialog.allowForce && (
            <label className="check-row">
              <input type="checkbox" checked={force} onChange={(event) => setForce(event.target.checked)} />
              <span>force=true로 조건 우회 요청</span>
            </label>
          )}
        </div>

        <footer className="modal-actions">
          <button type="button" className="ghost-button" onClick={onClose}>취소</button>
          <button type="button" className="primary-action" onClick={() => onConfirm(value, note, force)} disabled={pending}>
            <CheckCircle2 size={17} aria-hidden="true" />
            변경 적용
          </button>
        </footer>
      </section>
    </div>
  );
}

function PanelHeader({ icon: Icon, title, action }) {
  return (
    <div className="panel-header">
      <div className="panel-title">
        <Icon size={19} aria-hidden="true" />
        <h2>{title}</h2>
      </div>
      {action}
    </div>
  );
}

function SearchBox({ value, onChange, placeholder }) {
  return (
    <label className="search-box">
      <Search size={16} aria-hidden="true" />
      <input type="search" value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} />
    </label>
  );
}

function SystemRow({ icon: Icon, label, value, ok }) {
  return (
    <div className="system-row">
      <Icon size={18} aria-hidden="true" />
      <span>{label}</span>
      <strong className={ok ? 'ok' : 'warn'}>{value}</strong>
    </div>
  );
}

function StatusBadge({ status }) {
  return <Badge tone={statusTone[status] || 'gray'}>{statusLabels[status] || status || '-'}</Badge>;
}

function Badge({ tone = 'gray', children }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

function EmptyRow({ colSpan, label }) {
  return (
    <tr>
      <td colSpan={colSpan} className="empty-cell">{label}</td>
    </tr>
  );
}

export default App;
