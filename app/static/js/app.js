/**
 * Personal AI Manager - Executive Dashboard Logic
 * Full suite: Briefings, Tasks, Reminders, Approvals, Profile, Job Discovery & Fraud Check, Resume Studio
 */

const state = {
  activeTab: 'overview',
  profile: null,
  tasks: [],
  reminders: [],
  approvals: [],
  jobs: [],
  applications: [],
  masterResume: null,
  activeTailored: null,
  briefing: null,
  systemStatus: null
};

// DOM Elements
const elements = {
  pageTitle: document.getElementById('page-title'),
  timeDisplay: document.getElementById('time-display'),
  modeSelect: document.getElementById('mode-select'),
  navItems: document.querySelectorAll('.nav-item'),
  tabContents: document.querySelectorAll('.tab-content'),
  
  // Briefing
  briefingGreeting: document.getElementById('briefing-greeting'),
  briefingSummary: document.getElementById('briefing-summary'),
  briefingPrioritiesList: document.getElementById('briefing-priorities-list'),
  briefingRecommendationsList: document.getElementById('briefing-recommendations-list'),
  btnRefreshBriefing: document.getElementById('btn-refresh-briefing'),
  
  // Badges & Metrics
  badgePendingTasks: document.getElementById('badge-pending-tasks'),
  badgeActiveReminders: document.getElementById('badge-active-reminders'),
  badgePendingApprovals: document.getElementById('badge-pending-approvals'),
  badgeJobsCount: document.getElementById('badge-jobs-count'),
  badgeApplicationsCount: document.getElementById('badge-applications-count'),
  
  metricPendingTasks: document.getElementById('metric-pending-tasks'),
  metricOverdueTasks: document.getElementById('metric-overdue-tasks'),
  metricActiveReminders: document.getElementById('metric-active-reminders'),
  metricPendingApprovals: document.getElementById('metric-pending-approvals'),
  metricCompletedTasks: document.getElementById('metric-completed-tasks'),
  
  // Tasks Tab
  tasksContainer: document.getElementById('tasks-container'),
  taskFilterStatus: document.getElementById('task-filter-status'),
  taskFilterPriority: document.getElementById('task-filter-priority'),
  taskFilterCategory: document.getElementById('task-filter-category'),
  
  // Task Modal
  taskModal: document.getElementById('task-modal'),
  btnOpenTaskModal: document.getElementById('btn-open-task-modal'),
  btnAddTaskPanel: document.getElementById('btn-add-task-panel'),
  btnCloseTaskModal: document.getElementById('btn-close-task-modal'),
  btnCancelTaskModal: document.getElementById('btn-cancel-task-modal'),
  btnSaveTask: document.getElementById('btn-save-task'),
  modalTaskId: document.getElementById('modal-task-id'),
  modalTaskTitle: document.getElementById('modal-task-title'),
  modalTaskDesc: document.getElementById('modal-task-desc'),
  modalTaskDue: document.getElementById('modal-task-due'),
  modalTaskPriority: document.getElementById('modal-task-priority'),
  modalTaskCategory: document.getElementById('modal-task-category'),
  modalTaskReminder: document.getElementById('modal-task-reminder'),
  modalTaskConfirmed: document.getElementById('modal-task-confirmed'),
  
  // Jobs Tab
  jobsContainer: document.getElementById('jobs-container'),
  btnDiscoverJobs: document.getElementById('btn-discover-jobs'),
  btnAddJobManual: document.getElementById('btn-add-job-manual'),
  jobFilterVerification: document.getElementById('job-filter-verification'),
  jobFilterRemote: document.getElementById('job-filter-remote'),
  
  // Job Add Modal
  jobModal: document.getElementById('job-modal'),
  btnCloseJobModal: document.getElementById('btn-close-job-modal'),
  btnCancelJobModal: document.getElementById('btn-cancel-job-modal'),
  btnSaveJob: document.getElementById('btn-save-job'),
  modalJobTitle: document.getElementById('modal-job-title'),
  modalJobCompany: document.getElementById('modal-job-company'),
  modalJobLocation: document.getElementById('modal-job-location'),
  modalJobUrl: document.getElementById('modal-job-url'),
  modalJobDesc: document.getElementById('modal-job-desc'),
  
  // Career & Resume Studio Tab
  masterResumeSummaryCard: document.getElementById('master-resume-summary-card'),
  masterAtsScore: document.getElementById('master-ats-score'),
  applicationsContainer: document.getElementById('applications-container'),
  
  // Tailored Modal
  tailoredModal: document.getElementById('tailored-modal'),
  tailoredModalTitle: document.getElementById('tailored-modal-title'),
  tailoredModalBody: document.getElementById('tailored-modal-body'),
  btnCloseTailoredModal: document.getElementById('btn-close-tailored-modal'),
  btnCloseTailoredBtn: document.getElementById('btn-close-tailored-btn'),
  btnTrackThisApp: document.getElementById('btn-track-this-app'),
  
  // Reminders Tab
  remindersContainer: document.getElementById('reminders-container'),
  btnTriggerDueReminders: document.getElementById('btn-trigger-due-reminders'),
  
  // Approvals & Audit Tab
  approvalsContainer: document.getElementById('approvals-container'),
  auditLogsContainer: document.getElementById('audit-logs-container'),
  
  // Profile Tab
  profFullname: document.getElementById('prof-fullname'),
  profEducation: document.getElementById('prof-education'),
  profCollege: document.getElementById('prof-college'),
  profGraduation: document.getElementById('prof-graduation'),
  profTimezone: document.getElementById('prof-timezone'),
  profOs: document.getElementById('prof-os'),
  profInterests: document.getElementById('prof-interests'),
  profObjectives: document.getElementById('prof-objectives'),
  profSkills: document.getElementById('prof-skills'),
  profBudget: document.getElementById('prof-budget'),
  btnSaveProfile: document.getElementById('btn-save-profile'),
  sidebarUserName: document.getElementById('sidebar-user-name'),
  sidebarUserRole: document.getElementById('sidebar-user-role'),
  
  // System Tab
  backupsContainer: document.getElementById('backups-container'),
  btnCreateBackup: document.getElementById('btn-create-backup'),
  systemStatusInfo: document.getElementById('system-status-info'),

  // Communications & MCP Tab
  badgeEmailsCount: document.getElementById('badge-emails-count'),
  btnSyncGmail: document.getElementById('btn-sync-gmail'),
  btnSyncLinkedin: document.getElementById('btn-sync-linkedin'),
  btnConfigMcp: document.getElementById('btn-config-mcp'),
  mcpConfigModal: document.getElementById('mcp-config-modal'),
  btnCloseMcpModal: document.getElementById('btn-close-mcp-modal'),
  btnCloseMcpBtn: document.getElementById('btn-close-mcp-btn'),
  emailsContainer: document.getElementById('emails-container'),
  inboxCountTag: document.getElementById('inbox-count-tag'),
  linkedinCountTag: document.getElementById('linkedin-count-tag'),
  liViewActivity: document.getElementById('li-view-activity'),
  liViewPost: document.getElementById('li-view-post'),
  liViewNote: document.getElementById('li-view-note'),
  btnLiTabActivity: document.getElementById('btn-li-tab-activity'),
  btnLiTabPost: document.getElementById('btn-li-tab-post'),
  btnLiTabNote: document.getElementById('btn-li-tab-note'),
  btnGeneratePost: document.getElementById('btn-generate-post'),
  btnGenerateNote: document.getElementById('btn-generate-note'),
  liPostTopic: document.getElementById('li-post-topic'),
  liPostResult: document.getElementById('li-post-result'),
  liPostHook: document.getElementById('li-post-hook'),
  liPostBody: document.getElementById('li-post-body'),
  liPostHashtags: document.getElementById('li-post-hashtags'),
  liNoteName: document.getElementById('li-note-name'),
  liNoteRole: document.getElementById('li-note-role'),
  liNoteCompany: document.getElementById('li-note-company'),
  liNoteResult: document.getElementById('li-note-result'),
  liNoteChars: document.getElementById('li-note-chars'),
  liNoteBody: document.getElementById('li-note-body'),
  mcpGmailStatusBadge: document.getElementById('mcp-gmail-status-badge'),
  mcpGmailMode: document.getElementById('mcp-gmail-mode'),
  mcpGmailAddr: document.getElementById('mcp-gmail-addr'),
  mcpLinkedinStatusBadge: document.getElementById('mcp-linkedin-status-badge'),
  mcpLinkedinMode: document.getElementById('mcp-linkedin-mode'),
  mcpLinkedinSession: document.getElementById('mcp-linkedin-session')
};


// Utilities
const api = {
  async get(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    return res.json();
  },
  async post(url, data = null) {
    const options = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    };
    if (data) options.body = JSON.stringify(data);
    const res = await fetch(url, options);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },
  async put(url, data) {
    const res = await fetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },
  async delete(url) {
    const res = await fetch(url, { method: 'DELETE' });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    return true;
  }
};

// Live Clock
function startLiveClock() {
  function update() {
    const now = new Date();
    const tz = (state.profile && state.profile.timezone) ? state.profile.timezone : 'Asia/Kolkata';
    try {
      const formatted = new Intl.DateTimeFormat('en-IN', {
        timeZone: tz,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
        weekday: 'short',
        month: 'short',
        day: 'numeric'
      }).format(now);
      elements.timeDisplay.textContent = formatted;
    } catch {
      elements.timeDisplay.textContent = now.toLocaleTimeString();
    }
  }
  update();
  setInterval(update, 1000);
}

// Tab Switching
function setupTabs() {
  const titles = {
    overview: 'Executive Briefing',
    tasks: 'Tasks & Commitments',
    jobs: 'Job Discovery & Fraud Check',
    career: 'Resume Studio & Applications',
    comms: 'Communications & MCP (Email & LinkedIn)',
    reminders: 'Reminders & Deadlines',
    approvals: 'Security & Approvals',
    profile: 'Profile & Memory',
    system: 'Backups & System Status'
  };

  elements.navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const tab = item.getAttribute('data-tab');
      switchTab(tab);
    });
  });

  function switchTab(tab) {
    state.activeTab = tab;
    elements.pageTitle.textContent = titles[tab] || 'Dashboard';
    
    elements.navItems.forEach(i => {
      if (i.getAttribute('data-tab') === tab) i.classList.add('active');
      else i.classList.remove('active');
    });

    elements.tabContents.forEach(content => {
      if (content.id === `tab-${tab}`) content.style.display = 'block';
      else content.style.display = 'none';
    });

    if (tab === 'tasks') loadTasks();
    if (tab === 'jobs') loadJobs();
    if (tab === 'career') { loadMasterResume(); loadApplications(); }
    if (tab === 'comms') loadCommunications();
    if (tab === 'reminders') loadReminders();
    if (tab === 'approvals') loadApprovals();
    if (tab === 'profile') loadProfile();
    if (tab === 'system') loadSystemInfo();
  }
}


// Initial App Load
async function initApp() {
  startLiveClock();
  setupTabs();
  setupEventListeners();

  try {
    await Promise.all([
      loadProfile(),
      loadBriefing(),
      loadTasks(),
      loadJobs(),
      loadApplications(),
      loadCommunications(),
      loadReminders(),
      loadApprovals(),
      loadSystemInfo()
    ]);

  } catch (err) {
    console.error("Initialization error:", err);
  }
}

// Profile
async function loadProfile() {
  try {
    const prof = await api.get('/api/profile');
    state.profile = prof;
    
    elements.sidebarUserName.textContent = prof.full_name || 'Mohil';
    elements.sidebarUserRole.textContent = `${prof.education.split(' ')[0]} '27`;
    
    elements.profFullname.value = prof.full_name;
    elements.profEducation.value = prof.education;
    elements.profCollege.value = prof.college;
    elements.profGraduation.value = prof.expected_graduation;
    elements.profTimezone.value = prof.timezone;
    elements.profOs.value = prof.operating_environment;
    elements.profInterests.value = (prof.technical_interests || []).join(', ');
    elements.profObjectives.value = (prof.career_objectives || []).join(', ');
    elements.profSkills.value = (prof.existing_skills || []).join(', ');
    elements.profBudget.value = prof.budget_preference;
  } catch (err) {
    console.error("Failed to load profile:", err);
  }
}

async function saveProfile() {
  try {
    const payload = {
      full_name: elements.profFullname.value.trim(),
      education: elements.profEducation.value.trim(),
      college: elements.profCollege.value.trim(),
      expected_graduation: elements.profGraduation.value.trim(),
      timezone: elements.profTimezone.value.trim(),
      operating_environment: elements.profOs.value.trim(),
      technical_interests: elements.profInterests.value.split(',').map(s => s.trim()).filter(Boolean),
      career_objectives: elements.profObjectives.value.split(',').map(s => s.trim()).filter(Boolean),
      existing_skills: elements.profSkills.value.split(',').map(s => s.trim()).filter(Boolean),
      budget_preference: elements.profBudget.value.trim()
    };
    const updated = await api.put('/api/profile', payload);
    state.profile = updated;
    alert("Profile preferences updated successfully.");
    loadProfile();
  } catch (err) {
    alert("Failed to save profile: " + err.message);
  }
}

// Briefing
async function loadBriefing() {
  try {
    const briefing = await api.get('/api/briefing');
    state.briefing = briefing;
    
    elements.briefingGreeting.textContent = briefing.greeting;
    elements.briefingSummary.textContent = briefing.executive_summary;

    elements.briefingPrioritiesList.innerHTML = '';
    if (briefing.top_three_priorities.length === 0) {
      elements.briefingPrioritiesList.innerHTML = '<li class="briefing-item" style="color: var(--text-sub);">No pending priority tasks.</li>';
    } else {
      briefing.top_three_priorities.forEach((task, idx) => {
        const li = document.createElement('li');
        li.className = 'briefing-item';
        li.innerHTML = `<span><strong>${idx + 1}.</strong> ${escapeHtml(task.title)}</span> <span class="tag tag-${task.priority.toLowerCase().split('_')[0]}">${task.priority.replace('_', ' ')}</span>`;
        elements.briefingPrioritiesList.appendChild(li);
      });
    }

    elements.briefingRecommendationsList.innerHTML = '';
    if (briefing.recommendations.length === 0) {
      elements.briefingRecommendationsList.innerHTML = '<li class="briefing-item" style="color: var(--text-sub);">All actions up to date.</li>';
    } else {
      briefing.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.className = 'briefing-item';
        li.innerHTML = `<span>• ${escapeHtml(rec)}</span>`;
        elements.briefingRecommendationsList.appendChild(li);
      });
    }
  } catch (err) {
    console.error("Failed to load briefing:", err);
  }
}

// Tasks
async function loadTasks() {
  try {
    const status = elements.taskFilterStatus.value;
    const priority = elements.taskFilterPriority.value;
    const category = elements.taskFilterCategory.value;

    let url = '/api/tasks?';
    if (status) url += `status=${status}&`;
    if (priority) url += `priority=${priority}&`;
    if (category) url += `category=${category}&`;

    const tasks = await api.get(url);
    state.tasks = tasks;

    const pendingCount = tasks.filter(t => t.status === 'PENDING' || t.status === 'IN_PROGRESS').length;
    const completedCount = tasks.filter(t => t.status === 'COMPLETED').length;
    
    const now = new Date();
    const overdueCount = tasks.filter(t => {
      if (t.status === 'COMPLETED' || !t.due_date) return false;
      return new Date(t.due_date) < now;
    }).length;

    elements.badgePendingTasks.textContent = pendingCount;
    elements.metricPendingTasks.textContent = pendingCount;
    elements.metricCompletedTasks.textContent = completedCount;
    elements.metricOverdueTasks.textContent = overdueCount;

    renderTaskList(tasks);
  } catch (err) {
    console.error("Failed to load tasks:", err);
  }
}

function renderTaskList(tasks) {
  elements.tasksContainer.innerHTML = '';
  if (tasks.length === 0) {
    elements.tasksContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📋</div>
        <div>No tasks found matching your filter criteria.</div>
      </div>
    `;
    return;
  }

  tasks.forEach(task => {
    const div = document.createElement('div');
    div.className = `task-item ${task.status === 'COMPLETED' ? 'completed' : ''}`;
    
    const isChecked = task.status === 'COMPLETED' ? 'checked' : '';
    const pTagClass = `tag-${task.priority.toLowerCase().split('_')[0]}`;
    const pTagLabel = task.priority.replace('_', ' ');

    let dueLabel = 'No deadline';
    if (task.due_date) {
      const d = new Date(task.due_date);
      dueLabel = `Due: ${d.toLocaleDateString()} ${d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
    }

    const confirmedTag = task.is_confirmed 
      ? '<span class="tag tag-confirmed">Confirmed</span>' 
      : '<span class="tag tag-inferred">Inferred (Verify)</span>';

    div.innerHTML = `
      <div class="task-left">
        <input type="checkbox" class="task-checkbox" ${isChecked} data-task-id="${task.id}">
        <div class="task-details">
          <div class="task-title">${escapeHtml(task.title)}</div>
          ${task.description ? `<div style="font-size:0.8rem; color:var(--text-muted);">${escapeHtml(task.description)}</div>` : ''}
          <div class="task-meta">
            <span class="tag ${pTagClass}">${pTagLabel}</span>
            <span class="tag" style="background:rgba(255,255,255,0.06);">${task.status}</span>
            <span>📂 ${task.category}</span>
            <span>📅 ${dueLabel}</span>
            ${confirmedTag}
          </div>
        </div>
      </div>
      <div class="task-actions">
        <button class="btn btn-secondary btn-sm btn-edit-task" data-task-id="${task.id}">Edit</button>
        <button class="btn btn-danger btn-sm btn-delete-task" data-task-id="${task.id}">Delete</button>
      </div>
    `;

    const checkbox = div.querySelector('.task-checkbox');
    checkbox.addEventListener('change', async () => {
      try {
        if (checkbox.checked) await api.post(`/api/tasks/${task.id}/complete`);
        else await api.put(`/api/tasks/${task.id}`, { status: 'PENDING' });
        await loadTasks();
        await loadBriefing();
      } catch (e) {
        alert("Failed to update status: " + e.message);
      }
    });

    div.querySelector('.btn-delete-task').addEventListener('click', async () => {
      if (confirm(`Delete task "${task.title}"?`)) {
        await api.delete(`/api/tasks/${task.id}`);
        await loadTasks();
        await loadBriefing();
      }
    });

    div.querySelector('.btn-edit-task').addEventListener('click', () => {
      openTaskModal(task);
    });

    elements.tasksContainer.appendChild(div);
  });
}

// Jobs & Fraud Verification
async function loadJobs() {
  try {
    const ver = elements.jobFilterVerification ? elements.jobFilterVerification.value : '';
    const rem = elements.jobFilterRemote ? elements.jobFilterRemote.value : '';

    let url = '/api/career/jobs?';
    if (ver) url += `verification_status=${ver}&`;
    if (rem) url += `is_remote=${rem}&`;

    const jobs = await api.get(url);
    state.jobs = jobs;
    if (elements.badgeJobsCount) elements.badgeJobsCount.textContent = jobs.length;

    renderJobsList(jobs);
  } catch (err) {
    console.error("Failed to load jobs:", err);
  }
}

function renderJobsList(jobs) {
  if (!elements.jobsContainer) return;
  elements.jobsContainer.innerHTML = '';
  
  if (jobs.length === 0) {
    elements.jobsContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">💼</div>
        <div>No job listings found. Click 'Discover Live Jobs' or '+ Add / Inspect Job'.</div>
      </div>
    `;
    return;
  }

  jobs.forEach(job => {
    const div = document.createElement('div');
    div.className = 'task-item';
    
    // Status styling
    let verTagClass = 'tag-p2'; // Needs review
    let verLabel = 'NEEDS REVIEW';
    if (job.verification_status === 'VERIFIED_BY_EVIDENCE') {
      verTagClass = 'tag-confirmed';
      verLabel = 'VERIFIED BY EVIDENCE';
    } else if (job.verification_status === 'HIGH_RISK') {
      verTagClass = 'tag-p1';
      verLabel = 'HIGH RISK / FRAUD';
    }

    const report = job.verification_report;
    const fraudWarnings = report.suspicious_indicators.length > 0
      ? `<div style="color:#fb7185; font-size:0.8rem; margin-top:4px;">⚠️ Suspicious Indicators: ${report.suspicious_indicators.join(' | ')}</div>`
      : '';

    div.innerHTML = `
      <div class="task-left">
        <div class="task-details" style="width:100%;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="task-title">${escapeHtml(job.title)} <span style="color:var(--accent-cyan); font-weight:normal;">@ ${escapeHtml(job.company)}</span></div>
            <div class="tag tag-p3" style="font-size:0.75rem;">Match: ${job.match_score}%</div>
          </div>
          <div style="font-size:0.8rem; color:var(--text-muted);">${escapeHtml(job.suitability_explanation || '')}</div>
          ${fraudWarnings}
          <div class="task-meta" style="margin-top:6px;">
            <span class="tag ${verTagClass}">${verLabel}</span>
            <span>📍 ${escapeHtml(job.location || 'Remote')}</span>
            <span>🔗 <a href="${job.source_url}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;">Source URL</a> (${job.source_name})</span>
            ${job.matching_skills.length ? `<span>✓ Matches: ${job.matching_skills.slice(0,3).join(', ')}</span>` : ''}
          </div>
          <div style="font-size:0.75rem; color:var(--text-sub); margin-top:4px;">
            <strong>Recommendation:</strong> ${escapeHtml(report.recommended_action)}
          </div>
        </div>
      </div>
      <div class="task-actions" style="flex-direction:column; gap:0.4rem; min-width:140px;">
        <button class="btn btn-primary btn-sm btn-tailor-job" data-id="${job.id}" style="width:100%;">Tailor Resume</button>
        <button class="btn btn-secondary btn-sm btn-track-job" data-id="${job.id}" style="width:100%;">Track App</button>
      </div>
    `;

    div.querySelector('.btn-tailor-job').addEventListener('click', () => tailorResume(job.id));
    div.querySelector('.btn-track-job').addEventListener('click', () => trackApplicationDirect(job));

    elements.jobsContainer.appendChild(div);
  });
}

// Discover live jobs from Arbeitnow & Remotive
async function discoverLiveJobs() {
  if (!confirm("Query permitted live APIs (Arbeitnow & Remotive) for new Python/AI/Software opportunities?")) return;
  try {
    elements.btnDiscoverJobs.disabled = true;
    elements.btnDiscoverJobs.textContent = "Searching APIs...";
    const discovered = await api.post('/api/career/jobs/discover');
    alert(`Discovery complete! Found and analyzed ${discovered.length} relevant opportunity listing(s).`);
    await loadJobs();
    await loadBriefing();
  } catch (err) {
    alert("Discovery failed: " + err.message);
  } finally {
    elements.btnDiscoverJobs.disabled = false;
    elements.btnDiscoverJobs.textContent = "🌐 Discover Live Jobs";
  }
}

// Tailor Resume for a Job
async function tailorResume(jobId) {
  try {
    const tailored = await api.post(`/api/career/jobs/${jobId}/tailor`);
    state.activeTailored = tailored;
    
    const targetJob = state.jobs.find(j => j.id === jobId) || { company: 'Employer', title: 'Position', source_url: '' };
    
    elements.tailoredModalTitle.textContent = `Tailored Package: ${targetJob.title} @ ${targetJob.company}`;
    
    const gapAnalysis = tailored.keyword_gap_analysis;
    const missingKeys = (gapAnalysis.missing_keywords || []).join(', ') || 'None identified';
    const matchedKeys = (gapAnalysis.matched_keywords || []).join(', ') || 'None';

    elements.tailoredModalBody.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:1.25rem;">
        <div style="background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.3); border-radius:8px; padding:1rem;">
          <h4 style="font-size:0.9rem; color:var(--accent-cyan); margin-bottom:0.5rem;">🎯 ATS Alignment & Factual Integrity</h4>
          <div style="font-size:0.8rem; line-height:1.6;">
            <div><strong>Matched Skills:</strong> <span style="color:#34d399;">${escapeHtml(matchedKeys)}</span></div>
            <div><strong>Skill Gaps:</strong> <span style="color:#fbbf24;">${escapeHtml(missingKeys)}</span></div>
            <div style="margin-top:6px; color:var(--text-muted);">
              ${(tailored.changes_made || []).map(c => `• ${escapeHtml(c)}`).join('<br>')}
            </div>
          </div>
        </div>

        <div>
          <h4 style="font-size:0.9rem; margin-bottom:0.4rem;">Factual Tailored Summary</h4>
          <div style="background:rgba(0,0,0,0.3); padding:0.75rem; border-radius:6px; font-size:0.85rem; line-height:1.5;">
            ${escapeHtml(tailored.tailored_summary)}
          </div>
        </div>

        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
            <h4 style="font-size:0.9rem;">Tailored Cover Letter</h4>
            <button class="btn btn-secondary btn-sm" id="btn-copy-cover-letter">📋 Copy Letter</button>
          </div>
          <textarea class="form-textarea" id="tailored-cover-letter-text" rows="8" readonly style="font-family:inherit; font-size:0.82rem; line-height:1.6;">${escapeHtml(tailored.cover_letter)}</textarea>
        </div>

        <div>
          <h4 style="font-size:0.9rem; margin-bottom:0.4rem;">Prepared Application Answers</h4>
          <div style="background:rgba(0,0,0,0.25); padding:0.75rem; border-radius:6px; font-size:0.8rem; line-height:1.6;">
            ${Object.entries(tailored.application_answers).map(([q, a]) => `
              <div style="margin-bottom:0.5rem;">
                <strong>${escapeHtml(q)}</strong><br>
                <span style="color:var(--text-muted);">${escapeHtml(a)}</span>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;

    document.getElementById('btn-copy-cover-letter').addEventListener('click', () => {
      navigator.clipboard.writeText(tailored.cover_letter);
      alert("Cover letter copied to clipboard!");
    });

    elements.btnTrackThisApp.onclick = async () => {
      await trackApplicationDirect(targetJob, tailored.version_label);
      elements.tailoredModal.classList.remove('active');
    };

    elements.tailoredModal.classList.add('active');
  } catch (err) {
    alert("Tailoring failed: " + err.message);
  }
}

// Track Application
async function trackApplicationDirect(job, resumeVersion = "v1.0-master") {
  try {
    const payload = {
      job_id: job.id,
      company: job.company,
      position: job.title,
      job_url: job.source_url,
      resume_version: resumeVersion,
      notes: `Discovered via ${job.source_name}. Awaiting user authorization before submission.`
    };
    const created = await api.post('/api/career/applications', payload);
    alert(`Application tracked for ${job.title} at ${job.company}! Security authorization request created.`);
    await loadApplications();
    await loadApprovals();
    await loadBriefing();
  } catch (err) {
    alert("Tracking failed: " + err.message);
  }
}

// Load Master Resume & Applications
async function loadMasterResume() {
  try {
    const resume = await api.get('/api/career/resume');
    state.masterResume = resume;
    
    if (elements.masterAtsScore) elements.masterAtsScore.textContent = `ATS Score: ${resume.ats_score}/100`;
    if (elements.masterResumeSummaryCard) {
      elements.masterResumeSummaryCard.innerHTML = `
        <div style="margin-bottom:0.5rem;"><strong>Summary:</strong> ${escapeHtml(resume.summary)}</div>
        <div style="margin-bottom:0.5rem;"><strong>Education:</strong> ${resume.education.map(e => `${escapeHtml(e.degree)} (${escapeHtml(e.institution)}) - Class of ${escapeHtml(e.expected_graduation)}`).join('; ')}</div>
        <div style="margin-bottom:0.5rem;"><strong>Verified Skills:</strong> ${resume.skills.map(s => `<span class="tag tag-p3" style="margin:2px;">${escapeHtml(s)}</span>`).join(' ')}</div>
        <div><strong>Projects:</strong> ${resume.projects.map(p => `<strong>${escapeHtml(p.title)}</strong> (${(p.technologies||[]).join(', ')})`).join(' | ')}</div>
      `;
    }
  } catch (err) {
    console.error("Failed to load master resume:", err);
  }
}

async function loadApplications() {
  try {
    const apps = await api.get('/api/career/applications');
    state.applications = apps;
    if (elements.badgeApplicationsCount) elements.badgeApplicationsCount.textContent = apps.length;

    renderApplicationsList(apps);
  } catch (err) {
    console.error("Failed to load applications:", err);
  }
}

function renderApplicationsList(apps) {
  if (!elements.applicationsContainer) return;
  elements.applicationsContainer.innerHTML = '';
  
  if (apps.length === 0) {
    elements.applicationsContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📄</div>
        <div>No tracked job applications yet. Track an opportunity from the Jobs tab.</div>
      </div>
    `;
    return;
  }

  apps.forEach(app => {
    const div = document.createElement('div');
    div.className = 'task-item';
    
    let statusClass = 'tag-p3';
    if (app.status === 'READY_FOR_APPROVAL') statusClass = 'tag-p2';
    if (app.status === 'SUBMITTED' || app.status === 'OFFER') statusClass = 'tag-confirmed';
    if (app.status === 'REJECTED') statusClass = 'tag-p4';

    div.innerHTML = `
      <div class="task-left">
        <div class="task-details">
          <div class="task-title">${escapeHtml(app.position)} @ <strong>${escapeHtml(app.company)}</strong></div>
          <div class="task-meta">
            <span class="tag ${statusClass}">${app.status}</span>
            <span>Version: ${escapeHtml(app.resume_version || 'Master')}</span>
            <span>📅 Tracked: ${new Date(app.created_at).toLocaleDateString()}</span>
            ${app.job_url ? `<span>🔗 <a href="${app.job_url}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;">Job Posting</a></span>` : ''}
          </div>
          <div style="font-size:0.75rem; color:var(--text-sub); margin-top:3px;">
            Next Action: ${escapeHtml(app.next_action || 'Review')}
          </div>
        </div>
      </div>
      <div class="task-actions">
        <button class="btn btn-secondary btn-sm btn-update-stage" data-id="${app.id}">Update Status</button>
      </div>
    `;

    div.querySelector('.btn-update-stage').addEventListener('click', async () => {
      const newStatus = prompt("Enter new status (DRAFTED, READY_FOR_APPROVAL, SUBMITTED, INTERVIEW_SCHEDULED, OFFER, REJECTED):", app.status);
      if (newStatus) {
        try {
          await api.put(`/api/career/applications/${app.id}`, { status: newStatus.trim().toUpperCase() });
          await loadApplications();
          await loadBriefing();
        } catch (e) {
          alert("Update failed: " + e.message);
        }
      }
    });

    elements.applicationsContainer.appendChild(div);
  });
}

// Reminders
async function loadReminders() {
  try {
    const reminders = await api.get('/api/reminders');
    state.reminders = reminders;

    const activeCount = reminders.filter(r => r.status === 'SCHEDULED').length;
    elements.badgeActiveReminders.textContent = activeCount;
    elements.metricActiveReminders.textContent = activeCount;

    elements.remindersContainer.innerHTML = '';
    if (reminders.length === 0) {
      elements.remindersContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">⏰</div>
          <div>No active reminders. Reminders can be scheduled with tasks.</div>
        </div>
      `;
      return;
    }

    reminders.forEach(rem => {
      const div = document.createElement('div');
      div.className = 'task-item';
      
      const dt = new Date(rem.remind_at);
      const formatted = `${dt.toLocaleDateString()} ${dt.toLocaleTimeString()}`;

      let statusTagClass = 'tag-p3';
      if (rem.status === 'DELIVERED') statusTagClass = 'tag-confirmed';
      if (rem.status === 'DISMISSED') statusTagClass = 'tag-p4';

      div.innerHTML = `
        <div class="task-left">
          <div class="task-details">
            <div class="task-title">${escapeHtml(rem.delivery_message || 'Reminder')}</div>
            <div class="task-meta">
              <span class="tag ${statusTagClass}">${rem.status}</span>
              <span>⏰ Scheduled: ${formatted}</span>
              <span>🔄 Snoozed: ${rem.snooze_count} times</span>
              ${rem.delivery_timestamp ? `<span>✓ Delivered at: ${new Date(rem.delivery_timestamp).toLocaleTimeString()}</span>` : ''}
            </div>
          </div>
        </div>
        <div class="task-actions">
          <button class="btn btn-secondary btn-sm btn-snooze-rem" data-id="${rem.id}">Snooze 15m</button>
          <button class="btn btn-danger btn-sm btn-dismiss-rem" data-id="${rem.id}">Dismiss</button>
        </div>
      `;

      div.querySelector('.btn-snooze-rem').addEventListener('click', async () => {
        await api.post(`/api/reminders/${rem.id}/snooze`, { snooze_minutes: 15 });
        loadReminders();
        loadBriefing();
      });

      div.querySelector('.btn-dismiss-rem').addEventListener('click', async () => {
        await api.post(`/api/reminders/${rem.id}/dismiss`);
        loadReminders();
        loadBriefing();
      });

      elements.remindersContainer.appendChild(div);
    });
  } catch (err) {
    console.error("Failed to load reminders:", err);
  }
}

async function triggerDueReminders() {
  try {
    const delivered = await api.post('/api/reminders/process-due');
    if (delivered.length > 0) alert(`Delivered ${delivered.length} due reminder(s)!`);
    else alert("No reminders are currently due at this moment.");
    await loadReminders();
    await loadBriefing();
  } catch (err) {
    alert("Check failed: " + err.message);
  }
}

// Approvals & Audit Log
async function loadApprovals() {
  try {
    const approvals = await api.get('/api/approvals');
    const logs = await api.get('/api/approvals/audit/logs?limit=30');

    state.approvals = approvals;
    const pendingCount = approvals.filter(a => a.status === 'PENDING').length;
    elements.badgePendingApprovals.textContent = pendingCount;
    elements.metricPendingApprovals.textContent = pendingCount;

    elements.approvalsContainer.innerHTML = '';
    if (approvals.length === 0) {
      elements.approvalsContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">🛡️</div>
          <div>No pending authorizations. System is operating safely within allowed bounds.</div>
        </div>
      `;
    } else {
      approvals.forEach(appr => {
        const div = document.createElement('div');
        div.className = 'task-item';
        
        div.innerHTML = `
          <div class="task-left">
            <div class="task-details">
              <div class="task-title">${escapeHtml(appr.title)}</div>
              <div style="font-size:0.82rem; color:var(--text-muted);">${escapeHtml(appr.description)}</div>
              <div class="task-meta">
                <span class="tag tag-p1">Risk: ${appr.risk_level}</span>
                <span class="tag tag-status-awaiting">${appr.status}</span>
                <span>📅 ${new Date(appr.created_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
          <div class="task-actions">
            ${appr.status === 'PENDING' ? `
              <button class="btn btn-success btn-sm btn-approve" data-id="${appr.id}">Authorize</button>
              <button class="btn btn-danger btn-sm btn-reject" data-id="${appr.id}">Reject</button>
            ` : `<span style="font-size:0.8rem; color:var(--text-sub);">${appr.status} (${appr.decision_reason || 'No comment'})</span>`}
          </div>
        `;

        const btnApprove = div.querySelector('.btn-approve');
        if (btnApprove) {
          btnApprove.addEventListener('click', async () => {
            const reason = prompt("Optional authorization note:", "Approved by Mohil");
            await api.post(`/api/approvals/${appr.id}/decide`, { decision: 'APPROVED', reason });
            loadApprovals();
            loadBriefing();
          });
        }

        const btnReject = div.querySelector('.btn-reject');
        if (btnReject) {
          btnReject.addEventListener('click', async () => {
            const reason = prompt("Reason for rejection:", "Declined by user");
            await api.post(`/api/approvals/${appr.id}/decide`, { decision: 'REJECTED', reason });
            loadApprovals();
            loadBriefing();
          });
        }

        elements.approvalsContainer.appendChild(div);
      });
    }

    elements.auditLogsContainer.innerHTML = '';
    logs.forEach(log => {
      const div = document.createElement('div');
      div.className = 'task-item';
      div.style.padding = '0.75rem 1rem';
      
      div.innerHTML = `
        <div class="task-left">
          <div class="task-details">
            <div style="font-size:0.85rem; font-weight:600;">${escapeHtml(log.action_type)} <span style="color:var(--text-sub); font-size:0.75rem;">(${log.target_entity})</span></div>
            <div style="font-size:0.75rem; color:var(--text-muted); font-family:monospace;">${escapeHtml(log.details || '')}</div>
            <div class="task-meta">
              <span class="tag tag-p3">${log.mode}</span>
              <span class="tag tag-confirmed">${log.status}</span>
              <span>⏱ ${new Date(log.created_at).toLocaleTimeString()} (${new Date(log.created_at).toLocaleDateString()})</span>
            </div>
          </div>
        </div>
      `;
      elements.auditLogsContainer.appendChild(div);
    });
  } catch (err) {
    console.error("Failed to load approvals or audit logs:", err);
  }
}

// System & Backups
async function loadSystemInfo() {
  try {
    const health = await api.get('/api/system/health');
    const backups = await api.get('/api/system/backups');
    state.systemStatus = health;

    elements.modeSelect.value = health.autonomy_mode;
    elements.systemStatusInfo.innerHTML = `
      <div><strong>Status:</strong> <span style="color:#34d399;">● Operational</span></div>
      <div><strong>Version:</strong> ${health.version}</div>
      <div><strong>Active Timezone:</strong> ${health.timezone}</div>
      <div><strong>Autonomy Mode:</strong> ${health.autonomy_mode}</div>
      <div><strong>Storage Engine:</strong> SQLite 3 (WAL mode with point-in-time snapshotting)</div>
    `;

    elements.backupsContainer.innerHTML = '';
    if (backups.length === 0) {
      elements.backupsContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">💾</div>
          <div>No backups created yet. Click 'Create New Backup' to generate a snapshot.</div>
        </div>
      `;
      return;
    }

    backups.forEach(b => {
      const div = document.createElement('div');
      div.className = 'task-item';
      const sizeKB = (b.size_bytes / 1024).toFixed(1);
      
      div.innerHTML = `
        <div class="task-left">
          <div class="task-details">
            <div class="task-title">${escapeHtml(b.filename)}</div>
            <div class="task-meta">
              <span>Size: ${sizeKB} KB</span>
              <span>Created: ${new Date(b.created_at * 1000).toLocaleString()}</span>
            </div>
          </div>
        </div>
        <div class="task-actions">
          <button class="btn btn-secondary btn-sm btn-restore" data-fn="${b.filename}">Restore This Snapshot</button>
        </div>
      `;

      div.querySelector('.btn-restore').addEventListener('click', async () => {
        if (confirm(`Restore database from snapshot "${b.filename}"? Current data will be replaced by the snapshot state.`)) {
          try {
            await api.post(`/api/system/restore?filename=${encodeURIComponent(b.filename)}`);
            alert("Database successfully restored! Reloading...");
            location.reload();
          } catch (e) {
            alert("Restore error: " + e.message);
          }
        }
      });

      elements.backupsContainer.appendChild(div);
    });
  } catch (err) {
    console.error("Failed to load system info:", err);
  }
}

async function createBackup() {
  try {
    const res = await api.post('/api/system/backup');
    alert(`Backup created successfully: ${res.backup_filename}`);
    loadSystemInfo();
  } catch (err) {
    alert("Backup creation failed: " + err.message);
  }
}

async function changeAutonomyMode(e) {
  const newMode = e.target.value;
  try {
    await api.post('/api/system/mode', { mode: newMode });
    alert(`Autonomy mode updated to: ${newMode}`);
    loadApprovals();
  } catch (err) {
    alert("Failed to update mode: " + err.message);
  }
}

// Task Modal
function openTaskModal(task = null) {
  if (task) {
    elements.modalTaskId.value = task.id;
    elements.modalTaskTitle.value = task.title;
    elements.modalTaskDesc.value = task.description || '';
    elements.modalTaskDue.value = task.due_date ? task.due_date.slice(0, 16) : '';
    elements.modalTaskPriority.value = task.priority;
    elements.modalTaskCategory.value = task.category;
    elements.modalTaskReminder.value = '';
    elements.modalTaskConfirmed.checked = task.is_confirmed;
    document.getElementById('task-modal-title').textContent = 'Edit Task';
  } else {
    elements.modalTaskId.value = '';
    elements.modalTaskTitle.value = '';
    elements.modalTaskDesc.value = '';
    elements.modalTaskDue.value = '';
    elements.modalTaskPriority.value = 'P3_MEDIUM';
    elements.modalTaskCategory.value = 'PERSONAL';
    elements.modalTaskReminder.value = '';
    elements.modalTaskConfirmed.checked = true;
    document.getElementById('task-modal-title').textContent = 'Create New Task';
  }
  elements.taskModal.classList.add('active');
}

function closeTaskModal() {
  elements.taskModal.classList.remove('active');
}

async function saveTask() {
  const title = elements.modalTaskTitle.value.trim();
  if (!title) {
    alert("Task title is required.");
    return;
  }

  const taskId = elements.modalTaskId.value;
  const payload = {
    title,
    description: elements.modalTaskDesc.value.trim() || null,
    due_date: elements.modalTaskDue.value ? new Date(elements.modalTaskDue.value).toISOString() : null,
    priority: elements.modalTaskPriority.value,
    category: elements.modalTaskCategory.value,
    is_confirmed: elements.modalTaskConfirmed.checked
  };

  try {
    if (taskId) {
      await api.put(`/api/tasks/${taskId}`, payload);
    } else {
      const remMins = elements.modalTaskReminder.value ? parseInt(elements.modalTaskReminder.value) : null;
      if (remMins) payload.reminder_minutes_before = remMins;
      await api.post('/api/tasks', payload);
    }
    closeTaskModal();
    await loadTasks();
    await loadReminders();
    await loadBriefing();
  } catch (err) {
    alert("Failed to save task: " + err.message);
  }
}

// Job Modal
function openJobModal() {
  elements.modalJobTitle.value = '';
  elements.modalJobCompany.value = '';
  elements.modalJobLocation.value = 'Remote / India';
  elements.modalJobUrl.value = '';
  elements.modalJobDesc.value = '';
  elements.jobModal.classList.add('active');
}

function closeJobModal() {
  elements.jobModal.classList.remove('active');
}

async function saveJobManual() {
  const title = elements.modalJobTitle.value.trim();
  const company = elements.modalJobCompany.value.trim();
  const url = elements.modalJobUrl.value.trim();
  const desc = elements.modalJobDesc.value.trim();

  if (!title || !company || !url || !desc) {
    alert("Please fill in Title, Company, URL, and Description.");
    return;
  }

  try {
    const payload = {
      title,
      company,
      location: elements.modalJobLocation.value.trim() || 'Remote / India',
      source_url: url,
      source_name: 'Manual / Inspected',
      description: desc
    };
    const job = await api.post('/api/career/jobs', payload);
    closeJobModal();
    alert(`Job inspected and saved!\nVerification Status: ${job.verification_status}\nMatch Score: ${job.match_score}%\nRecommendation: ${job.verification_report.recommended_action}`);
    await loadJobs();
    await loadBriefing();
  } catch (err) {
    alert("Failed to save job: " + err.message);
  }
}

// ==========================================
// Communications & MCP Functions
// ==========================================
async function loadCommunications() {
  try {
    const [mcpStatus, emails, interactions] = await Promise.all([
      api.get('/api/communication/mcp/status').catch(() => null),
      api.get('/api/communication/emails?limit=50').catch(() => []),
      api.get('/api/communication/linkedin/interactions?limit=50').catch(() => [])
    ]);

    // 1. Update MCP Status Badges
    if (mcpStatus) {
      if (elements.mcpGmailMode) {
        elements.mcpGmailMode.textContent = mcpStatus.gmail.mode || 'Ready';
      }
      if (elements.mcpGmailAddr) {
        elements.mcpGmailAddr.textContent = 'Account: ' + (mcpStatus.gmail.configured_address || 'Not Configured');
      }
      if (elements.mcpGmailStatusBadge) {
        elements.mcpGmailStatusBadge.textContent = mcpStatus.gmail.credentials_present ? 'Live IMAP' : 'Simulation Sandbox';
        elements.mcpGmailStatusBadge.className = mcpStatus.gmail.credentials_present ? 'tag tag-confirmed' : 'tag tag-inferred';
      }

      if (elements.mcpLinkedinMode) {
        elements.mcpLinkedinMode.textContent = mcpStatus.linkedin.mode || 'Browser Ready';
      }
      if (elements.mcpLinkedinSession) {
        elements.mcpLinkedinSession.textContent = mcpStatus.linkedin.session_cookie_configured ? 'Authenticated Session Active' : 'Simulation Sandbox Active';
      }
      if (elements.mcpLinkedinStatusBadge) {
        elements.mcpLinkedinStatusBadge.textContent = mcpStatus.linkedin.session_cookie_configured ? 'Live Session' : 'Simulation Sandbox';
        elements.mcpLinkedinStatusBadge.className = mcpStatus.linkedin.session_cookie_configured ? 'tag tag-confirmed' : 'tag tag-inferred';
      }
    }

    // 2. Render Emails
    renderEmails(emails);

    // 3. Render LinkedIn Interactions
    renderLinkedInInteractions(interactions);

    // Update Badge
    if (elements.badgeEmailsCount) {
      elements.badgeEmailsCount.textContent = emails.length;
    }
  } catch (err) {
    console.error("Failed loading communications:", err);
  }
}

function renderEmails(emails) {
  if (!elements.emailsContainer) return;
  if (elements.inboxCountTag) elements.inboxCountTag.textContent = `${emails.length} messages`;

  if (!emails || emails.length === 0) {
    elements.emailsContainer.innerHTML = `
      <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
        No emails synced yet. Click <strong>↻ Sync Gmail (MCP)</strong> to pull unread messages.
      </div>
    `;
    return;
  }

  elements.emailsContainer.innerHTML = emails.map(m => {
    const isPhishing = m.phishing_risk === 'HIGH';
    const hasFlags = m.phishing_flags && m.phishing_flags.length > 0;
    const isRecruiter = m.is_recruiter;
    
    let riskTag = `<span class="tag tag-confirmed">Phishing: Low</span>`;
    if (m.phishing_risk === 'HIGH') riskTag = `<span class="tag tag-high-risk">⚠️ Phishing: High Risk</span>`;
    else if (m.phishing_risk === 'MEDIUM') riskTag = `<span class="tag tag-needs-review">⚠️ Phishing: Medium</span>`;

    let intentTag = `<span class="tag tag-inferred">${escapeHtml(m.detected_intent)}</span>`;
    if (m.detected_intent === 'INTERVIEW') intentTag = `<span class="tag tag-confirmed" style="background: rgba(16, 185, 129, 0.2); color: #10b981;">🎯 INTERVIEW</span>`;
    else if (m.detected_intent === 'OFFER') intentTag = `<span class="tag tag-confirmed" style="background: rgba(6, 182, 212, 0.2); color: #06b6d4;">🎉 OFFER</span>`;

    let securityNotice = '';
    if (hasFlags) {
      securityNotice = `
        <div style="background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: var(--radius-sm); padding: 0.5rem 0.75rem; margin-top: 0.5rem; font-size: 0.8rem; color: var(--accent-rose);">
          🛡️ <strong>Security Sanitizer:</strong> ${m.phishing_flags.map(f => escapeHtml(f)).join(' • ')}
        </div>
      `;
    }

    let datesHtml = '';
    if (m.extracted_dates && m.extracted_dates.length > 0) {
      datesHtml = `
        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--accent-cyan);">
          📅 <strong>Dates Detected:</strong> ${m.extracted_dates.map(d => `${escapeHtml(d.text)} (${d.status})`).join(', ')}
        </div>
      `;
    }

    return `
      <div class="task-card" style="margin-bottom: 1rem; border-left: 3px solid ${isPhishing ? 'var(--accent-rose)' : isRecruiter ? 'var(--accent-emerald)' : 'var(--primary)'};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
          <div>
            <div style="font-weight: 600; font-size: 0.95rem; color: var(--text-main);">${escapeHtml(m.subject)}</div>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.15rem;">From: <strong>${escapeHtml(m.sender)}</strong> • ${new Date(m.received_at).toLocaleDateString()}</div>
          </div>
          <div style="display: flex; gap: 0.35rem; flex-wrap: wrap;">
            ${intentTag}
            ${riskTag}
          </div>
        </div>
        
        <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; white-space: pre-wrap; max-height: 120px; overflow-y: auto; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: var(--radius-sm);">${escapeHtml(m.body)}</p>
        
        ${securityNotice}
        ${datesHtml}

        <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
          <div style="font-size: 0.8rem; color: var(--text-sub);">
            ${m.proposed_reply ? '💡 Proposed response drafted' : ''}
          </div>
          ${m.proposed_reply && !isPhishing ? `
            <button class="btn btn-secondary btn-sm" onclick="queueEmailReplyApproval('${m.id}')">
              ✍️ Request Reply Approval
            </button>
          ` : ''}
        </div>
      </div>
    `;
  }).join('');
}

function renderLinkedInInteractions(interactions) {
  if (!elements.liViewActivity) return;
  if (elements.linkedinCountTag) elements.linkedinCountTag.textContent = `${interactions.length} items`;

  if (!interactions || interactions.length === 0) {
    elements.liViewActivity.innerHTML = `
      <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
        No LinkedIn activity synced yet. Click <strong>↻ Sync LinkedIn (MCP)</strong> to pull recruiter conversations.
      </div>
    `;
    return;
  }

  elements.liViewActivity.innerHTML = interactions.map(item => {
    const isConn = item.interaction_type === 'CONNECTION_REQUEST';
    return `
      <div class="task-card" style="margin-bottom: 0.75rem; border-left: 3px solid ${isConn ? 'var(--accent-purple)' : 'var(--accent-cyan)'};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <div>
            <div style="font-weight: 600; font-size: 0.9rem; color: var(--text-main);">${escapeHtml(item.sender_name || 'Anonymous User')}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">${escapeHtml(item.sender_title || '')} ${item.company ? '• ' + escapeHtml(item.company) : ''}</div>
          </div>
          <span class="tag ${isConn ? 'tag-confirmed' : 'tag-inferred'}">${isConn ? 'Invitation' : 'Direct Message'}</span>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-main); margin-top: 0.5rem; line-height: 1.5; background: rgba(0,0,0,0.15); padding: 0.5rem; border-radius: var(--radius-sm);">${escapeHtml(item.content)}</p>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; font-size: 0.75rem; color: var(--text-sub);">
          <span>${item.profile_url ? `<a href="${item.profile_url}" target="_blank" style="color: var(--accent-cyan); text-decoration: none;">View LinkedIn Profile ↗</a>` : ''}</span>
          <span>${new Date(item.created_at).toLocaleDateString()}</span>
        </div>
      </div>
    `;
  }).join('');
}

async function syncGmailMCP() {
  try {
    if (elements.btnSyncGmail) {
      elements.btnSyncGmail.disabled = true;
      elements.btnSyncGmail.textContent = '↻ Syncing...';
    }
    const res = await api.post('/api/communication/mcp/sync-emails', { limit: 10 });
    alert(`Gmail MCP Sync Complete!\n${res.message}`);
    await loadCommunications();
    await loadBriefing();
  } catch (err) {
    alert("Gmail Sync Error: " + err.message);
  } finally {
    if (elements.btnSyncGmail) {
      elements.btnSyncGmail.disabled = false;
      elements.btnSyncGmail.textContent = '↻ Sync Gmail (MCP)';
    }
  }
}

async function syncLinkedInMCP() {
  try {
    if (elements.btnSyncLinkedin) {
      elements.btnSyncLinkedin.disabled = true;
      elements.btnSyncLinkedin.textContent = '↻ Syncing...';
    }
    const res = await api.post('/api/communication/mcp/sync-linkedin', { limit: 10 });
    alert(`LinkedIn MCP Sync Complete!\n${res.message}`);
    await loadCommunications();
    await loadBriefing();
  } catch (err) {
    alert("LinkedIn Sync Error: " + err.message);
  } finally {
    if (elements.btnSyncLinkedin) {
      elements.btnSyncLinkedin.disabled = false;
      elements.btnSyncLinkedin.textContent = '↻ Sync LinkedIn (MCP)';
    }
  }
}

async function queueEmailReplyApproval(emailId) {
  try {
    const res = await api.post(`/api/communication/emails/${emailId}/reply`, {});
    alert(`Approval Request Created!\n${res.message}\nAction queued under Security & Approvals.`);
    await loadApprovals();
    await loadBriefing();
  } catch (err) {
    alert("Failed to queue reply approval: " + err.message);
  }
}

async function generateLinkedInPost() {
  const topic = elements.liPostTopic.value.trim() || "Autonomous Drone Systems & Agentic AI";
  try {
    elements.btnGeneratePost.disabled = true;
    elements.btnGeneratePost.textContent = "Generating...";
    const post = await api.post('/api/communication/linkedin/post-draft', { topic });
    elements.liPostResult.style.display = 'block';
    elements.liPostHook.textContent = post.hook;
    elements.liPostBody.textContent = post.post_body + "\n\n" + post.call_to_action;
    elements.liPostHashtags.textContent = post.hashtags.join(' ');
  } catch (err) {
    alert("Failed generating post: " + err.message);
  } finally {
    elements.btnGeneratePost.disabled = false;
    elements.btnGeneratePost.textContent = "Generate Post Draft";
  }
}

async function generateLinkedInConnectionNote() {
  const recipient_name = elements.liNoteName.value.trim();
  const recipient_role = elements.liNoteRole.value.trim();
  const company = elements.liNoteCompany.value.trim();

  if (!recipient_name || !company) {
    alert("Please provide recipient name and company.");
    return;
  }

  try {
    elements.btnGenerateNote.disabled = true;
    elements.btnGenerateNote.textContent = "Generating...";
    const res = await api.post('/api/communication/linkedin/connection-note', {
      recipient_name,
      recipient_role: recipient_role || "Engineering Lead",
      company
    });
    elements.liNoteResult.style.display = 'block';
    elements.liNoteChars.textContent = `${res.character_count} / 300 characters`;
    elements.liNoteBody.textContent = res.note;
  } catch (err) {
    alert("Failed generating note: " + err.message);
  } finally {
    elements.btnGenerateNote.disabled = false;
    elements.btnGenerateNote.textContent = "Generate Connection Note";
  }
}

// Event Listeners
function setupEventListeners() {
  elements.btnOpenTaskModal.addEventListener('click', () => openTaskModal());
  elements.btnAddTaskPanel.addEventListener('click', () => openTaskModal());
  elements.btnCloseTaskModal.addEventListener('click', closeTaskModal);
  elements.btnCancelTaskModal.addEventListener('click', closeTaskModal);
  elements.btnSaveTask.addEventListener('click', saveTask);

  elements.taskFilterStatus.addEventListener('change', loadTasks);
  elements.taskFilterPriority.addEventListener('change', loadTasks);
  elements.taskFilterCategory.addEventListener('change', loadTasks);

  // Job listeners
  if (elements.btnDiscoverJobs) elements.btnDiscoverJobs.addEventListener('click', discoverLiveJobs);
  if (elements.btnAddJobManual) elements.btnAddJobManual.addEventListener('click', openJobModal);
  if (elements.btnCloseJobModal) elements.btnCloseJobModal.addEventListener('click', closeJobModal);
  if (elements.btnCancelJobModal) elements.btnCancelJobModal.addEventListener('click', closeJobModal);
  if (elements.btnSaveJob) elements.btnSaveJob.addEventListener('click', saveJobManual);
  if (elements.jobFilterVerification) elements.jobFilterVerification.addEventListener('change', loadJobs);
  if (elements.jobFilterRemote) elements.jobFilterRemote.addEventListener('change', loadJobs);

  // Tailored modal listeners
  if (elements.btnCloseTailoredModal) elements.btnCloseTailoredModal.addEventListener('click', () => elements.tailoredModal.classList.remove('active'));
  if (elements.btnCloseTailoredBtn) elements.btnCloseTailoredBtn.addEventListener('click', () => elements.tailoredModal.classList.remove('active'));

  // Communications & MCP listeners
  if (elements.btnSyncGmail) elements.btnSyncGmail.addEventListener('click', syncGmailMCP);
  if (elements.btnSyncLinkedin) elements.btnSyncLinkedin.addEventListener('click', syncLinkedInMCP);
  if (elements.btnConfigMcp) elements.btnConfigMcp.addEventListener('click', () => elements.mcpConfigModal.classList.add('active'));
  if (elements.btnCloseMcpModal) elements.btnCloseMcpModal.addEventListener('click', () => elements.mcpConfigModal.classList.remove('active'));
  if (elements.btnCloseMcpBtn) elements.btnCloseMcpBtn.addEventListener('click', () => elements.mcpConfigModal.classList.remove('active'));
  if (elements.btnGeneratePost) elements.btnGeneratePost.addEventListener('click', generateLinkedInPost);
  if (elements.btnGenerateNote) elements.btnGenerateNote.addEventListener('click', generateLinkedInConnectionNote);

  // Sub-tabs for LinkedIn
  if (elements.btnLiTabActivity) {
    elements.btnLiTabActivity.addEventListener('click', () => {
      elements.liViewActivity.style.display = 'block';
      elements.liViewPost.style.display = 'none';
      elements.liViewNote.style.display = 'none';
      elements.btnLiTabActivity.classList.add('active');
      elements.btnLiTabPost.classList.remove('active');
      elements.btnLiTabNote.classList.remove('active');
    });
  }
  if (elements.btnLiTabPost) {
    elements.btnLiTabPost.addEventListener('click', () => {
      elements.liViewActivity.style.display = 'none';
      elements.liViewPost.style.display = 'block';
      elements.liViewNote.style.display = 'none';
      elements.btnLiTabActivity.classList.remove('active');
      elements.btnLiTabPost.classList.add('active');
      elements.btnLiTabNote.classList.remove('active');
    });
  }
  if (elements.btnLiTabNote) {
    elements.btnLiTabNote.addEventListener('click', () => {
      elements.liViewActivity.style.display = 'none';
      elements.liViewPost.style.display = 'none';
      elements.liViewNote.style.display = 'block';
      elements.btnLiTabActivity.classList.remove('active');
      elements.btnLiTabPost.classList.remove('active');
      elements.btnLiTabNote.classList.add('active');
    });
  }

  elements.btnRefreshBriefing.addEventListener('click', loadBriefing);
  elements.btnTriggerDueReminders.addEventListener('click', triggerDueReminders);
  elements.btnSaveProfile.addEventListener('click', saveProfile);
  elements.btnCreateBackup.addEventListener('click', createBackup);
  elements.modeSelect.addEventListener('change', changeAutonomyMode);
}


function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}

document.addEventListener('DOMContentLoaded', initApp);
