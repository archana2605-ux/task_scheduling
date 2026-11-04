from datetime import datetime
from task import Task

class TaskScheduler:
    def __init__(self):
        self.tasks: list[Task] = []

    def add_task(self, name: str, deadline: datetime, priority: int, email: str | None = None) -> Task:
        task_id = len(self.tasks) + 1
        task = Task(task_id, name, deadline, priority, email)
        self.tasks.append(task)
        self.sort_tasks()
        print(f"[+] Added task #{task_id}: '{name}' (Priority {priority})")
        return task

    def sort_tasks(self):
        self.tasks.sort()

    def complete_task(self, task_id: int) -> bool:
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if task:
            task.completed = True
            print(f"[OK] Task #{task_id} '{task.name}' marked as complete!")
            return True
        print(f"[!] Task #{task_id} not found.")
        return False

    def delete_task(self, task_id: int) -> bool:
        initial_len = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
        if len(self.tasks) < initial_len:
            print(f"[-] Task #{task_id} removed.")
            return True
        print(f"[!] Task #{task_id} not found.")
        return False

    def remove_expired_tasks(self) -> int:
        now = datetime.now()
        before_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.deadline >= now or t.completed]
        removed = before_count - len(self.tasks)
        print(f"[i] Removed {removed} expired overdue task(s).")
        return removed

    def show_tasks(self):
        if not self.tasks:
            print("\n--- No tasks scheduled currently ---")
            return

        now = datetime.now()
        print("\n" + "=" * 72)
        print(f"{'ID':<4} | {'Priority':<8} | {'Deadline':<17} | {'Status':<11} | {'Name'}")
        print("-" * 72)
        for t in self.tasks:
            if t.completed:
                status = "[DONE]"
            elif t.deadline < now:
                status = "[OVERDUE]"
            else:
                status = "[PENDING]"

            print(f"{t.task_id:<4} | P{t.priority:<7} | {t.deadline.strftime('%Y-%m-%d %H:%M'):<17} | {status:<11} | {t.name}")
        print("=" * 72 + "\n")

    def get_filtered_tasks(self, search: str = '', priority_filter: str = 'all', status_filter: str = 'all'):
        filtered_tasks = self.tasks
        if search:
            filtered_tasks = [task for task in filtered_tasks if search.lower() in task.name.lower()]

        if priority_filter != 'all':
            filtered_tasks = [task for task in filtered_tasks if str(task.priority) == priority_filter]

        if status_filter != 'all':
            if status_filter == 'completed':
                filtered_tasks = [task for task in filtered_tasks if task.completed]
            elif status_filter == 'pending':
                filtered_tasks = [task for task in filtered_tasks if not task.completed]
            elif status_filter == 'overdue':
                filtered_tasks = [task for task in filtered_tasks if task.deadline < datetime.now() and not task.completed]

        return filtered_tasks

    def get_all_tasks(self):
        return self.tasks
