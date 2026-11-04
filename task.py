from datetime import datetime

class Task:
    """Core Task entity for task scheduling and prioritization."""

    def __init__(self, task_id: int, name: str, deadline: datetime, priority: int, email: str | None = None):
        self.task_id = task_id
        self.name = name
        self.deadline = deadline
        self.priority = priority  # 1 (Critical) to 5 (Optional)
        self.completed = False
        self.email = email
        self.created_at = datetime.now()

    def __lt__(self, other):
        # Earliest deadline first
        if self.deadline != other.deadline:
            return self.deadline < other.deadline
        # Higher priority (lower number) first if deadline ties
        return self.priority < other.priority

    @property
    def is_overdue(self) -> bool:
        return datetime.now() > self.deadline and not self.completed

    @property
    def urgency_score(self) -> int:
        """Smart dynamic urgency rating combining deadline countdown and priority weight."""
        if self.completed:
            return 0
        now = datetime.now()
        if self.deadline < now:
            return 100 + (6 - self.priority) * 10
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
        return base + (6 - self.priority) * 5

    def __repr__(self) -> str:
        return f"<Task #{self.task_id} '{self.name}' [P{self.priority}] Due: {self.deadline.strftime('%Y-%m-%d %H:%M')}>"
