from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#6C63FF')
    icon = db.Column(db.String(10), default='📋')
    tasks = db.relationship('Task', backref='category', lazy=True)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    deadline = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.Integer, default=3)  # 1=Critical, 2=High, 3=Medium, 4=Low, 5=Optional
    status = db.Column(db.String(20), default='todo')  # todo, in_progress, done
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    email = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=datetime.now)
    completed_at = db.Column(db.DateTime, nullable=True)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence = db.Column(db.String(20), default='')  # daily, weekly, monthly
    pomodoro_count = db.Column(db.Integer, default=0)
    share_token = db.Column(db.String(36), default=lambda: str(uuid.uuid4()))
    notes = db.Column(db.Text, default='')
    subtasks = db.relationship('Subtask', backref='task', lazy=True, cascade='all, delete-orphan')

    @property
    def completed(self):
        return self.status == 'done'

    @property
    def urgency_score(self):
        """AI-inspired smart priority: combines deadline proximity with manual priority weight."""
        if self.status == 'done':
            return 0
        now = datetime.now()
        if self.deadline < now:
            return 100 + (6 - self.priority) * 10  # overdue items get highest urgency
        hours_left = (self.deadline - now).total_seconds() / 3600
        if hours_left <= 1:
            base = 90
        elif hours_left <= 6:
            base = 70
        elif hours_left <= 24:
            base = 50
        elif hours_left <= 72:
            base = 30
        else:
            base = 10
        return base + (6 - self.priority) * 5  # lower priority number = higher weight

    @property
    def subtask_progress(self):
        if not self.subtasks:
            return 0
        done = sum(1 for s in self.subtasks if s.completed)
        return int((done / len(self.subtasks)) * 100)

    @property
    def urgency_label(self):
        score = self.urgency_score
        if score >= 90:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 30:
            return 'medium'
        else:
            return 'low'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M'),
            'priority': self.priority,
            'status': self.status,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'Uncategorized',
            'category_color': self.category.color if self.category else '#6C63FF',
            'category_icon': self.category.icon if self.category else '📋',
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M') if self.completed_at else None,
            'urgency_score': self.urgency_score,
            'urgency_label': self.urgency_label,
            'is_recurring': self.is_recurring,
            'recurrence': self.recurrence,
            'pomodoro_count': self.pomodoro_count,
            'share_token': self.share_token,
            'notes': self.notes,
            'subtasks': [s.to_dict() for s in self.subtasks],
            'subtask_progress': self.subtask_progress
        }

class Subtask(db.Model):
    __tablename__ = 'subtasks'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {'id': self.id, 'task_id': self.task_id, 'name': self.name, 'completed': self.completed}

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=True)
    task_name = db.Column(db.String(200))
    action = db.Column(db.String(50))
    details = db.Column(db.Text, default='')
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id, 'task_id': self.task_id, 'task_name': self.task_name,
            'action': self.action, 'details': self.details,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M') if self.timestamp else ''
        }

class BusinessRequest(db.Model):
    __tablename__ = 'business_requests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_email = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.now)
