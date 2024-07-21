from storage.db_manager import create_tables, clear_user_table, clear_habit_table, clear_log_table
from app.habit import Habit
from datetime import datetime, timedelta
from app.user import User


def setup_tables():
    """Create tables if they do not exist and clear all tables."""
    create_tables()
    clear_user_table()
    clear_habit_table()
    clear_log_table()


def create_example_user():
    """Create a user with specific details."""
    # Create a user with specific details
    username = 'user123'
    password = 'password123'
    created_at = datetime(2024, 6, 20, 15, 30, 0, 123456)

    # Create the user
    user = User.create(username, password, created_at)
    return user


def create_example_habits(user_id):
    """Create five predefined habits with specific details and log entries for tracking."""
    base_created_at = datetime(2024, 6, 23, 16, 30, 0, 123456)
    habits_data = [
        {"name": "Grocery Shopping", "description": "Weekly food haul", "periodicity": "weekly", "duration": 4,
         "streak": 4},
        {"name": "Attend a Fitness Class", "description": "Aerobic workouts", "periodicity": "weekly", "duration": 4,
         "streak": 4},
        {"name": "Practice a Hobby", "description": "Join a tennis club", "periodicity": "weekly", "duration": 4,
         "streak": 0},
        {"name": "Write in a journal", "description": "Journaling", "periodicity": "daily", "duration": 28,
         "streak": 28},
        {"name": "Read for 20 minutes", "description": "Reading", "periodicity": "daily", "duration": 28, "streak": 0}
    ]

    habits = []
    for i, habit_data in enumerate(habits_data):
        created_at = base_created_at + timedelta(minutes=30 * i)
        habit = Habit.create(user_id, habit_data["name"], habit_data["description"],
                             habit_data["periodicity"], habit_data["duration"], habit_data["streak"], created_at)
        habits.append(habit)

        # Generate log entries for tracking
        create_example_logs(habit, habit_data["periodicity"], habit_data["duration"], created_at)

    return habits


def create_example_logs(habit, periodicity, duration, base_created_at):
    """Create example logs for a habit with specific details."""
    logs = []

    if periodicity == "daily":
        if habit.name == "Write in a journal":
            # All successful for 28 days
            logs = [{
                "habit_id": habit.habit_id,
                "success": 1,
                "note": "Habit completed successfully on time",
                "log_time": base_created_at + timedelta(days=i)
            } for i in range(duration)]
        elif habit.name == "Read for 20 minutes":
            # 14 incomplete, 14 successful
            logs = [{
                "habit_id": habit.habit_id,
                "success": 1,
                "note": "Habit completed successfully on time",
                "log_time": base_created_at + timedelta(days=i)
            } for i in range(14)] + [{
                "habit_id": habit.habit_id,
                "success": 0,
                "note": "Habit marked as incomplete",
                "log_time": base_created_at + timedelta(days=i + 14)
            } for i in range(14)]

    elif periodicity == "weekly":
        if habit.name in ["Grocery Shopping", "Attend a Fitness Class"]:
            # 3 successful, 1 incomplete in each week
            pattern = [
                {"success": 1, "note": "Habit completed successfully on time"},
                {"success": 1, "note": "Habit completed successfully on time"},
                {"success": 1, "note": "Habit completed successfully on time"},
                {"success": 0, "note": "Habit marked as incomplete"}
            ]
            for i in range(duration):
                current_date = base_created_at + timedelta(weeks=i)
                log_entry = pattern[i % 4]
                logs.append({
                    "habit_id": habit.habit_id,
                    "success": log_entry["success"],
                    "note": log_entry["note"],
                    "log_time": current_date
                })

        elif habit.name == "Practice a Hobby":
            # 1 incomplete in each week
            logs = [{
                "habit_id": habit.habit_id,
                "success": 0,
                "note": "Habit marked as incomplete",
                "log_time": base_created_at + timedelta(weeks=i)
            } for i in range(duration)]

    # Add the logs to the habit
    for log_entry in logs:
        habit.add_log_entry(success=log_entry["success"], note=log_entry["note"], log_time=log_entry["log_time"])


if __name__ == "__main__":
    setup_tables()
    user = create_example_user()
    create_example_habits(user.user_id)
