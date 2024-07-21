import unittest
from datetime import datetime
from storage.ex_data import setup_tables, create_example_user
from storage.db_manager import clear_user_table
from app.user import User


class TestUser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test database and create example user."""
        setup_tables()
        cls.example_user = create_example_user()

    @classmethod
    def tearDownClass(cls):
        """Clear user table after tests."""
        clear_user_table()

    def setUp(self):
        """Set up test users before each test."""
        self.test_user = User.create("User1", "testpassword", datetime(2024, 6, 19, 15, 30, 0, 123456))
        self.updated_user = User.create("User2", "updatedpassword", datetime(2024, 6, 19, 15, 30, 0, 123456))

    def tearDown(self):
        """Delete test users after each test."""
        if User.get_by_username("User1"):
            User.get_by_username("User1").delete()
        if User.get_by_username("User2"):
            User.get_by_username("User2").delete()
        if User.get_by_username("User3"):
            User.get_by_username("User3").delete()

    def test_create_user(self):
        """Test creating a new user."""
        username = "User4"
        password = "testpassword"
        created_at = datetime(2024, 6, 19, 15, 30, 0, 123456)
        user = User.create(username, password, created_at)
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))
        user.delete()  # Clean up after test

    def test_get_user_by_username(self):
        """Test retrieving a user by username."""
        user = User.get_by_username("User1")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "User1")

    def test_update_user(self):
        """Test updating user details."""
        # Ensure the updated user does not exist before the test
        existing_user = User.get_by_username("User2")
        if existing_user:
            existing_user.delete()

        user = User.get_by_username("User1")
        new_username = "User2"
        new_password = "updatedpassword"
        user.update(username=new_username, password=new_password)
        self.assertEqual(user.username, new_username)
        self.assertTrue(user.check_password(new_password))

    def test_delete_user(self):
        """Test deleting a user."""
        # Ensure the user exists before deletion
        username = "User3"
        password = "todeletepassword"
        created_at = datetime(2024, 6, 19, 15, 30, 0, 123456)
        user = User.create(username, password, created_at)

        # Retrieve the user by username
        user_to_delete = User.get_by_username(username)
        self.assertIsNotNone(user_to_delete)

        # Delete the user
        user_to_delete.delete()

        # Verify the user is deleted
        deleted_user = User.get_by_username(username)
        self.assertIsNone(deleted_user)

    def test_update_last_login(self):
        """Test updating the last login timestamp."""
        user = self.test_user
        user.update_last_login()
        self.assertIsNotNone(user.last_login)

    def test_reset_password(self):
        """Test resetting the user's password."""
        user = User.get_by_username("User1")
        new_password = "newpassword123"
        user.reset_password(new_password)
        self.assertTrue(user.check_password(new_password))


if __name__ == "__main__":
    unittest.main()
