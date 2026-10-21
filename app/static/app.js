// Alumni Tracking System Frontend Logic (Week 1 - Week 6 Progression)
let allUsers = [];
let allJobs = [];
let allApplications = [];
let currentView = 'table'; // 'table' or 'grid'
let currentMainTab = 'alumni'; // 'alumni', 'jobs', 'applications'

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

function initApp() {
  checkApiHealth();
  loadUsers();
  loadJobs();
  loadApplications();
  setupEventListeners();

  // Periodic health check every 20 seconds
  setInterval(checkApiHealth, 20000);
}

// ----------------------------------------
// Event Listeners & UI Toggles
// ----------------------------------------
function setupEventListeners() {
  // Search input for alumni
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');

  if (searchInput) {
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
  }

  // Department filter
  const deptFilter = document.getElementById('deptFilter');
  if (deptFilter) {
    deptFilter.addEventListener('change', () => {
      filterAndRender();
    });
  }

  // Search input for jobs
  const jobSearchInput = document.getElementById('jobSearchInput');
  if (jobSearchInput) {
    jobSearchInput.addEventListener('input', (e) => {
      const val = e.target.value.toLowerCase().trim();
      const filtered = allJobs.filter(j => 
        j.title.toLowerCase().includes(val) || 
        j.company.toLowerCase().includes(val) ||
        String(j.id) === val
      );
      renderJobsTable(filtered);
    });
  }

  // View switches
  const viewTableBtn = document.getElementById('viewTableBtn');
  const viewGridBtn = document.getElementById('viewGridBtn');
  if (viewTableBtn) viewTableBtn.addEventListener('click', () => setView('table'));
  if (viewGridBtn) viewGridBtn.addEventListener('click', () => setView('grid'));

  // Refresh button
  const refreshBtn = document.getElementById('refreshBtn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      loadUsers();
      loadJobs();
      loadApplications();
    });
  }

  // Open Add User Modal
  const openAddModalBtn = document.getElementById('openAddModalBtn');
  if (openAddModalBtn) {
    openAddModalBtn.addEventListener('click', () => openAddModal());
  }

  // Seed Data Button (Week 5 & 6: Factory & Seeder)
  const seedBtn = document.getElementById('seedDataBtn');
  if (seedBtn) {
    seedBtn.addEventListener('click', async () => {
      seedBtn.disabled = true;
      const originalText = seedBtn.innerHTML;
      seedBtn.innerHTML = '🌱 Tohumlanıyor...';
      try {
        const res = await fetch('/api/seed?count=50', { method: 'POST' });
        const data = await res.json();
        showToast(data.message || 'Veritabanı başarıyla tohumlandı!', 'success');
        logApiEvent('POST', '/api/seed', '200 OK', 'Seed complete');
        await loadUsers();
        await loadJobs();
        await loadApplications();
      } catch (err) {
        showToast('Tohum verisi eklenirken hata oluştu!', 'error');
        logApiEvent('POST', '/api/seed', 'ERR', err.message);
      } finally {
        seedBtn.disabled = false;
        seedBtn.innerHTML = originalText;
      }
    });
  }

  // Toggle API Console
  const toggleConsoleBtn = document.getElementById('toggleConsoleBtn');
  if (toggleConsoleBtn) {
    toggleConsoleBtn.addEventListener('click', () => {
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
  }

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
// Main Tab Switching (Week 6 Multi-Entity)
// ----------------------------------------
function switchMainTab(tab) {
  currentMainTab = tab;

  const btnAlumni = document.getElementById('tabBtnAlumni');
  const btnJobs = document.getElementById('tabBtnJobs');
  const btnApps = document.getElementById('tabBtnApps');

  const contentAlumni = document.getElementById('alumniTabContent');
  const contentJobs = document.getElementById('jobsTabContent');
  const contentApps = document.getElementById('applicationsTabContent');

  btnAlumni.classList.toggle('active', tab === 'alumni');
  btnJobs.classList.toggle('active', tab === 'jobs');
  btnApps.classList.toggle('active', tab === 'applications');

  contentAlumni.style.display = tab === 'alumni' ? 'block' : 'none';
  contentJobs.style.display = tab === 'jobs' ? 'block' : 'none';
  contentApps.style.display = tab === 'applications' ? 'block' : 'none';

  if (tab === 'jobs') loadJobs();
  if (tab === 'applications') loadApplications();
}

// ----------------------------------------
// API Health & Database Status
// ----------------------------------------
async function checkApiHealth() {
  const indicator = document.getElementById('healthIndicator');
  const statusText = document.getElementById('healthStatusText');

  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    if (res.ok && data.status === 'ok') {
      indicator.className = 'health-indicator online';
      statusText.textContent = 'API & DB Aktif';
    } else {
      indicator.className = 'health-indicator degraded';
      statusText.textContent = 'Servis Yanıt Vermiyor';
    }
  } catch (err) {
    indicator.className = 'health-indicator offline';
    statusText.textContent = 'Bağlantı Hatası';
  }
}

// ----------------------------------------
// TAB 1: USERS (MEZUNLAR)
// ----------------------------------------
async function loadUsers() {
  const spinner = document.getElementById('loadingSpinner');
  const emptyState = document.getElementById('emptyState');
  const tableView = document.getElementById('tableView');
  const gridView = document.getElementById('gridView');

  spinner.style.display = 'flex';
  emptyState.style.display = 'none';
  tableView.style.display = 'none';
  gridView.style.display = 'none';

  try {
    const res = await fetch('/api/users');
    const data = await res.json();

    if (res.ok) {
      allUsers = data;
      logApiEvent('GET', '/api/users', '200 OK', `${allUsers.length} mezun yüklendi`);
      populateDepartmentFilter(allUsers);
      updateUserStats(allUsers);
      filterAndRender();
    } else {
      showToast('Kullanıcılar yüklenemedi!', 'error');
      logApiEvent('GET', '/api/users', `${res.status}`, 'Hata');
    }
  } catch (err) {
    showToast('Sunucu ile bağlantı kurulamadı.', 'error');
    logApiEvent('GET', '/api/users', 'ERR', err.message);
  } finally {
    spinner.style.display = 'none';
  }
}

function filterAndRender() {
  const searchInput = document.getElementById('searchInput');
  const deptFilter = document.getElementById('deptFilter');

  const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const selectedDept = deptFilter ? deptFilter.value : '';

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
      <td><a href="mailto:${escapeHtml(user.email)}" class="email-link">${escapeHtml(user.email)}</a></td>
      <td><span class="dept-badge">${escapeHtml(user.department)}</span></td>
      <td style="text-align: right;">
        <div class="actions-group">
          <button class="action-btn" onclick="inspectUser(${user.id})" title="Detay & İlanlar (Include: GET /api/users/:id?include=jobs)">
            Detay
          </button>
          <button class="action-btn" onclick="openAddJobForUser(${user.id})" style="background: rgba(99, 102, 241, 0.15); color: #a5b4fc; border: 1px solid #6366f1;" title="Bu Mezun İçin İlan Aç (Nested: POST /api/users/:id/jobs)">
            + İlan
          </button>
          <button class="action-btn edit-btn" onclick="openEditModal(${user.id})" title="Düzenle (PUT/PATCH)">
            Düzenle
          </button>
          <button class="action-btn del-btn" onclick="openDeleteModal(${user.id}, '${escapeHtml(user.name)}')" title="Sil (RESTRICT Kuralı)">
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
          <a href="mailto:${escapeHtml(user.email)}" class="email-link">${escapeHtml(user.email)}</a>
        </div>
      </div>
      <div class="card-actions">
        <button class="btn btn-secondary btn-sm" onclick="inspectUser(${user.id})">Detay (Include)</button>
        <button class="btn btn-secondary btn-sm" onclick="openAddJobForUser(${user.id})">+ İlan Aç</button>
        <button class="btn btn-secondary btn-sm" onclick="openEditModal(${user.id})">Düzenle</button>
        <button class="btn btn-danger btn-sm" onclick="openDeleteModal(${user.id}, '${escapeHtml(user.name)}')">Sil</button>
      </div>
    `;
    grid.appendChild(card);
  });
}

function populateDepartmentFilter(users) {
  const deptSelect = document.getElementById('deptFilter');
  if (!deptSelect) return;
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

function updateUserStats(users) {
  document.getElementById('statTotalUsers').textContent = users.length;
  document.getElementById('tabCounterAlumni').textContent = users.length;
}

// ----------------------------------------
// User CRUD Operations
// ----------------------------------------
async function handleCreateUser(e) {
  e.preventDefault();
  const idVal = document.getElementById('addUserId').value.trim();
  const name = document.getElementById('addUserName').value.trim();
  const email = document.getElementById('addUserEmail').value.trim();
  const department = document.getElementById('addUserDepartment').value.trim();

  const payload = { name, email, department };
  if (idVal) payload.id = parseInt(idVal, 10);

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
      showToast(`Yeni mezun #${data.id} başarıyla eklendi! (201 Created)`, 'success');
      logApiEvent('POST', '/api/users', '201 Created', `ID: ${data.id} - ${data.name}`);
      closeModal('addModal');
      document.getElementById('addUserForm').reset();
      loadUsers();
    } else {
      showToast(data.detail || 'Kullanıcı eklenemedi.', 'error');
      logApiEvent('POST', '/api/users', `${res.status}`, data.detail);
    }
  } catch (err) {
    showToast('Sunucu hatası oluştu!', 'error');
    logApiEvent('POST', '/api/users', 'ERR', err.message);
  } finally {
    saveBtn.disabled = false;
  }
}

async function handleUpdateUser(e) {
  e.preventDefault();
  const userId = document.getElementById('editUserId').value;
  const method = document.querySelector('input[name="updateMethod"]:checked').value;

  const name = document.getElementById('editUserName').value.trim();
  const email = document.getElementById('editUserEmail').value.trim();
  const department = document.getElementById('editUserDepartment').value.trim();

  let payload = {};
  if (method === 'PUT') {
    payload = { name, email, department };
  } else {
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

async function confirmDeleteUser() {
  const userId = document.getElementById('deleteUserId').value;

  try {
    const res = await fetch(`/api/users/${userId}`, { method: 'DELETE' });

    if (res.status === 204) {
      showToast(`Mezun #${userId} silindi. (204 No Content)`, 'info');
      logApiEvent('DELETE', `/api/users/${userId}`, '204 No Content', `ID: ${userId} silindi`);
      closeModal('deleteModal');
      loadUsers();
    } else if (res.status === 409) {
      // RESTRICT rule violation!
      const data = await res.json();
      showToast(data.detail || 'Bu mezunun aktif ilanları var, silinemez! (409 Conflict)', 'warning');
      logApiEvent('DELETE', `/api/users/${userId}`, '409 Conflict', data.detail);
      closeModal('deleteModal');
    } else {
      const data = await res.json();
      showToast(data.detail || 'Silme işlemi başarısız.', 'error');
      logApiEvent('DELETE', `/api/users/${userId}`, `${res.status}`, data.detail);
    }
  } catch (err) {
    showToast('Silme işlemi sırasında hata oluştu.', 'error');
    logApiEvent('DELETE', `/api/users/${userId}`, 'ERR', err.message);
  }
}

// Inspect with Include: GET /api/users/:id?include=jobs
async function inspectUser(userId) {
  try {
    const res = await fetch(`/api/users/${userId}?include=jobs`);
    const user = await res.json();

    if (res.ok) {
      logApiEvent('GET', `/api/users/${userId}?include=jobs`, `${res.status} OK`, `${user.name} (Include Jobs)`);

      const body = document.getElementById('detailModalBody');
      const jobsList = user.jobs && user.jobs.length > 0 ? user.jobs.map(j => `
        <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 6px; padding: 0.6rem 0.8rem; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <strong style="color: #f8fafc; font-size: 0.95rem;">${escapeHtml(j.title)}</strong>
            <span style="color: #a5b4fc; font-size: 0.85rem; margin-left: 0.4rem;">@ ${escapeHtml(j.company)}</span>
          </div>
          <span style="font-size: 0.75rem; color: #cbd5e1; background: rgba(0,0,0,0.3); padding: 0.15rem 0.4rem; border-radius: 4px;">İlan #${j.id}</span>
        </div>
      `).join('') : '<p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">Bu mezuna ait açılmış bir iş ilanı henüz yok.</p>';

      body.innerHTML = `
        <div style="display:flex; align-items:center; gap: 1rem; margin-bottom: 1.25rem;">
          <div class="user-avatar" style="width: 58px; height: 58px; font-size: 1.3rem;">
            ${getInitials(user.name)}
          </div>
          <div>
            <h3 style="font-size: 1.25rem; font-weight: 700; color:#fff;">${escapeHtml(user.name)}</h3>
            <span class="dept-badge">${escapeHtml(user.department)}</span>
          </div>
        </div>

        <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 1rem; font-family: monospace; font-size: 0.85rem; display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1.25rem;">
          <div><strong style="color: #94a3b8;">Kayıt ID:</strong> <span style="color:#60a5fa;">#${user.id}</span></div>
          <div><strong style="color: #94a3b8;">E-posta:</strong> <span style="color:#f8fafc;">${escapeHtml(user.email)}</span></div>
          <div><strong style="color: #94a3b8;">Bölüm:</strong> <span style="color:#a5b4fc;">${escapeHtml(user.department)}</span></div>
        </div>

        <div style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <h4 style="margin: 0; color: #f8fafc; font-size: 0.95rem;">💼 Açtığı İş İlanları (Include - One answer, two tables)</h4>
            <span style="font-size: 0.75rem; background: #4f46e5; color: #fff; padding: 0.1rem 0.5rem; border-radius: 999px;">${user.jobs ? user.jobs.length : 0} İlan</span>
          </div>
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            ${jobsList}
          </div>
        </div>
      `;
      openModal('detailModal');
    } else {
      showToast(user.detail || 'Kullanıcı bulunamadı.', 'error');
    }
  } catch (err) {
    showToast('Kullanıcı detayı alınamadı.', 'error');
  }
}

// ----------------------------------------
// TAB 2: JOB POSTINGS (WEEK 6)
// ----------------------------------------
async function loadJobs() {
  const spinner = document.getElementById('jobsLoadingSpinner');
  const emptyState = document.getElementById('jobsEmptyState');
  const tableWrapper = document.getElementById('jobsTableWrapper');

  if (spinner) spinner.style.display = 'flex';
  if (emptyState) emptyState.style.display = 'none';

  try {
    const res = await fetch('/api/jobs');
    const jobs = await res.json();

    if (res.ok) {
      allJobs = jobs;
      logApiEvent('GET', '/api/jobs', '200 OK', `${jobs.length} iş ilanı yüklendi`);
      document.getElementById('statTotalJobs').textContent = jobs.length;
      document.getElementById('tabCounterJobs').textContent = jobs.length;

      if (jobs.length === 0) {
        if (emptyState) emptyState.style.display = 'block';
        if (tableWrapper) tableWrapper.style.display = 'none';
      } else {
        if (emptyState) emptyState.style.display = 'none';
        if (tableWrapper) tableWrapper.style.display = 'block';
        renderJobsTable(jobs);
      }
    }
  } catch (err) {
    logApiEvent('GET', '/api/jobs', 'ERR', err.message);
  } finally {
    if (spinner) spinner.style.display = 'none';
  }
}

function renderJobsTable(jobs) {
  const tbody = document.getElementById('jobsTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  jobs.forEach(job => {
    const owner = allUsers.find(u => u.id === job.user_id);
    const ownerName = owner ? owner.name : `Mezun #${job.user_id}`;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><span class="id-badge">#${job.id}</span></td>
      <td>
        <strong style="color: #f8fafc; font-size: 0.95rem;">${escapeHtml(job.title)}</strong>
      </td>
      <td>
        <span style="color: #a5b4fc; font-weight: 600;">🏢 ${escapeHtml(job.company)}</span>
      </td>
      <td>
        <span class="user-cell" style="cursor: pointer;" onclick="inspectUser(${job.user_id})">
          <span style="color: #93c5fd;">👤 ${escapeHtml(ownerName)}</span>
          <span style="font-size: 0.75rem; color: #64748b; margin-left: 0.3rem;">(#${job.user_id})</span>
        </span>
      </td>
      <td>
        <button class="action-btn" onclick="openViewApplicantsModal(${job.id}, '${escapeHtml(job.title)}')" style="background: rgba(16, 185, 129, 0.15); color: #a7f3d0; border: 1px solid #10b981;">
          👥 Başvuranları Gör
        </button>
      </td>
      <td style="text-align: right;">
        <div class="actions-group">
          <button class="action-btn" onclick="openApplyJobModal(${job.id}, '${escapeHtml(job.title)}', '${escapeHtml(job.company)}')" style="background: rgba(59, 130, 246, 0.2); color: #bfdbfe; border: 1px solid #3b82f6;" title="İlana Başvuru Yap (POST /api/jobs/:id/applications)">
            ⚡ Başvur
          </button>
          <button class="action-btn del-btn" onclick="deleteJob(${job.id})" title="İlanı Sil (DELETE /api/jobs/:id)">
            Sil
          </button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function openAddJobModal() {
  populateUserDropdown('jobOwnerSelect');
  openModal('addJobModal');
}

function openAddJobForUser(userId) {
  openAddJobModal();
  const select = document.getElementById('jobOwnerSelect');
  if (select) select.value = userId;
}

function populateUserDropdown(selectId) {
  const select = document.getElementById(selectId);
  if (!select) return;
  select.innerHTML = '<option value="">Mezun Seçin...</option>';
  allUsers.forEach(u => {
    const opt = document.createElement('option');
    opt.value = u.id;
    opt.textContent = `#${u.id} - ${u.name} (${u.department})`;
    select.appendChild(opt);
  });
}

// Nested Route: POST /api/users/:id/jobs
async function handleCreateJob(e) {
  e.preventDefault();
  const userId = document.getElementById('jobOwnerSelect').value;
  const title = document.getElementById('jobTitle').value.trim();
  const company = document.getElementById('jobCompany').value.trim();

  if (!userId) {
    showToast('Lütfen ilanı açacak mezunu seçin.', 'warning');
    return;
  }

  try {
    const res = await fetch(`/api/users/${userId}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, company })
    });
    const data = await res.json();

    if (res.status === 201) {
      showToast(`Yeni iş ilanı oluşturuldu! (201 Created)`, 'success');
      logApiEvent('POST', `/api/users/${userId}/jobs`, '201 Created', `${data.title} @ ${data.company}`);
      closeModal('addJobModal');
      document.getElementById('addJobForm').reset();
      loadJobs();
    } else {
      showToast(data.detail || 'İlan oluşturulamadı.', 'error');
      logApiEvent('POST', `/api/users/${userId}/jobs`, `${res.status}`, data.detail);
    }
  } catch (err) {
    showToast('Sunucu hatası!', 'error');
  }
}

async function deleteJob(jobId) {
  if (!confirm(`İlan #${jobId} silinsin mi? Bağlı başvurular da temizlenecektir.`)) return;

  try {
    const res = await fetch(`/api/jobs/${jobId}`, { method: 'DELETE' });
    if (res.status === 204) {
      showToast(`İlan #${jobId} silindi.`, 'info');
      logApiEvent('DELETE', `/api/jobs/${jobId}`, '204 No Content', `İlan silindi`);
      loadJobs();
      loadApplications();
    } else {
      showToast('İlan silinemedi.', 'error');
    }
  } catch (err) {
    showToast('Hata oluştu.', 'error');
  }
}

// ----------------------------------------
// TAB 3: APPLICATIONS (WEEK 6)
// ----------------------------------------
async function loadApplications() {
  const spinner = document.getElementById('appsLoadingSpinner');
  const emptyState = document.getElementById('appsEmptyState');
  const tableWrapper = document.getElementById('appsTableWrapper');

  if (spinner) spinner.style.display = 'flex';
  if (emptyState) emptyState.style.display = 'none';

  try {
    const res = await fetch('/api/applications');
    const apps = await res.json();

    if (res.ok) {
      allApplications = apps;
      logApiEvent('GET', '/api/applications', '200 OK', `${apps.length} başvuru yüklendi`);
      document.getElementById('statTotalApps').textContent = apps.length;
      document.getElementById('tabCounterApps').textContent = apps.length;

      if (apps.length === 0) {
        if (emptyState) emptyState.style.display = 'block';
        if (tableWrapper) tableWrapper.style.display = 'none';
      } else {
        if (emptyState) emptyState.style.display = 'none';
        if (tableWrapper) tableWrapper.style.display = 'block';
        renderApplicationsTable(apps);
      }
    }
  } catch (err) {
    logApiEvent('GET', '/api/applications', 'ERR', err.message);
  } finally {
    if (spinner) spinner.style.display = 'none';
  }
}

function renderApplicationsTable(apps) {
  const tbody = document.getElementById('appsTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  apps.forEach(app => {
    const applicant = allUsers.find(u => u.id === app.user_id);
    const applicantName = applicant ? applicant.name : `Mezun #${app.user_id}`;

    const job = allJobs.find(j => j.id === app.job_posting_id);
    const jobTitle = job ? `${job.title} (@ ${job.company})` : `İlan #${app.job_posting_id}`;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><span class="id-badge">#${app.id}</span></td>
      <td>
        <strong style="color: #93c5fd; cursor: pointer;" onclick="inspectUser(${app.user_id})">👤 ${escapeHtml(applicantName)}</strong>
        <span style="font-size: 0.75rem; color: #64748b; margin-left: 0.3rem;">(#${app.user_id})</span>
      </td>
      <td>
        <strong style="color: #f8fafc;">💼 ${escapeHtml(jobTitle)}</strong>
      </td>
      <td>
        <span class="status-pill status-${app.status}">${app.status}</span>
      </td>
      <td style="text-align: right;">
        <div class="actions-group">
          <select class="custom-select" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onchange="updateApplicationStatus(${app.id}, this.value)">
            <option value="applied" ${app.status === 'applied' ? 'selected' : ''}>applied</option>
            <option value="interview" ${app.status === 'interview' ? 'selected' : ''}>interview</option>
            <option value="accepted" ${app.status === 'accepted' ? 'selected' : ''}>accepted</option>
            <option value="rejected" ${app.status === 'rejected' ? 'selected' : ''}>rejected</option>
          </select>
          <button class="action-btn del-btn" onclick="deleteApplication(${app.id})" title="Geri Çek (DELETE)">
            Geri Çek
          </button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function openApplyJobModal(jobId, jobTitle, jobCompany) {
  document.getElementById('applyJobId').value = jobId;
  document.getElementById('applyJobTitle').textContent = jobTitle;
  document.getElementById('applyJobCompany').textContent = jobCompany;
  populateUserDropdown('applicantUserSelect');
  openModal('applyJobModal');
}

// Applications Route: POST /api/jobs/:id/applications (Enforces UNIQUE & 409 Conflict)
async function handleApplyToJob(e) {
  e.preventDefault();
  const jobId = document.getElementById('applyJobId').value;
  const userId = document.getElementById('applicantUserSelect').value;

  if (!userId) {
    showToast('Lütfen başvuru yapacak mezunu seçin.', 'warning');
    return;
  }

  try {
    const res = await fetch(`/api/jobs/${jobId}/applications`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId: parseInt(userId, 10) })
    });
    const data = await res.json();

    if (res.status === 201) {
      showToast(`Başvuru başarıyla oluşturuldu! (201 Created)`, 'success');
      logApiEvent('POST', `/api/jobs/${jobId}/applications`, '201 Created', `User #${userId} applied`);
      closeModal('applyJobModal');
      loadApplications();
      loadJobs();
    } else if (res.status === 409) {
      // UNIQUE (user_id, job_posting_id) constraint triggered!
      showToast(`Bu mezun bu ilana daha önce başvurmuş! (409 Conflict)`, 'warning');
      logApiEvent('POST', `/api/jobs/${jobId}/applications`, '409 Conflict', data.detail);
    } else {
      showToast(data.detail || 'Başvuru yapılamadı.', 'error');
      logApiEvent('POST', `/api/jobs/${jobId}/applications`, `${res.status}`, data.detail);
    }
  } catch (err) {
    showToast('Sunucu hatası!', 'error');
  }
}

// Two Lists: GET /api/jobs/:id/applicants (List of User objects)
async function openViewApplicantsModal(jobId, jobTitle) {
  document.getElementById('applicantsModalTitle').textContent = `İlana Başvuranlar: ${jobTitle}`;
  const modalBody = document.getElementById('applicantsModalBody');
  modalBody.innerHTML = '<p style="color: #94a3b8;">Yükleniyor...</p>';
  openModal('applicantsModal');

  try {
    const res = await fetch(`/api/jobs/${jobId}/applicants`);
    const applicants = await res.json();

    if (res.ok) {
      logApiEvent('GET', `/api/jobs/${jobId}/applicants`, '200 OK', `${applicants.length} başvuran`);
      if (applicants.length === 0) {
        modalBody.innerHTML = '<p style="color: #94a3b8;">Henüz bu ilana başvuran bir mezun yok.</p>';
      } else {
        modalBody.innerHTML = applicants.map(u => `
          <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <div class="user-avatar" style="width: 36px; height: 36px; font-size: 0.85rem;">${getInitials(u.name)}</div>
              <div>
                <strong style="color: #f8fafc; font-size: 0.95rem;">${escapeHtml(u.name)}</strong>
                <div style="font-size: 0.8rem; color: #94a3b8;">${escapeHtml(u.email)} • <span style="color: #a5b4fc;">${escapeHtml(u.department)}</span></div>
              </div>
            </div>
            <span class="id-badge">#${u.id}</span>
          </div>
        `).join('');
      }
    }
  } catch (err) {
    modalBody.innerHTML = '<p style="color: #ef4444;">Başvuranlar alınamadı.</p>';
  }
}

// Direct Application PATCH: update status
async function updateApplicationStatus(appId, newStatus) {
  try {
    const res = await fetch(`/api/applications/${appId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    if (res.ok) {
      showToast(`Başvuru #${appId} durumu '${newStatus}' olarak güncellendi!`, 'success');
      logApiEvent('PATCH', `/api/applications/${appId}`, '200 OK', `Status: ${newStatus}`);
      loadApplications();
    } else {
      showToast('Durum güncellenemedi.', 'error');
    }
  } catch (err) {
    showToast('Hata oluştu.', 'error');
  }
}

// Direct Application DELETE: withdraw
async function deleteApplication(appId) {
  if (!confirm(`Başvuru #${appId} geri çekilsin mi?`)) return;

  try {
    const res = await fetch(`/api/applications/${appId}`, { method: 'DELETE' });
    if (res.status === 204) {
      showToast(`Başvuru #${appId} geri çekildi. (204 No Content)`, 'info');
      logApiEvent('DELETE', `/api/applications/${appId}`, '204 No Content', `Başvuru silindi`);
      loadApplications();
    }
  } catch (err) {
    showToast('Hata oluştu.', 'error');
  }
}

// ----------------------------------------
// Modals Handling
// ----------------------------------------
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('active');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('active');
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

  document.querySelector('input[name="updateMethod"][value="PUT"]').checked = true;
  handleMethodToggle('PUT');
  openModal('editModal');
}

function handleMethodToggle(method) {
  const badge = document.getElementById('editMethodBadge');
  const title = document.getElementById('editModalTitle');
  if (method === 'PUT') {
    badge.className = 'badge tag-put';
    badge.textContent = 'PUT /api/users/:id';
    title.textContent = 'Tam Güncelleme (PUT)';
  } else {
    badge.className = 'badge tag-patch';
    badge.textContent = 'PATCH /api/users/:id';
    title.textContent = 'Kısmi Güncelleme (PATCH)';
  }
}

function openDeleteModal(userId, userName) {
  document.getElementById('deleteUserId').value = userId;
  document.getElementById('deleteUserName').textContent = userName;
  openModal('deleteModal');
}

// ----------------------------------------
// Live API Console & Toasts
// ----------------------------------------
function logApiEvent(method, path, statusText, msg = '') {
  const logContainer = document.getElementById('consoleLog');
  if (!logContainer) return;

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
  while (logContainer.children.length > 30) {
    logContainer.removeChild(logContainer.firstChild);
  }

  const badge = document.getElementById('consoleBadge');
  if (badge) badge.textContent = `${method} ${path} (${statusText})`;
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
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
