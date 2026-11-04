import os
import json
import csv
import io
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, Response
)
from models import db, Category, Task, Subtask, ActivityLog, BusinessRequest

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def seed_categories():
    """Create default categories if the table is empty."""
    if Category.query.count() == 0:
        defaults = [
            Category(name='Work', color='#6C63FF', icon='💼'),
            Category(name='Study', color='#00D2FF', icon='📚'),
            Category(name='Personal', color='#FF6B6B', icon='🏠'),
            Category(name='Health', color='#00C853', icon='💪'),
            Category(name='Finance', color='#FFD600', icon='💰'),
        ]
        db.session.add_all(defaults)
        db.session.commit()


def log_action(task_id, task_name, action, details=''):
    entry = ActivityLog(
        task_id=task_id,
        task_name=task_name,
        action=action,
        details=details,
    )
    db.session.add(entry)
    db.session.commit()


def migrate_legacy_data():
    """Migrate tasks.json and task_log.json into the database if they exist."""
    tasks_file = os.path.join(os.path.dirname(__file__), 'tasks.json')
    if os.path.exists(tasks_file):
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                legacy_tasks = json.load(f)
            for t in legacy_tasks:
                deadline_str = t.get('deadline', '')
                try:
                    deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    try:
                        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
                    except (ValueError, TypeError):
                        deadline = datetime.now()

                task = Task(
                    name=t.get('name', 'Untitled'),
                    description=t.get('description', ''),
                    deadline=deadline,
                    priority=int(t.get('priority', 3)),
                    status=t.get('status', 'todo'),
                    email=t.get('email', ''),
                    is_recurring=t.get('is_recurring', False),
                    recurrence=t.get('recurrence', ''),
                    notes=t.get('notes', ''),
                )
                # Try to match category by name
                cat_name = t.get('category', '')
                if cat_name:
                    cat = Category.query.filter_by(name=cat_name).first()
                    if cat:
                        task.category_id = cat.id
                db.session.add(task)
            db.session.commit()
            os.rename(tasks_file, tasks_file + '.migrated')
        except Exception as e:
            print(f'[migrate] Error migrating tasks.json: {e}')

    log_file = os.path.join(os.path.dirname(__file__), 'task_log.json')
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                legacy_logs = json.load(f)
            for entry in legacy_logs:
                ts_str = entry.get('timestamp', '')
                try:
                    ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    try:
                        ts = datetime.strptime(ts_str, '%Y-%m-%dT%H:%M:%S')
                    except (ValueError, TypeError):
                        ts = datetime.now()
                log = ActivityLog(
                    task_id=entry.get('task_id'),
                    task_name=entry.get('task_name', ''),
                    action=entry.get('action', ''),
                    details=entry.get('details', ''),
                    timestamp=ts,
                )
                db.session.add(log)
            db.session.commit()
            os.rename(log_file, log_file + '.migrated')
        except Exception as e:
            print(f'[migrate] Error migrating task_log.json: {e}')


# ---------------------------------------------------------------------------
# Routes — Dashboard
# ---------------------------------------------------------------------------

@app.route('/', methods=['GET'])
def dashboard():
    search = request.args.get('search', '').strip()
    priority_val = request.args.get('priority', 'all')
    status_val = request.args.get('status', 'all')
    category_val = request.args.get('category', 'all')
    sort_val = request.args.get('sort', 'deadline')

    query = Task.query

    # Filters
    if search:
        query = query.filter(Task.name.ilike(f'%{search}%'))
    if priority_val != 'all':
        query = query.filter(Task.priority == int(priority_val))
    if status_val == 'overdue':
        query = query.filter(Task.deadline < datetime.now(), Task.status != 'done')
    elif status_val != 'all':
        query = query.filter(Task.status == status_val)
    if category_val != 'all':
        query = query.filter(Task.category_id == int(category_val))

    tasks = query.all()

    # Sort
    if sort_val == 'priority':
        tasks.sort(key=lambda t: t.priority)
    elif sort_val == 'urgency':
        tasks.sort(key=lambda t: t.urgency_score, reverse=True)
    elif sort_val == 'created':
        tasks.sort(key=lambda t: t.created_at or datetime.min, reverse=True)
    else:  # deadline (default)
        tasks.sort(key=lambda t: t.deadline)

    # Stats
    all_tasks = Task.query.all()
    now = datetime.now()
    stats = {
        'total': len(all_tasks),
        'pending': sum(1 for t in all_tasks if t.status != 'done'),
        'completed': sum(1 for t in all_tasks if t.status == 'done'),
        'overdue': sum(1 for t in all_tasks if t.deadline < now and t.status != 'done'),
        'in_progress': sum(1 for t in all_tasks if t.status == 'in_progress'),
    }

    categories = Category.query.all()

    return render_template(
        'index.html',
        tasks=tasks,
        categories=categories,
        stats=stats,
        now=now,
        active_page='dashboard',
        search_val=search,
        priority_val=priority_val,
        status_val=status_val,
        category_val=category_val,
        sort_val=sort_val,
    )


@app.route('/', methods=['POST'])
def add_task():
    name = request.form.get('name', '').strip()
    deadline_str = request.form.get('deadline', '')
    priority = int(request.form.get('priority', 3))
    category_id = request.form.get('category_id') or None
    email = request.form.get('email', '').strip()
    description = request.form.get('description', '').strip()
    is_recurring = bool(request.form.get('is_recurring'))
    recurrence = request.form.get('recurrence', '')

    if not name or not deadline_str:
        flash('Task name and deadline are required.', 'error')
        return redirect(url_for('dashboard'))

    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
        except ValueError:
            flash('Invalid deadline format.', 'error')
            return redirect(url_for('dashboard'))

    if category_id is not None:
        category_id = int(category_id) if category_id else None

    task = Task(
        name=name,
        deadline=deadline,
        priority=priority,
        category_id=category_id,
        email=email,
        description=description,
        is_recurring=is_recurring,
        recurrence=recurrence,
    )
    db.session.add(task)
    db.session.commit()

    log_action(task.id, task.name, 'added', f'Priority {priority}')
    flash(f'Task "{name}" added successfully!', 'success')
    return redirect(url_for('dashboard'))


# ---------------------------------------------------------------------------
# Routes — Kanban
# ---------------------------------------------------------------------------

@app.route('/kanban')
def kanban():
    todo_tasks = Task.query.filter_by(status='todo').all()
    progress_tasks = Task.query.filter_by(status='in_progress').all()
    done_tasks = Task.query.filter_by(status='done').all()

    todo_tasks.sort(key=lambda t: t.urgency_score, reverse=True)
    progress_tasks.sort(key=lambda t: t.urgency_score, reverse=True)
    done_tasks.sort(key=lambda t: t.urgency_score, reverse=True)

    categories = Category.query.all()

    return render_template(
        'kanban.html',
        todo_tasks=todo_tasks,
        progress_tasks=progress_tasks,
        done_tasks=done_tasks,
        categories=categories,
        active_page='kanban',
    )


# ---------------------------------------------------------------------------
# Routes — Task Actions
# ---------------------------------------------------------------------------

@app.route('/task/<int:id>/status', methods=['POST'])
def update_task_status(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    new_status = data.get('status', task.status)
    old_status = task.status

    task.status = new_status

    if new_status == 'done' and old_status != 'done':
        task.completed_at = datetime.now()
    elif new_status != 'done' and old_status == 'done':
        task.completed_at = None

    db.session.commit()
    log_action(task.id, task.name, 'status_changed', f'{old_status} → {new_status}')
    return jsonify({'success': True, 'task': task.to_dict()})


@app.route('/task/<int:id>/complete', methods=['POST'])
def complete_task(id):
    task = Task.query.get_or_404(id)
    task.status = 'done'
    task.completed_at = datetime.now()
    db.session.commit()

    # Handle recurring tasks
    if task.is_recurring and task.recurrence:
        if task.recurrence == 'daily':
            new_deadline = task.deadline + timedelta(days=1)
        elif task.recurrence == 'weekly':
            new_deadline = task.deadline + timedelta(days=7)
        elif task.recurrence == 'monthly':
            new_deadline = task.deadline + timedelta(days=30)
        else:
            new_deadline = task.deadline + timedelta(days=1)

        new_task = Task(
            name=task.name,
            description=task.description,
            deadline=new_deadline,
            priority=task.priority,
            category_id=task.category_id,
            email=task.email,
            is_recurring=True,
            recurrence=task.recurrence,
            notes=task.notes,
        )
        db.session.add(new_task)
        db.session.commit()
        log_action(new_task.id, new_task.name, 'recurring_created',
                   f'Next occurrence: {new_deadline.strftime("%Y-%m-%d %H:%M")}')

    log_action(task.id, task.name, 'completed')
    flash(f'Task "{task.name}" marked as complete!', 'success')
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/task/<int:id>/delete', methods=['POST'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    task_name = task.name
    log_action(task.id, task_name, 'deleted')
    db.session.delete(task)
    db.session.commit()
    flash(f'Task "{task_name}" deleted.', 'success')
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/task/<int:id>/edit', methods=['POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()

    if 'name' in data:
        task.name = data['name']
    if 'description' in data:
        task.description = data['description']
    if 'deadline' in data:
        try:
            task.deadline = datetime.strptime(data['deadline'], '%Y-%m-%dT%H:%M')
        except ValueError:
            try:
                task.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M')
            except ValueError:
                pass
    if 'priority' in data:
        task.priority = int(data['priority'])
    if 'status' in data:
        task.status = data['status']
    if 'category_id' in data:
        task.category_id = data['category_id'] if data['category_id'] else None
    if 'email' in data:
        task.email = data['email']
    if 'is_recurring' in data:
        task.is_recurring = bool(data['is_recurring'])
    if 'recurrence' in data:
        task.recurrence = data['recurrence']
    if 'notes' in data:
        task.notes = data['notes']

    db.session.commit()
    log_action(task.id, task.name, 'edited')
    return jsonify({'success': True, 'task': task.to_dict()})


# ---------------------------------------------------------------------------
# Routes — Subtasks
# ---------------------------------------------------------------------------

@app.route('/task/<int:id>/subtask', methods=['POST'])
def add_subtask(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Subtask name required'}), 400

    subtask = Subtask(task_id=task.id, name=name)
    db.session.add(subtask)
    db.session.commit()
    return jsonify({'success': True, 'subtask': subtask.to_dict()})


@app.route('/subtask/<int:id>/toggle', methods=['POST'])
def toggle_subtask(id):
    subtask = Subtask.query.get_or_404(id)
    subtask.completed = not subtask.completed
    db.session.commit()
    return jsonify({'success': True, 'subtask': subtask.to_dict()})


# ---------------------------------------------------------------------------
# Routes — Pomodoro
# ---------------------------------------------------------------------------

@app.route('/task/<int:id>/pomodoro', methods=['POST'])
def log_pomodoro(id):
    task = Task.query.get_or_404(id)
    task.pomodoro_count += 1
    db.session.commit()
    log_action(task.id, task.name, 'pomodoro', f'Session #{task.pomodoro_count}')
    return jsonify({'success': True, 'pomodoro_count': task.pomodoro_count})


# ---------------------------------------------------------------------------
# Routes — Analytics
# ---------------------------------------------------------------------------

@app.route('/analytics')
def analytics():
    return render_template('analytics.html', active_page='analytics')


@app.route('/api/analytics')
def api_analytics():
    all_tasks = Task.query.all()
    now = datetime.now()

    total = len(all_tasks)
    completed = [t for t in all_tasks if t.status == 'done']
    pending = [t for t in all_tasks if t.status != 'done']
    overdue = [t for t in all_tasks if t.deadline < now and t.status != 'done']
    in_progress = [t for t in all_tasks if t.status == 'in_progress']

    completion_rate = (len(completed) / total * 100) if total > 0 else 0

    # Category breakdown
    categories = Category.query.all()
    category_breakdown = []
    for cat in categories:
        cat_tasks = [t for t in all_tasks if t.category_id == cat.id]
        category_breakdown.append({
            'name': cat.name,
            'color': cat.color,
            'icon': cat.icon,
            'total': len(cat_tasks),
            'completed': sum(1 for t in cat_tasks if t.status == 'done'),
        })

    # Priority breakdown
    priority_labels = {1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low', 5: 'Optional'}
    priority_breakdown = []
    for p in range(1, 6):
        p_tasks = [t for t in all_tasks if t.priority == p]
        priority_breakdown.append({
            'priority': p,
            'label': priority_labels[p],
            'total': len(p_tasks),
            'completed': sum(1 for t in p_tasks if t.status == 'done'),
        })

    # Daily completions (last 30 days)
    daily_completions = []
    for i in range(29, -1, -1):
        day = (now - timedelta(days=i)).date()
        count = sum(
            1 for t in completed
            if t.completed_at and t.completed_at.date() == day
        )
        daily_completions.append({'date': day.strftime('%Y-%m-%d'), 'count': count})

    # Streak — consecutive days with at least one completion (ending today or yesterday)
    streak = 0
    check_day = now.date()
    while True:
        day_completions = sum(
            1 for t in completed
            if t.completed_at and t.completed_at.date() == check_day
        )
        if day_completions > 0:
            streak += 1
            check_day -= timedelta(days=1)
        else:
            break

    # Average completion time
    completion_times = []
    for t in completed:
        if t.completed_at and t.created_at:
            hours = (t.completed_at - t.created_at).total_seconds() / 3600
            completion_times.append(hours)
    avg_completion_time_hours = (
        round(sum(completion_times) / len(completion_times), 1)
        if completion_times else 0
    )

    # Pomodoro total
    pomodoro_total = sum(t.pomodoro_count for t in all_tasks)

    # Urgency distribution (non-done tasks only)
    urgency_distribution = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for t in pending:
        label = t.urgency_label
        if label in urgency_distribution:
            urgency_distribution[label] += 1

    return jsonify({
        'completion_rate': round(completion_rate, 1),
        'total_tasks': total,
        'completed_tasks': len(completed),
        'pending_tasks': len(pending),
        'overdue_tasks': len(overdue),
        'in_progress_tasks': len(in_progress),
        'category_breakdown': category_breakdown,
        'priority_breakdown': priority_breakdown,
        'daily_completions': daily_completions,
        'streak': streak,
        'avg_completion_time_hours': avg_completion_time_hours,
        'pomodoro_total': pomodoro_total,
        'urgency_distribution': urgency_distribution,
    })


# ---------------------------------------------------------------------------
# Routes — Export
# ---------------------------------------------------------------------------

@app.route('/export/csv')
def export_csv():
    tasks = Task.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'id', 'name', 'deadline', 'priority', 'status', 'category',
        'email', 'created_at', 'completed_at', 'urgency_score', 'pomodoro_count',
    ])
    for t in tasks:
        writer.writerow([
            t.id,
            t.name,
            t.deadline.strftime('%Y-%m-%d %H:%M'),
            t.priority,
            t.status,
            t.category.name if t.category else 'Uncategorized',
            t.email,
            t.created_at.strftime('%Y-%m-%d %H:%M') if t.created_at else '',
            t.completed_at.strftime('%Y-%m-%d %H:%M') if t.completed_at else '',
            t.urgency_score,
            t.pomodoro_count,
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=taskflow_export.csv'},
    )


# ---------------------------------------------------------------------------
# Routes — Activity Logs
# ---------------------------------------------------------------------------

@app.route('/logs')
def logs():
    all_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()
    return render_template('logs.html', logs=all_logs, active_page='logs')


@app.route('/api/logs')
def api_logs():
    action_filter = request.args.get('action', '').strip()
    search = request.args.get('search', '').strip()

    query = ActivityLog.query

    if action_filter:
        query = query.filter(ActivityLog.action == action_filter)
    if search:
        query = query.filter(ActivityLog.task_name.ilike(f'%{search}%'))

    logs = query.order_by(ActivityLog.timestamp.desc()).all()
    return jsonify([l.to_dict() for l in logs])


# ---------------------------------------------------------------------------
# Routes — Shared Task
# ---------------------------------------------------------------------------

@app.route('/shared/<token>')
def shared_task(token):
    task = Task.query.filter_by(share_token=token).first_or_404()
    return jsonify(task.to_dict())


# ---------------------------------------------------------------------------
# Routes — Business Form
# ---------------------------------------------------------------------------

@app.route('/business', methods=['GET'])
def business_form():
    return render_template('business_form.html', active_page='business')


@app.route('/business', methods=['POST'])
def business_submit():
    name = request.form.get('name', '').strip()
    contact_email = request.form.get('contact_email', '').strip()
    description = request.form.get('description', '').strip()

    if not name or not contact_email:
        flash('Name and email are required.', 'error')
        return redirect(url_for('business_form'))

    req = BusinessRequest(
        name=name,
        contact_email=contact_email,
        description=description,
    )
    db.session.add(req)
    db.session.commit()
    flash('Your request has been submitted!', 'success')
    return redirect(url_for('business_form'))


# ---------------------------------------------------------------------------
# Routes — Admin
# ---------------------------------------------------------------------------

@app.route('/admin/requests', methods=['GET'])
def admin_requests():
    pending = BusinessRequest.query.filter_by(status='pending').all()
    return render_template('admin_requests.html', pending=pending, active_page='admin')


@app.route('/admin/requests', methods=['POST'])
def admin_handle_request():
    request_id = request.form.get('request_id')
    action = request.form.get('action')  # 'approve' or 'reject'

    br = BusinessRequest.query.get_or_404(int(request_id))
    if action == 'approve':
        br.status = 'approved'
        flash(f'Request from "{br.name}" approved.', 'success')
    elif action == 'reject':
        br.status = 'rejected'
        flash(f'Request from "{br.name}" rejected.', 'success')
    db.session.commit()
    return redirect(url_for('admin_requests'))


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html', active_page=None), 404


@app.errorhandler(500)
def server_error(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html', active_page=None), 500


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_categories()
        migrate_legacy_data()
    app.run(debug=True)
