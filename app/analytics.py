import logging
from storage.db_manager import (
    get_habits_by_user, get_logs_by_habit, count_success_by_habit, count_unsuccessful_by_habit,
    count_success, count_failure, get_habit_by_id
)

# Setup logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_active_habits(user_id):
    # Retrieve all habits for the specified user and filter to return only active habits
    habits_data = get_habits_by_user(user_id)  # Fetch habits from database
    active_habits = [habit for habit in habits_data if habit['active'] == 1]  # Filter active habits

    if not active_habits:
        print(f"No active habits found for user {user_id}.")  # Print message if no active habits

    return active_habits


def get_habits_by_periodicity(user_id, periodicity):
    # Retrieve all habits for the specified user and filter by periodicity
    habits_data = get_habits_by_user(user_id)  # Fetch habits from database
    habits_by_periodicity = [habit for habit in habits_data if habit[4] == periodicity]  # Filter by periodicity
    print(f"Habits with periodicity '{periodicity}' for user {user_id}: {habits_by_periodicity}")
    return habits_by_periodicity


def get_longest_streak_all_habits(user_id):
    # Retrieve all habits for the specified user and find the habit with the longest streak
    habits_data = get_habits_by_user(user_id)  # Fetch habits from database
    longest_streak = max(habits_data, key=lambda habit: habit[8])  # Find habit with maximum streak
    return longest_streak


def get_longest_streak_for_habit(habit_id):
    # Retrieve a specific habit by ID and return its longest streak
    habit = get_habit_by_id(habit_id)  # Fetch habit from database
    if habit:
        longest_streak = habit.streak  # Get streak for the habit
        print(f"Longest streak for habit {habit_id}: {longest_streak}")
        return longest_streak
    else:
        print(f"No habit found with ID {habit_id}.")  # Print message if habit not found
        return 0


def get_completion_rate(habit_id):
    # Calculate and return the completion rate for a specific habit
    success_count = count_success_by_habit(habit_id)  # Count successful logs for the habit
    total = count_success_by_habit(habit_id) + count_unsuccessful_by_habit(habit_id)  # Calculate total logs
    completion_rate = (success_count / total) * 100 if total > 0 else 0  # Calculate completion rate
    print(f"Completion rate for habit {habit_id}: {completion_rate}%")
    return completion_rate


def analyze_logs(habit_id):
    # Analyze logs for a specific habit and return various statistics
    logs_data = get_logs_by_habit(habit_id)  # Fetch logs from database
    success_logs = count_success(habit_id)  # Count successful logs
    failure_logs = count_failure(habit_id)  # Count failed logs
    completed_habits = count_success_by_habit(habit_id)  # Count completed habits
    failure_habits = count_unsuccessful_by_habit(habit_id)  # Count failed habits

    # Collect unique notes from the logs
    unique_notes = set()
    for log in logs_data:
        unique_notes.add(log[4])  # Add note to the set to ensure uniqueness

    # Create a summary of the log analysis
    analysis = {
        "total_logs": len(logs_data),  # Total number of logs
        "success_logs": success_logs,  # Number of successful logs
        "failure_logs": failure_logs,  # Number of failed logs
        "completed_habits": completed_habits,  # Number of completed habits
        "failure_habits": failure_habits,  # Number of failed habits
        "notes": list(unique_notes)  # List of unique notes
    }

    print(f"Log analysis for habit {habit_id}: {analysis}")
    return analysis
