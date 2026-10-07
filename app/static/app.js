// Alumni Tracking System Frontend Logic
let allUsers = [];
let currentView = 'table'; // 'table' or 'grid'

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

function initApp() {
  checkApiHealth();
  loadUsers();
  setupEventListeners();

  // Periodic health check every 15 seconds
  setInterval(checkApiHealth, 15000);
}

// ----------------------------------------
// Event Listeners & UI Toggles
// ----------------------------------------
function setupEventListeners() {
  // Search input
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');

  searchInput.addEventListener('input', (e) => {
    const val = e.target.value.trim();
    clearSearchBtn.style.display = val ? 'block' : 'none';
    filterAndRender();
  });

  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    clearSearchBtn.style.display = 'none';
    filterAndRender();
  });

  // Department filter
  document.getElementById('deptFilter').addEventListener('change', () => {
    filterAndRender();
  });

  // View switches
  document.getElementById('viewTableBtn').addEventListener('click', () => {
    setView('table');
  });
  document.getElementById('viewGridBtn').addEventListener('click', () => {
    setView('grid');
  });

  // Refresh button
  document.getElementById('refreshBtn').addEventListener('click', () => {
    loadUsers();
  });

  // Open Add Modal
  document.getElementById('openAddModalBtn').addEventListener('click', () => {
    openAddModal();
  });

  // Toggle API Console
  document.getElementById('toggleConsoleBtn').addEventListener('click', () => {
    const body = document.getElementById('consoleBody');
    const icon = document.querySelector('.console-toggle-icon');
    if (body.style.display === 'none') {
      body.style.display = 'block';
      icon.textContent = '▾';
    } else {
      body.style.display = 'none';
      icon.textContent = '▸';
    }
  });

  // Close modals when clicking backdrop
  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('active');
      }
    });
  });
}

function setView(view) {
  currentView = view;
  const tableBtn = document.getElementById('viewTableBtn');
  const gridBtn = document.getElementById('viewGridBtn');
  const tableView = document.getElementById('tableView');
  const gridView = document.getElementById('gridView');

  if (view === 'table') {
    tableBtn.classList.add('active');
    gridBtn.classList.remove('active');
    tableView.style.display = 'block';
    gridView.style.display = 'none';
  } else {
    tableBtn.classList.remove('active');
    gridBtn.classList.add('active');
    tableView.style.display = 'none';
    gridView.style.display = 'grid';
  }
}

// ----------------------------------------
// API Operations
// ----------------------------------------

// 1. Health Check (GET /api/health)
async function checkApiHealth() {
  const indicator = document.getElementById('healthIndicator');
  const text = document.getElementById('healthStatusText');
  try {
    const startTime = performance.now();
    const res = await fetch('/api/health');
    const elapsed = Math.round(performance.now() - startTime);

    if (res.ok) {
      const data = await res.json();
      indicator.classList.remove('error');
      text.textContent = `API Aktif (${elapsed}ms)`;
      document.getElementById('statStatus').textContent = 'REST Aktif';
    } else {
      throw new Error(`HTTP ${res.status}`);
    }
  } catch (err) {
    indicator.classList.add('error');
    text.textContent = 'API Bağlantısı Kesildi';
    document.getElementById('statStatus').textContent = 'Çevrimdışı';
    logApiEvent('GET', '/api/health', 'ERR', 'Sunucuya ulaşılamadı');
  }
}

// 2. Fetch All Users (GET /api/users)
async function loadUsers() {
  const loading = document.getElementById('loadingSpinner');
  loading.style.display = 'block';

  try {
    const res = await fetch('/api/users');
    const data = await res.json();

    if (res.ok) {
      allUsers = data;
      logApiEvent('GET', '/api/users', `${res.status} OK`, `${data.length} mezun listelendi`);
      populateDepartmentFilter(allUsers);
      filterAndRender();
      updateStats(allUsers);
    } else {
      showToast('Kullanıcılar alınırken hata oluştu.', 'error');
      logApiEvent('GET', '/api/users', `${res.status}`, data.detail || 'Hata');
    }
  } catch (err) {
    showToast('Sunucuya bağlanılamadı!', 'error');
    logApiEvent('GET', '/api/users', 'ERR', err.message);
  } finally {
    loading.style.display = 'none';
  }
}

// 3. Create User (POST /api/users)
async function handleCreateUser(e) {
  e.preventDefault();
  const idInput = document.getElementById('addUserId').value.trim();
  const name = document.getElementById('addUserName').value.trim();
  const email = document.getElementById('addUserEmail').value.trim();
  const department = document.getElementById('addUserDepartment').value.trim();

  const payload = {
    name,
    email,
    department
  };

  if (idInput) {
    payload.id = parseInt(idInput, 10);
  }

  const saveBtn = document.getElementById('saveAddBtn');
  saveBtn.disabled = true;

  try {
    const res = await fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (res.status === 201) {
      showToast(`"${data.name}" başarıyla eklendi! (ID: ${data.id})`, 'success');
      logApiEvent('POST', '/api/users', '201 Created', `ID: ${data.id} - ${data.name}`);
      closeModal('addModal');
      document.getElementById('addUserForm').reset();
      loadUsers();
    } else {
      // Handles 400 "User ID already exists"
      showToast(data.detail || 'Kullanıcı eklenemedi.', 'error');
      logApiEvent('POST', '/api/users', `${res.status} Error`, data.detail || 'Eklenemedi');
    }
  } catch (err) {
    showToast('İstek gönderilirken hata oluştu.', 'error');
    logApiEvent('POST', '/api/users', 'ERR', err.message);
  } finally {
    saveBtn.disabled = false;
  }
}

// 4. Update User (PUT or PATCH /api/users/:user_id)
async function handleUpdateUser(e) {
  e.preventDefault();
  const userId = document.getElementById('editUserId').value;
  const method = document.querySelector('input[name="updateMethod"]:checked').value; // 'PUT' or 'PATCH'

  const name = document.getElementById('editUserName').value.trim();
  const email = document.getElementById('editUserEmail').value.trim();
  const department = document.getElementById('editUserDepartment').value.trim();

  let payload = {};

  if (method === 'PUT') {
    // PUT requires all fields
    payload = { name, email, department };
  } else {
    // PATCH allows partial fields
    if (name) payload.name = name;
    if (email) payload.email = email;
    if (department) payload.department = department;
  }

  const saveBtn = document.getElementById('saveEditBtn');
  saveBtn.disabled = true;

  try {
    const res = await fetch(`/api/users/${userId}`, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (res.ok) {
      showToast(`Mezun ID #${userId} güncellendi! (${method})`, 'success');
      logApiEvent(method, `/api/users/${userId}`, `${res.status} OK`, `${data.name}`);
      closeModal('editModal');
      loadUsers();
    } else {
      showToast(data.detail || 'Güncelleme başarısız.', 'error');
      logApiEvent(method, `/api/users/${userId}`, `${res.status}`, data.detail);
    }
  } catch (err) {
    showToast('Sunucu hatası!', 'error');
    logApiEvent(method, `/api/users/${userId}`, 'ERR', err.message);
  } finally {
    saveBtn.disabled = false;
  }
}

// 5. Delete User (DELETE /api/users/:user_id)
async function confirmDeleteUser() {
  const userId = document.getElementById('deleteUserId').value;
  const confirmBtn = document.getElementById('confirmDeleteBtn');
  confirmBtn.disabled = true;

  try {
    const res = await fetch(`/api/users/${userId}`, {
      method: 'DELETE'
    });

    if (res.status === 204) {
      showToast(`Mezun #${userId} silindi. (204 No Content)`, 'info');
      logApiEvent('DELETE', `/api/users/${userId}`, '204 No Content', `ID: ${userId} silindi`);
      closeModal('deleteModal');
      loadUsers();
    } else {
      const data = await res.json();
      showToast(data.detail || 'Silme işlemi başarısız.', 'error');
      logApiEvent('DELETE', `/api/users/${userId}`, `${res.status}`, data.detail);
    }
  } catch (err) {
    showToast('Silme işlemi sırasında hata oluştu.', 'error');
    logApiEvent('DELETE', `/api/users/${userId}`, 'ERR', err.message);
  } finally {
    confirmBtn.disabled = false;
  }
}

// 6. Inspect Single User (GET /api/users/:user_id)
async function inspectUser(userId) {
  try {
    const res = await fetch(`/api/users/${userId}`);
    const user = await res.json();

    if (res.ok) {
      logApiEvent('GET', `/api/users/${userId}`, `${res.status} OK`, `${user.name}`);

      const body = document.getElementById('detailModalBody');
      body.innerHTML = `
        <div style="display:flex; align-items:center; gap: 1rem; margin-bottom: 1.25rem;">
          <div class="user-avatar" style="width: 58px; height: 58px; font-size: 1.3rem;">
            ${getInitials(user.name)}
          </div>
          <div>
            <h3 style="font-size: 1.25rem; font-weight: 700;">${escapeHtml(user.name)}</h3>
            <span class="dept-badge">${escapeHtml(user.department)}</span>
          </div>
        </div>

        <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 1rem; font-family: monospace; font-size: 0.85rem; display: flex; flex-direction: column; gap: 0.5rem;">
          <div><strong style="color: #94a3b8;">Kayıt ID:</strong> <span style="color:#60a5fa;">${user.id}</span></div>
          <div><strong style="color: #94a3b8;">E-posta:</strong> <span style="color:#f8fafc;">${escapeHtml(user.email)}</span></div>
          <div><strong style="color: #94a3b8;">Bölüm:</strong> <span style="color:#a5b4fc;">${escapeHtml(user.department)}</span></div>
          <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.08); color:#64748b; font-size: 0.78rem;">
            Endpoint: GET /api/users/${user.id}
          </div>
        </div>
      `;
      openModal('detailModal');
    } else {
      showToast(user.detail || 'Kullanıcı bulunamadı.', 'error');
      logApiEvent('GET', `/api/users/${userId}`, `${res.status}`, user.detail);
    }
  } catch (err) {
    showToast('Kullanıcı detayı alınamadı.', 'error');
  }
}

// ----------------------------------------
// Filtering & Rendering
// ----------------------------------------
function filterAndRender() {
  const searchTerm = document.getElementById('searchInput').value.trim().toLowerCase();
  const selectedDept = document.getElementById('deptFilter').value;

  const filtered = allUsers.filter(u => {
    const matchesSearch = !searchTerm ||
      u.name.toLowerCase().includes(searchTerm) ||
      u.email.toLowerCase().includes(searchTerm) ||
      u.department.toLowerCase().includes(searchTerm) ||
      u.id.toString() === searchTerm;

    const matchesDept = !selectedDept || u.department.toLowerCase() === selectedDept.toLowerCase();

    return matchesSearch && matchesDept;
  });

  const emptyState = document.getElementById('emptyState');
  const tableView = document.getElementById('tableView');
  const gridView = document.getElementById('gridView');

  if (filtered.length === 0) {
    emptyState.style.display = 'block';
    tableView.style.display = 'none';
    gridView.style.display = 'none';
  } else {
    emptyState.style.display = 'none';
    if (currentView === 'table') {
      tableView.style.display = 'block';
      gridView.style.display = 'none';
    } else {
      tableView.style.display = 'none';
      gridView.style.display = 'grid';
    }

    renderTable(filtered);
    renderGrid(filtered);
  }
}

function renderTable(users) {
  const tbody = document.getElementById('alumniTableBody');
  tbody.innerHTML = '';

  users.forEach(user => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><span class="id-badge">#${user.id}</span></td>
      <td>
        <div class="user-cell">
          <div class="user-avatar">${getInitials(user.name)}</div>
          <span class="user-name-title">${escapeHtml(user.name)}</span>
        </div>
      </td>
      <td>
        <a href="mailto:${escapeHtml(user.email)}" class="email-link">${escapeHtml(user.email)}</a>
      </td>
      <td>
        <span class="dept-badge">${escapeHtml(user.department)}</span>
      </td>
      <td style="text-align: right;">
        <div class="actions-group">
          <button class="action-btn" onclick="inspectUser(${user.id})" title="Detay (GET /api/users/:id)">
            Detay
          </button>
          <button class="action-btn edit-btn" onclick="openEditModal(${user.id})" title="Düzenle (PUT/PATCH)">
            Düzenle
          </button>
          <button class="action-btn del-btn" onclick="openDeleteModal(${user.id}, '${escapeHtml(user.name)}')" title="Sil (DELETE)">
            Sil
          </button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderGrid(users) {
  const grid = document.getElementById('gridView');
  grid.innerHTML = '';

  users.forEach(user => {
    const card = document.createElement('div');
    card.className = 'alumni-card';
    card.innerHTML = `
      <div class="card-top">
        <div class="card-profile">
          <div class="card-avatar">${getInitials(user.name)}</div>
          <div class="card-info">
            <h3>${escapeHtml(user.name)}</h3>
            <span class="dept-badge">${escapeHtml(user.department)}</span>
          </div>
        </div>
        <span class="id-badge">#${user.id}</span>
      </div>

      <div class="card-details">
        <div class="detail-row">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
            <polyline points="22,6 12,13 2,6"></polyline>
          </svg>
          <a href="mailto:${escapeHtml(user.email)}" class="email-link">${escapeHtml(user.email)}</a>
        </div>
      </div>

      <div class="card-actions">
        <button class="btn btn-secondary btn-sm" onclick="inspectUser(${user.id})">Detay</button>
        <button class="btn btn-secondary btn-sm" onclick="openEditModal(${user.id})">Düzenle</button>
        <button class="btn btn-danger btn-sm" onclick="openDeleteModal(${user.id}, '${escapeHtml(user.name)}')">Sil</button>
      </div>
    `;
    grid.appendChild(card);
  });
}

function populateDepartmentFilter(users) {
  const deptSelect = document.getElementById('deptFilter');
  const currentVal = deptSelect.value;
  const departments = [...new Set(users.map(u => u.department))].sort();

  deptSelect.innerHTML = '<option value="">Tüm Bölümler</option>';
  departments.forEach(dept => {
    const opt = document.createElement('option');
    opt.value = dept;
    opt.textContent = dept;
    if (dept === currentVal) opt.selected = true;
    deptSelect.appendChild(opt);
  });
}

function updateStats(users) {
  document.getElementById('statTotalUsers').textContent = users.length;
  const distinctDepts = new Set(users.map(u => u.department.toLowerCase()));
  document.getElementById('statDepartments').textContent = distinctDepts.size;
}

// ----------------------------------------
// Modals Handling
// ----------------------------------------
function openModal(modalId) {
  document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove('active');
}

function openAddModal() {
  document.getElementById('addUserForm').reset();
  openModal('addModal');
  document.getElementById('addUserName').focus();
}

function openEditModal(userId) {
  const user = allUsers.find(u => u.id === userId);
  if (!user) return;

  document.getElementById('editUserId').value = user.id;
  document.getElementById('displayEditId').value = `#${user.id}`;
  document.getElementById('editUserName').value = user.name;
  document.getElementById('editUserEmail').value = user.email;
  document.getElementById('editUserDepartment').value = user.department;

  // Default to PUT
  document.querySelector('input[name="updateMethod"][value="PUT"]').checked = true;
  handleMethodToggle('PUT');

  openModal('editModal');
}

function handleMethodToggle(method) {
  const badge = document.getElementById('editMethodBadge');
  const title = document.getElementById('editModalTitle');
  const nameReq = document.getElementById('nameRequired');
  const emailReq = document.getElementById('emailRequired');
  const deptReq = document.getElementById('deptRequired');

  if (method === 'PUT') {
    badge.className = 'badge tag-put';
    badge.textContent = 'PUT /api/users/:id';
    title.textContent = 'Tam Güncelleme (PUT)';
    nameReq.style.display = 'inline';
    emailReq.style.display = 'inline';
    deptReq.style.display = 'inline';
  } else {
    badge.className = 'badge tag-patch';
    badge.textContent = 'PATCH /api/users/:id';
    title.textContent = 'Kısmi Güncelleme (PATCH)';
    nameReq.style.display = 'none';
    emailReq.style.display = 'none';
    deptReq.style.display = 'none';
  }
}

function openDeleteModal(userId, userName) {
  document.getElementById('deleteUserId').value = userId;
  document.getElementById('deleteUserName').textContent = userName;
  document.getElementById('deleteTargetId').textContent = userId;
  openModal('deleteModal');
}

// ----------------------------------------
// Live API Console & Toasts
// ----------------------------------------
function logApiEvent(method, path, statusText, msg = '') {
  const logContainer = document.getElementById('consoleLog');
  const entry = document.createElement('div');
  entry.className = 'log-entry';

  const timeStr = new Date().toTimeString().split(' ')[0];
  const methodClass = `method-${method.toLowerCase()}`;

  let statusClass = 'text-green';
  if (statusText.includes('ERR') || statusText.startsWith('4') || statusText.startsWith('5')) {
    statusClass = 'text-red';
  } else if (statusText.startsWith('3')) {
    statusClass = 'text-amber';
  }

  entry.innerHTML = `
    <span class="log-time">${timeStr}</span>
    <span class="log-method ${methodClass}">${method}</span>
    <span class="log-path">${escapeHtml(path)}</span>
    <span class="log-res ${statusClass}">${escapeHtml(statusText)}</span>
    <span class="log-msg">${escapeHtml(msg)}</span>
  `;

  logContainer.appendChild(entry);

  // Keep max 25 entries in console
  while (logContainer.children.length > 25) {
    logContainer.removeChild(logContainer.firstChild);
  }

  const badge = document.getElementById('consoleBadge');
  badge.textContent = `${method} ${path} (${statusText})`;
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
  toast.innerHTML = `
    <span style="font-weight: 700; font-size: 1rem;">${icon}</span>
    <span>${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ----------------------------------------
// Utilities
// ----------------------------------------
function getInitials(name) {
  if (!name) return 'U';
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map(p => p[0].toUpperCase())
    .join('');
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
