import logging
from storage.db_manager import (
    get_habits_by_user, get_logs_by_habit, count_success_by_habit, count_unsuccessful_by_habit,
    count_success, count_failure, get_habit_by_id
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_active_habits(user_id):
    habits_data = get_habits_by_user(user_id)
    active_habits = [habit for habit in habits_data if habit['active'] == 1]

    if not active_habits:
        print(f"No active habits found for user {user_id}.")

    return active_habits


def get_habits_by_periodicity(user_id, periodicity):
    habits_data = get_habits_by_user(user_id)
    habits_by_periodicity = [habit for habit in habits_data if habit[4] == periodicity]
    print(f"Habits with periodicity '{periodicity}' for user {user_id}: {habits_by_periodicity}")
    return habits_by_periodicity


def get_longest_streak_all_habits(user_id):
    habits_data = get_habits_by_user(user_id)
    longest_streak = max(habits_data, key=lambda habit: habit[8])
    return longest_streak


def get_longest_streak_for_habit(habit_id):
    habit = get_habit_by_id(habit_id)
    if habit:
        longest_streak = habit.streak
        print(f"Longest streak for habit {habit_id}: {longest_streak}")
        return longest_streak
    else:
        print(f"No habit found with ID {habit_id}.")
        return 0


def get_completion_rate(habit_id):
    success_count = count_success_by_habit(habit_id)
    total = count_success_by_habit(habit_id) + count_unsuccessful_by_habit(habit_id)
    completion_rate = (success_count / total) * 100 if total > 0 else 0
    print(f"Completion rate for habit {habit_id}: {completion_rate}%")
    return completion_rate


def analyze_logs(habit_id):
    logs_data = get_logs_by_habit(habit_id)
    success_logs = count_success(habit_id)
    failure_logs = count_failure(habit_id)
    completed_habits = count_success_by_habit(habit_id)
    failure_habits = count_unsuccessful_by_habit(habit_id)

    # Ensure notes are distinct
    unique_notes = set()
    for log in logs_data:
        unique_notes.add(log[4])

    analysis = {
        "total_logs": len(logs_data),
        "success_logs": success_logs,
        "failure_logs": failure_logs,
        "completed_habits": completed_habits,
        "failure_habits": failure_habits,
        "notes": list(unique_notes)
    }

    print(f"Log analysis for habit {habit_id}: {analysis}")
    return analysis
