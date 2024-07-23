import unittest
from datetime import datetime, timedelta

from storage.db_manager import clear_habit_table, clear_user_table, clear_log_table
from storage.ex_data import setup_tables, create_example_user, create_example_habits
from app.habit import Habit


class TestHabit(unittest.TestCase):

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

    def test_create_habit(self):
        """Test creating a new habit."""
        habit = Habit.create(self.user.user_id, "Test Habit", "Test Description", "daily", 7)
        self.assertIsInstance(habit, Habit)
        self.assertEqual(habit.name, "Test Habit")
        self.assertEqual(habit.description, "Test Description")
        self.assertEqual(habit.periodicity, "daily")
        self.assertEqual(habit.duration, 7)

    def test_get_all_by_user(self):
        """Test retrieving all habits for a user."""
        habits = Habit.get_all_by_user(self.user.user_id)
        self.assertEqual(len(habits), 7)  # Based on the 7 example habits + created in test

    def test_update_habit(self):
        """Test updating a habit."""
        habit = self.habits[0]
        habit.update(name="Updated Habit", description="Updated Description", periodicity="weekly", duration=4)
        self.assertEqual(habit.name, "Updated Habit")
        self.assertEqual(habit.description, "Updated Description")
        self.assertEqual(habit.periodicity, "weekly")
        self.assertEqual(habit.duration, 4)

    def test_delete_habit(self):
        """Test deleting a habit."""
        habit = self.habits[1]
        habit_id = habit.habit_id
        habit.delete()
        # After deletion, habit should not be retrievable
        habits = Habit.get_all_by_user(self.user.user_id)
        self.assertNotIn(habit, habits)

    def test_add_log_entry(self):
        """Test adding a log entry to a habit."""
        habit = self.habits[2]
        log_id = habit.add_log_entry(success=1, note="Test log entry")
        self.assertIsNotNone(log_id)

    def test_can_mark_complete(self):
        """Test if a habit can be marked as complete."""
        habit = Habit.create(self.user.user_id, "Test Habit", "Test Description", "daily", 2)
        can_mark = habit.can_mark_complete()
        self.assertTrue(can_mark)

    def test_update_status(self):
        """Test updating the status of a habit."""
        habit = self.habits[4]
        habit.update_status()
        # Check if the status update was successful
        last_log = habit.add_log_entry(success=1, note="Test status update log")
        self.assertIsNotNone(last_log)

    def test_deactivate_habit_due(self):
        """Test deactivating a habit."""
        habit = Habit.create(self.user.user_id, "Test Habit", "Test Description", "daily", 2, 0,
                             datetime.now() - timedelta(days=3))
        habit.deactivate()
        self.assertEqual(habit.active, 0)
        print("Test passed: Habit deactivated due to deadline exceedance.")

    def test_calculate_streak(self):
        """Test calculating the streak of a habit."""
        habit = self.habits[4]
        streak = habit.calculate_streak(habit.habit_id)
        self.assertEqual(streak, habit.streak)


if __name__ == "__main__":
    unittest.main()
