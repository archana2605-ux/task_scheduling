from scheduler import TaskScheduler
from datetime import datetime

def main():
    scheduler = TaskScheduler()

    while True:
        print("\n=== TaskFlow CLI Scheduler ===")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Complete Task")
        print("4. Remove Expired Tasks")
        print("5. Delete Task")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == '1':
            name = input("Enter task name: ").strip()
            deadline_input = input("Enter deadline (YYYY-MM-DD HH:MM): ").strip()
            try:
                deadline = datetime.strptime(deadline_input, "%Y-%m-%d %H:%M")
                priority = int(input("Enter priority (1=Critical, 2=High, 3=Med, 4=Low, 5=Opt): "))
                scheduler.add_task(name, deadline, priority)
            except ValueError as e:
                print(f"[!] Invalid input: {e}")

        elif choice == '2':
            scheduler.show_tasks()

        elif choice == '3':
            try:
                task_id = int(input("Enter task ID to mark as complete: "))
                scheduler.complete_task(task_id)
            except ValueError:
                print("[!] Please enter a valid numerical ID.")

        elif choice == '4':
            scheduler.remove_expired_tasks()

        elif choice == '5':
            try:
                task_id = int(input("Enter task ID to delete: "))
                scheduler.delete_task(task_id)
            except ValueError:
                print("[!] Please enter a valid numerical ID.")

        elif choice == '6':
            print("Exiting Task Scheduler. Goodbye!")
            break

        else:
            print("[!] Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    main()
