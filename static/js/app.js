/* ============================================
   TaskFlow Pro — Application JavaScript
   ============================================ */

// === 1. THEME MANAGER ===
const ThemeManager = {
    init() {
        const saved = localStorage.getItem('taskflow-theme') || 'dark';
        this.setTheme(saved);
        document.getElementById('theme-toggle')?.addEventListener('click', () => this.toggle());
    },
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('taskflow-theme', theme);
        const icon = document.querySelector('.theme-icon');
        if (icon) icon.textContent = theme === 'dark' ? '🌙' : '☀️';
    },
    toggle() {
        const current = document.documentElement.getAttribute('data-theme');
        this.setTheme(current === 'dark' ? 'light' : 'dark');
    }
};

// === 2. TOAST SYSTEM ===
function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icons = { success: '✅', error: '❌', danger: '❌', info: 'ℹ️', warning: '⚠️' };
    toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// === 3. POMODORO TIMER ===
const PomodoroTimer = {
    duration: 25 * 60,
    breakDuration: 5 * 60,
    remaining: 25 * 60,
    isRunning: false,
    isBreak: false,
    interval: null,
    taskId: null,
    taskName: '',
    sessions: 0,

    open(taskId, taskName, currentSessions) {
        this.taskId = taskId;
        this.taskName = taskName;
        this.sessions = currentSessions || 0;
        this.remaining = this.duration;
        this.isRunning = false;
        this.isBreak = false;
        this.render();
    },

    render() {
        let overlay = document.getElementById('pomodoro-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'pomodoro-overlay';
            overlay.className = 'pomodoro-overlay';
            document.body.appendChild(overlay);
        }
        const mins = Math.floor(this.remaining / 60).toString().padStart(2, '0');
        const secs = (this.remaining % 60).toString().padStart(2, '0');
        overlay.innerHTML = `
            <div class="pomodoro-modal glass-card">
                <h2 style="margin-bottom:8px;font-size:20px;">${this.isBreak ? '☕ Break Time' : '🍅 Focus Mode'}</h2>
                <p class="pomodoro-label">${this.taskName}</p>
                <div class="pomodoro-display">${mins}:${secs}</div>
                <div class="pomodoro-controls">
                    <button class="btn-primary" onclick="PomodoroTimer.${this.isRunning ? 'pause' : 'start'}()">
                        ${this.isRunning ? '⏸ Pause' : '▶ Start'}
                    </button>
                    <button class="btn-secondary" onclick="PomodoroTimer.reset()">🔄 Reset</button>
                    <button class="btn-danger" onclick="PomodoroTimer.close()">✕ Close</button>
                </div>
                <div class="pomodoro-sessions">Sessions completed: ${this.sessions} 🍅</div>
            </div>
        `;
        overlay.style.display = 'flex';
    },

    start() {
        this.isRunning = true;
        this.render();
        this.interval = setInterval(() => {
            this.remaining--;
            if (this.remaining <= 0) {
                clearInterval(this.interval);
                this.isRunning = false;
                if (!this.isBreak) {
                    this.sessions++;
                    fetch(`/task/${this.taskId}/pomodoro`, { method: 'POST' });
                    showToast('🍅 Pomodoro complete! Take a break.', 'success');
                    this.isBreak = true;
                    this.remaining = this.breakDuration;
                } else {
                    showToast('Break over! Ready for another session?', 'info');
                    this.isBreak = false;
                    this.remaining = this.duration;
                }
            }
            this.render();
        }, 1000);
    },

    pause() {
        this.isRunning = false;
        clearInterval(this.interval);
        this.render();
    },

    reset() {
        this.pause();
        this.remaining = this.isBreak ? this.breakDuration : this.duration;
        this.render();
    },

    close() {
        this.pause();
        const overlay = document.getElementById('pomodoro-overlay');
        if (overlay) overlay.style.display = 'none';
    }
};

// === 4. KANBAN DRAG & DROP ===
function initKanban() {
    if (typeof Sortable === 'undefined') return;

    document.querySelectorAll('.kanban-tasks').forEach(column => {
        new Sortable(column, {
            group: 'kanban',
            animation: 200,
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
            onEnd: function(evt) {
                const taskId = evt.item.dataset.taskId;
                const newStatus = evt.to.dataset.status;
                fetch(`/task/${taskId}/status`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showToast(`Task moved to ${newStatus.replace('_', ' ')}`, 'success');
                        updateKanbanCounts();
                    }
                })
                .catch(() => showToast('Failed to update task', 'error'));
            }
        });
    });
}

function updateKanbanCounts() {
    document.querySelectorAll('.kanban-column').forEach(col => {
        const count = col.querySelectorAll('.kanban-task-card').length;
        const badge = col.querySelector('.kanban-count');
        if (badge) badge.textContent = count;
    });
}

// === 5. ANALYTICS CHARTS ===
function initAnalytics() {
    if (typeof Chart === 'undefined') return;

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    Chart.defaults.color = isDark ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.6)';
    Chart.defaults.borderColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

    fetch('/api/analytics')
        .then(r => r.json())
        .then(data => {
            renderCompletionChart(data);
            renderCategoryChart(data);
            renderPriorityChart(data);
            renderDailyChart(data);
        })
        .catch(err => console.error('Analytics error:', err));
}

function renderCompletionChart(data) {
    const ctx = document.getElementById('completion-chart');
    if (!ctx) return;
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'In Progress', 'Pending', 'Overdue'],
            datasets: [{
                data: [
                    data.completed_tasks,
                    data.in_progress_tasks,
                    data.pending_tasks - data.overdue_tasks - data.in_progress_tasks,
                    data.overdue_tasks
                ],
                backgroundColor: ['#00C853', '#6C63FF', '#00D2FF', '#FF1744'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { padding: 16, usePointStyle: true } }
            },
            cutout: '65%'
        }
    });
}

function renderCategoryChart(data) {
    const ctx = document.getElementById('category-chart');
    if (!ctx || !data.category_breakdown) return;
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.category_breakdown.map(c => c.icon + ' ' + c.name),
            datasets: [
                {
                    label: 'Total',
                    data: data.category_breakdown.map(c => c.total),
                    backgroundColor: data.category_breakdown.map(c => c.color + '99')
                },
                {
                    label: 'Completed',
                    data: data.category_breakdown.map(c => c.completed),
                    backgroundColor: data.category_breakdown.map(c => c.color)
                }
            ]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom' } },
            scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
        }
    });
}

function renderPriorityChart(data) {
    const ctx = document.getElementById('priority-chart');
    if (!ctx || !data.priority_breakdown) return;
    const labels_map = {1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low', 5: 'Optional'};
    const colors = {1: '#FF1744', 2: '#FF6B6B', 3: '#6C63FF', 4: '#00D2FF', 5: '#9E9E9E'};
    new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: data.priority_breakdown.map(p => labels_map[p.priority] || 'P'+p.priority),
            datasets: [{
                data: data.priority_breakdown.map(p => p.total),
                backgroundColor: data.priority_breakdown.map(p => (colors[p.priority] || '#6C63FF') + '99')
            }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    });
}

function renderDailyChart(data) {
    const ctx = document.getElementById('daily-chart');
    if (!ctx || !data.daily_completions) return;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.daily_completions.map(d => d.date.slice(5)),
            datasets: [{
                label: 'Tasks Completed',
                data: data.daily_completions.map(d => d.count),
                borderColor: '#6C63FF',
                backgroundColor: 'rgba(108, 99, 255, 0.1)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#6C63FF',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
        }
    });
}

// === 6. SUBTASK MANAGEMENT ===
function addSubtask(taskId) {
    const input = document.getElementById(`subtask-input-${taskId}`);
    if (!input || !input.value.trim()) return;

    fetch(`/task/${taskId}/subtask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: input.value.trim() })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            const list = document.getElementById(`subtask-list-${taskId}`);
            if (list) {
                const li = document.createElement('li');
                li.className = 'subtask-item';
                li.id = `subtask-${data.subtask.id}`;
                li.innerHTML = `
                    <input type="checkbox" class="subtask-checkbox" onchange="toggleSubtask(${data.subtask.id})">
                    <span>${data.subtask.name}</span>
                `;
                list.appendChild(li);
            }
            input.value = '';
            updateSubtaskProgress(taskId);
            showToast('Subtask added', 'success');
        }
    });
}

function toggleSubtask(subtaskId) {
    fetch(`/subtask/${subtaskId}/toggle`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                const item = document.getElementById(`subtask-${subtaskId}`);
                if (item) {
                    item.classList.toggle('done', data.subtask.completed);
                    item.querySelector('.subtask-checkbox').checked = data.subtask.completed;
                }
                updateSubtaskProgress(data.subtask.task_id);
            }
        });
}

function updateSubtaskProgress(taskId) {
    const list = document.getElementById(`subtask-list-${taskId}`);
    const bar = document.getElementById(`progress-${taskId}`);
    if (!list || !bar) return;
    const items = list.querySelectorAll('.subtask-item');
    const done = list.querySelectorAll('.subtask-item.done').length;
    const pct = items.length > 0 ? Math.round((done / items.length) * 100) : 0;
    bar.style.width = pct + '%';
}

// === 7. TASK EDIT MODAL ===
function openEditModal(taskId) {
    fetch(`/api/tasks?id=${taskId}`)
        .then(r => r.json())
        .then(task => {
            const newName = prompt('Edit task name:', task.name);
            if (newName && newName !== task.name) {
                fetch(`/task/${taskId}/edit`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: newName })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showToast('Task updated', 'success');
                        location.reload();
                    }
                });
            }
        });
}

// === 8. CONFIRM DELETE ===
function confirmDelete(taskId, taskName) {
    if (confirm(`Delete "${taskName}"? This cannot be undone.`)) {
        document.getElementById(`delete-form-${taskId}`).submit();
    }
}

// === 9. EXPORT ===
function exportCSV() {
    window.location.href = '/export/csv';
    showToast('Downloading tasks...', 'info');
}

// === 10. COPY SHARE LINK ===
function copyShareLink(token) {
    const url = `${window.location.origin}/shared/${token}`;
    navigator.clipboard.writeText(url).then(() => {
        showToast('Share link copied!', 'success');
    }).catch(() => {
        prompt('Copy this link:', url);
    });
}

// === 11. DOM CONTENT LOADED INIT ===
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    initKanban();
    if (document.getElementById('analytics-page')) {
        initAnalytics();
    }

    // Animate cards on load
    document.querySelectorAll('.task-card, .glass-card').forEach((card, i) => {
        card.style.animationDelay = `${i * 0.05}s`;
    });

    // Toggle recurring fields visibility
    const recurringCheckbox = document.getElementById('is_recurring');
    const recurrenceGroup = document.getElementById('recurrence-group');
    if (recurringCheckbox && recurrenceGroup) {
        function toggleRecurrence() {
            recurrenceGroup.style.display = recurringCheckbox.checked ? 'flex' : 'none';
        }
        recurringCheckbox.addEventListener('change', toggleRecurrence);
        toggleRecurrence();
    }
});
