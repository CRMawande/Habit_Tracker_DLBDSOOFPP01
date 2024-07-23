import hashlib
from datetime import datetime

from storage.db_manager import create_user, get_user_by_username, update_user, delete_user, update_last_login


class User:
    def __init__(self, user_id, username, password, created_at, last_login=None):
        # Initialize a User instance
        self.user_id = user_id
        self.username = username
        self.password = password
        self.created_at = created_at
        self.last_login = datetime.now() if last_login else None  # Set last_login to now if not provided

    @staticmethod
    def create(username, password, created_at):
        # Create a new user, hash the password, and store in the database
        hashed_password = User._hash_password(password)  # Hash the password
        user_id = create_user(username, hashed_password, created_at)  # Store user and get user_id
        print(f"User created: {username}")
        return User(user_id, username, hashed_password, created_at)  # Return a User instance

    @staticmethod
    def get_by_username(username):
        # Retrieve a user from the database by username
        user_data = get_user_by_username(username)  # Fetch user data from database
        if user_data:
            print(f"User retrieved: {username}")
            return User(*user_data)  # Create and return User instance from data
        print(f"User not found: {username}")
        return None  # Return None if user not found

    def update(self, username=None, password=None):
        # Update user's details in the database
        if username:
            self.username = username  # Update username if provided
        if password:
            self.password = User._hash_password(password)  # Hash and update password if provided
        update_user(self.user_id, username, self.password)  # Update user in database
        print(f"User updated: {self.username}")

    def delete(self):
        # Delete the user from the database
        delete_user(self.user_id)  # Remove user from database
        print(f"User deleted: {self.username}")

    def update_last_login(self):
        # Update the last login timestamp for the user
        update_last_login(self.username)  # Update last login timestamp in the database
        self.last_login = datetime.now()  # Set last_login to now
        print(f"Last login updated for user: {self.username}")

    @staticmethod
    def _hash_password(password):
        # Hash a password using SHA-256
        return hashlib.sha256(password.encode('utf-8')).hexdigest()  # Return hashed password

    def check_password(self, password):
        # Check if provided password matches the stored hashed password
        return self.password == self._hash_password(password)  # Return True if passwords match, otherwise False

    def reset_password(self, new_password):
        # Reset the user's password and update it in the database
        self.password = self._hash_password(new_password)  # Hash and set new password
        update_user(self.user_id, self.username, self.password)  # Update user in database
        print(f"Password updated successfully for user: {self.username}")
