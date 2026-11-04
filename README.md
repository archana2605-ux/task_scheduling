# ⚡ TaskFlow Pro — Smart Task & Workflow Orchestrator

**TaskFlow Pro** is an upgraded, modern task management and scheduling web application built with **Flask**, **SQLAlchemy**, and a responsive **Glassmorphism UI**. It pairs dynamic priority calculation with real-time analytics, kanban workflow boards, integrated Pomodoro focus tracking, and subtask checklists.

---

## ✨ What Makes TaskFlow Pro Unique?

1. **🧠 Dynamic AI-Inspired Urgency Engine**
   - Traditional schedulers sort only by manual priority or hard deadlines. TaskFlow calculates a compound **Urgency Score (0–150+)** in real time by factoring deadline proximity (hourly countdown) with weighted priority levels. Overdue tasks automatically escalate to the top.

2. **📋 Interactive Drag & Drop Kanban Board**
   - Switch effortlessly between the structured Dashboard List and a full **Kanban Board** (`To Do` ➔ `In Progress` ➔ `Done`). Uses asynchronous RESTful APIs to persist state immediately without full page reloads.

3. **🍅 Integrated Pomodoro Focus Engine**
   - Built-in customizable 25/5 Pomodoro focus timer linked directly to each task. Automatically tracks total completed focus blocks per task and logs your productive sessions into the system audit trail.

4. **📈 Visual Productivity Analytics**
   - Interactive Chart.js visual dashboard showing:
     - Real-time completion rates & day streaks
     - Category breakdown bar chart
     - Priority distribution polar area chart
     - 30-day historical completion velocity trend line
     - Average task turnaround duration

5. **🎨 Modern Glassmorphism Design System**
   - Responsive UI featuring frosted glass cards, dynamic ambient floating gradient orbs, custom micro-interactions, smooth CSS animations, and instant **Dark / Light theme toggling** with local storage persistence.

6. **✅ Nested Subtasks & Visual Progress Indicators**
   - Break complex tasks into subtasks with instant checkbox toggling and dynamic completion progress bars.

7. **🔁 Smart Recurring Tasks**
   - Set tasks to repeat automatically (Daily, Weekly, Monthly). When marked complete, the scheduler auto-generates the next occurrence with an advanced deadline and logs the event.

8. **🔗 Instant Task Sharing**
   - Secure UUID-based shareable tokens allowing one-click task sharing links.

9. **📥 CSV Data Export & Audit Logging**
   - One-click CSV export of all tasks with metadata and a timestamped audit log tracking all creations, completions, edits, and deletions.

10. **🏢 Enterprise Business Workflow Ingestion**
    - Built-in business partnership registration portal and administrative review console for approving organizational workflow requests.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask 3.x, Flask-SQLAlchemy 3.x, SQLite
- **Frontend**: Vanilla JavaScript (ES6+), Modern CSS3 (CSS Variables, Backdrop Filter, Flexbox/Grid), HTML5 Jinja2 Templates
- **Libraries**: [Chart.js](https://www.chartjs.org/) for data visualization, [SortableJS](https://sortablejs.github.io/Sortable/) for drag-and-drop
- **Storage**: SQLite relational database (`instance/taskflow.db`) with automatic legacy JSON data migration

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
*(On initial launch, default categories are automatically seeded and any legacy `tasks.json` data is migrated safely into SQLite).*

### 3. Run the Terminal / CLI Mode (Optional)
If you prefer managing tasks directly from your command line:
```bash
python main.py
```

---

## 📂 Project Structure

```text
task_scheduling/
├── app.py                     # Flask application routes, APIs, and business logic
├── models.py                  # SQLAlchemy models (Task, Category, Subtask, ActivityLog, BusinessRequest)
├── scheduler.py               # Core scheduling logic for standalone/CLI usage
├── task.py                    # Task class with urgency scoring
├── main.py                    # Interactive terminal CLI menu
├── requirements.txt           # Python package requirements
├── static/
│   ├── css/
│   │   └── style.css          # Glassmorphism dark/light design system
│   └── js/
│       └── app.js             # Theme toggle, toast alerts, Pomodoro, Kanban, Charts
├── templates/
│   ├── base.html              # Base navigation, theme toggle, and ambient background
│   ├── index.html             # Dashboard with task list, filters, subtasks, creation form
│   ├── kanban.html            # Drag-and-drop Kanban workflow board
│   ├── analytics.html         # Productivity analytics & visual charts
│   ├── logs.html              # Comprehensive activity log audit trail
│   ├── business_form.html     # Enterprise business request intake form
│   ├── admin_requests.html    # Administrative review & approval panel
│   ├── 404.html               # Custom 404 error page
│   └── 500.html               # Custom 500 error page
└── instance/
    └── taskflow.db            # SQLite relational database
```

---

## 🔒 Automated Legacy Migration

TaskFlow Pro automatically detects any existing `tasks.json` or `task_log.json` files on startup, converts the legacy unstructured JSON into strongly typed database records with categories and urgency scores, and archives the old JSON files as `.migrated`.

