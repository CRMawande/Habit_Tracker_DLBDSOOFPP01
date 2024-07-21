import unittest
from datetime import datetime
from storage.db_manager import (
    create_tables, create_user, get_user_by_username, update_last_login,
    update_user, delete_user, create_habit, get_habits_by_user, get_habit_by_id,
    update_habit, delete_habit, add_log_entry, get_logs_by_habit,
    clear_user_table, clear_habit_table, clear_log_table, count_success, count_failure,
    count_success_by_habit, count_unsuccessful_by_habit, count_consecutive_incomplete, get_last_log_entry
)


class TestDBManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the database tables before all tests."""
        create_tables()

    @classmethod
    def tearDownClass(cls):
        """Clear the database tables after all tests."""
        clear_user_table()
        clear_habit_table()
        clear_log_table()

    def setUp(self):
        """Set up test data before each test."""
        self.user_id = create_user("testuser", "testpassword", datetime.now())
        self.habit_id = create_habit(
            self.user_id, "test habit", "description", "daily", 30, 1, datetime.now(), 0, datetime.now()
        )

    def tearDown(self):
        """Clear the test data after each test."""
        clear_log_table()
        clear_habit_table()
        clear_user_table()

    def test_create_user(self):
        """Test creating a new user."""
        user_id = create_user("newuser", "newpassword", datetime.now())
        user = get_user_by_username("newuser")
        self.assertIsNotNone(user)
        self.assertEqual(user[0], user_id)

    def test_get_user_by_username(self):
        """Test retrieving a user by username."""
        user = get_user_by_username("testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "testuser")

    def test_update_last_login(self):
        """Test updating the last login timestamp."""
        update_last_login("testuser")
        user = get_user_by_username("testuser")
        self.assertIsNotNone(user)
        self.assertIsNotNone(user[4])  # last_login should be updated

    def test_update_user(self):
        """Test updating user details."""
        update_user(self.user_id, username="updateduser", password="newpassword")
        user = get_user_by_username("updateduser")
        self.assertIsNotNone(user)
        self.assertTrue(user[2] == "newpassword")  # Check password is updated

    def test_delete_user(self):
        """Test deleting a user."""
        delete_user(self.user_id)
        user = get_user_by_username("testuser")
        self.assertIsNone(user)

    def test_create_habit(self):
        """Test creating a new habit."""
        habit_id = create_habit(
            self.user_id, "new habit", "description", "weekly", 60, 1, datetime.now(), 0, datetime.now()
        )
        habit = get_habit_by_id(habit_id)
        self.assertIsNotNone(habit)
        self.assertEqual(habit.habit_id, habit_id)

    def test_get_habits_by_user(self):
        """Test retrieving habits by user ID."""
        habits = get_habits_by_user(self.user_id)
        self.assertGreater(len(habits), 0)

    def test_get_habit_by_id(self):
        """Test retrieving a habit by ID."""
        habit = get_habit_by_id(self.habit_id)
        self.assertIsNotNone(habit)
        self.assertEqual(habit.habit_id, self.habit_id)

    def test_update_habit(self):
        """Test updating habit details."""
        update_habit(self.habit_id, name="updated habit", description="updated description")
        habit = get_habit_by_id(self.habit_id)
        self.assertEqual(habit.name, "updated habit")
        self.assertEqual(habit.description, "updated description")

    def test_delete_habit(self):
        """Test deleting a habit."""
        delete_habit(self.habit_id)
        habit = get_habit_by_id(self.habit_id)
        self.assertIsNone(habit)

    def test_add_log_entry(self):
        """Test adding a log entry."""
        log_id = add_log_entry(self.habit_id, 1, "Completed", datetime.now())
        self.assertIsNotNone(log_id)

    def test_get_logs_by_habit(self):
        """Test retrieving logs by habit ID."""
        add_log_entry(self.habit_id, 1, "Completed", datetime.now())
        logs = get_logs_by_habit(self.habit_id)
        self.assertGreater(len(logs), 0)

    def test_get_last_log_entry(self):
        """Test retrieving the last log entry for a habit."""
        # Add multiple log entries
        add_log_entry(self.habit_id, 1, "Habit completed successfully on time", datetime.now())
        add_log_entry(self.habit_id, 0, "Habit marked as incomplete", datetime.now())

        last_log = get_last_log_entry(self.habit_id)
        self.assertIsNotNone(last_log)
        self.assertEqual(last_log['note'], 'Habit marked as incomplete')  # As it was added last
        self.assertIsInstance(last_log['log_time'], str)  # Ensure log_time is returned as a string

    def test_count_success(self):
        """Test counting successful logs."""
        add_log_entry(self.habit_id, 1, "Success Logs", datetime.now())
        count = count_success(self.habit_id)
        self.assertGreater(count, 0)

    def test_count_failure(self):
        """Test counting failed logs."""
        add_log_entry(self.habit_id, 0, "Failure Logs", datetime.now())
        count = count_failure(self.habit_id)
        self.assertGreater(count, 0)

    def test_count_success_by_habit(self):
        """Test counting successful logs by note."""
        add_log_entry(self.habit_id, 1, "Habit completed successfully on time", datetime.now())
        count = count_success_by_habit(self.habit_id)
        self.assertGreater(count, 0)

    def test_count_unsuccessful_by_habit(self):
        """Test counting unsuccessful logs by note."""
        add_log_entry(self.habit_id, 0, "Habit marked as incomplete", datetime.now())
        count = count_unsuccessful_by_habit(self.habit_id)
        self.assertGreater(count, 0)

    def test_count_consecutive_incomplete(self):
        """Test counting consecutive incomplete logs."""
        add_log_entry(self.habit_id, 0, "Habit marked as incomplete", datetime.now())
        count = count_consecutive_incomplete(self.habit_id)
        self.assertGreater(count, 0)


if __name__ == '__main__':
    unittest.main()
