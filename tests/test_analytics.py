import unittest
from app.analytics import (
    get_active_habits, get_habits_by_periodicity, get_longest_streak_all_habits,
    get_longest_streak_for_habit, get_completion_rate, analyze_logs
)
from storage.db_manager import clear_habit_table, clear_user_table, clear_log_table
from storage.ex_data import setup_tables, create_example_user, create_example_habits


class TestAnalytics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test database and create example user and habits."""
        setup_tables()
        cls.user = create_example_user()
        cls.habits = create_example_habits(cls.user.user_id)

    @classmethod
    def tearDownClass(cls):
        """Clear the habit and user tables after all tests."""
        clear_habit_table()
        clear_user_table()
        clear_log_table()

    def test_get_active_habits(self):
        """Test retrieving active habits for a user."""
        active_habits = get_active_habits(self.user.user_id)
        self.assertIsInstance(active_habits, list)
        self.assertGreater(len(active_habits), 0)
        print("Test passed: Retrieved active habits.")

    def test_get_habits_by_periodicity(self):
        """Test retrieving habits by periodicity for a user."""
        periodicity = "daily"
        habits = get_habits_by_periodicity(self.user.user_id, periodicity)
        self.assertIsInstance(habits, list)
        print(f"Test passed: Retrieved habits with periodicity '{periodicity}'.")

    def test_get_longest_streak_all_habits(self):
        """Test retrieving the longest streak for all habits of a user."""
        longest_streak_habit = get_longest_streak_all_habits(self.user.user_id)
        longest_streak_habit_dict = dict(longest_streak_habit)  # Convert sqlite3.Row to dict
        self.assertIsInstance(longest_streak_habit_dict, dict)
        self.assertIn('streak', longest_streak_habit_dict)
        print("Test passed: Retrieved longest streak for all habits.")

    def test_get_longest_streak_for_habit(self):
        """Test retrieving the longest streak for a specific habit."""
        habit_id = self.habits[0].habit_id
        longest_streak = get_longest_streak_for_habit(habit_id)
        self.assertIsInstance(longest_streak, int)
        self.assertGreaterEqual(longest_streak, 0)
        print(f"Test passed: Retrieved longest streak for habit {habit_id}.")

    def test_get_completion_rate(self):
        """Test calculating the completion rate for a specific habit."""
        habit_id = self.habits[0].habit_id
        completion_rate = get_completion_rate(habit_id)
        self.assertIsInstance(completion_rate, float)
        self.assertGreaterEqual(completion_rate, 0)
        self.assertLessEqual(completion_rate, 100)
        print(f"Test passed: Calculated completion rate for habit {habit_id}.")

    def test_analyze_logs(self):
        """Test analyzing logs for a specific habit."""
        habit_id = self.habits[0].habit_id
        analysis = analyze_logs(habit_id)
        self.assertIsInstance(analysis, dict)
        self.assertIn('total_logs', analysis)
        self.assertIn('success_logs', analysis)
        self.assertIn('failure_logs', analysis)
        print(f"Test passed: Analyzed logs for habit {habit_id}.")


if __name__ == "__main__":
    unittest.main()
